"""Query-expansion-with-multiple-queries demo for RAG retrieval.

Pipeline overview:
1. Embedding pipeline: PDF -> chunks -> embedding model -> stored in Chroma.
   This just builds the searchable index.
2. Retrieval with query expansion: this is part of RAG - specifically the
   "R" (Retrieval) step. It asks the LLM for several related questions,
   retrieves documents for the original query plus every related query, and
   de-duplicates the retrieved set.

Missing for full RAG: the "G" (Generation) step - feeding retrieved chunks
back into the LLM to synthesize a final answer. This script stops at
retrieval + visualizing the results.

Setup: local Ollama server (same setup as experiments/ai/01-llm-api)
    brew install ollama  ->  ollama serve  ->  ollama pull llama3.2
"""

import sys
from pathlib import Path
from typing import Any, NamedTuple

import chromadb
import httpx
import numpy as np
import ollama
import umap
from chromadb.api.types import PyEmbeddings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import ChatOllama
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from pypdf import PdfReader

import matplotlib.pyplot as plt

from helper_utils import project_embeddings, word_wrap

# Union of the embedding container types this module actually receives:
# chromadb's own (partly Optional) result types, plus plain numpy arrays.
EmbeddingsLike = chromadb.Embeddings | PyEmbeddings | np.ndarray

OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "llama3.2"
TIMEOUT_SECONDS: int = 60

# Resolved relative to this file (not the process cwd) so the script works
# regardless of how/where it's launched from (e.g. VS Code debugger defaults
# to the workspace root as cwd).
PDF_PATH: str = str(Path(__file__).resolve().parent / "data" / "microsoft-annual-report.pdf")
COLLECTION_NAME: str = "microsoft-collection"

CHARACTER_CHUNK_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " ", ""]
CHARACTER_CHUNK_SIZE: int = 1000
CHARACTER_CHUNK_OVERLAP: int = 0
TOKENS_PER_CHUNK: int = 256
TOKEN_CHUNK_OVERLAP: int = 0

# Sanity-check query used only to demonstrate that the collection answers
# queries before the multi-query flow runs; its result is not used further.
SAMPLE_QUERY: str = "What was the total revenue for the year?"
SAMPLE_QUERY_RESULT_COUNT: int = 5

ORIGINAL_QUERY: str = "What details can you provide about the factors that led to revenue growth?"
JOINT_QUERY_RESULT_COUNT: int = 5

DATASET_POINT_SIZE: int = 10
RETRIEVED_POINT_SIZE: int = 100
QUERY_POINT_SIZE: int = 150
DATASET_POINT_COLOR: str = "gray"
RETRIEVED_POINT_COLOR: str = "g"
ORIGINAL_QUERY_POINT_COLOR: str = "r"
JOINT_QUERY_POINT_COLOR: str = "orange"


class ProjectedMultiQueryEmbeddings(NamedTuple):
    """2D UMAP projections needed to draw one multi-query retrieval plot."""

    dataset: np.ndarray
    retrieved_documents: np.ndarray
    original_query: np.ndarray
    joint_queries: np.ndarray


def load_pdf_page_texts(pdf_path: str) -> list[str]:
    """Extracts non-empty text from every page of a PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        The stripped text of each page, excluding pages with no text.
    """
    reader: PdfReader = PdfReader(pdf_path)
    page_texts: list[str] = [page.extract_text().strip() for page in reader.pages]
    return [page_text for page_text in page_texts if page_text]


def split_into_character_chunks(page_texts: list[str]) -> list[str]:
    """Splits page texts into character-based chunks.

    Splits by paragraph, then by sentence, and finally by raw characters.

    Args:
        page_texts: Text extracted from each PDF page.

    Returns:
        The text split into character-based chunks.
    """
    character_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
        separators=CHARACTER_CHUNK_SEPARATORS,
        chunk_size=CHARACTER_CHUNK_SIZE,
        chunk_overlap=CHARACTER_CHUNK_OVERLAP,
    )
    return character_splitter.split_text("\n\n".join(page_texts))


def split_into_token_chunks(character_chunks: list[str]) -> list[str]:
    """Splits character-based chunks into chunks within the LLM's token limit.

    Args:
        character_chunks: Text already split into character-based chunks.

    Returns:
        The text re-split so no chunk exceeds `TOKENS_PER_CHUNK` tokens.
    """
    token_splitter: SentenceTransformersTokenTextSplitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=TOKEN_CHUNK_OVERLAP, tokens_per_chunk=TOKENS_PER_CHUNK
    )
    token_chunks: list[str] = []
    for character_chunk in character_chunks:
        token_chunks += token_splitter.split_text(character_chunk)
    return token_chunks


def build_chroma_collection(
    token_chunks: list[str], collection_name: str
) -> tuple[chromadb.Collection, SentenceTransformerEmbeddingFunction]:
    """Embeds chunks and stores them in a new in-memory Chroma collection.

    Args:
        token_chunks: Token-limited text chunks to embed and store.
        collection_name: Name to give the Chroma collection.

    Returns:
        The populated collection and the embedding function used to build it
        (the same function must be reused to embed later queries).
    """
    embedding_function: SentenceTransformerEmbeddingFunction = (
        SentenceTransformerEmbeddingFunction()
    )
    chroma_client: chromadb.ClientAPI = chromadb.Client()
    collection: chromadb.Collection = chroma_client.create_collection(
        collection_name, embedding_function=embedding_function
    )
    chunk_ids: list[str] = [str(index) for index in range(len(token_chunks))]
    collection.add(ids=chunk_ids, documents=token_chunks)
    return collection, embedding_function


def run_sample_query_against_collection(
    collection: chromadb.Collection, query_text: str, n_results: int
) -> chromadb.QueryResult:
    """Runs a smoke-test query to confirm the collection answers queries.

    The result is intentionally not inspected further; this exists to
    demonstrate the collection works before the multi-query flow runs.

    Args:
        collection: The Chroma collection to query.
        query_text: The query text.
        n_results: How many results to request.

    Returns:
        The raw Chroma query result.
    """
    return collection.query(query_texts=[query_text], n_results=n_results)


def generate_multi_query(query: str, model: str = OLLAMA_MODEL) -> list[str]:
    """
    Generate multiple related queries based on the original query.

    Args:
        query (str): The original query to expand.
        model (str): The Ollama model name; it must already be pulled.

    Returns:
        list[str]: A list of related queries.
    """
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a knowledgeable financial research assistant. "
                "Your users are inquiring about an annual report. "
                "For the given question, propose up to five related questions to "
                "assist them in finding the information they need. "
                "Provide concise, single-topic questions (without compounding "
                "sentences) that cover various aspects of the topic. "
                "Ensure each question is complete and directly related to the "
                "original inquiry. "
                "List each question on a separate line without numbering.",
            ),
            ("human", "{query}"),
        ]
    )
    llm: ChatOllama = ChatOllama(
        model=model,
        base_url=OLLAMA_BASE_URL,
        client_kwargs={"timeout": TIMEOUT_SECONDS},
    )
    # LCEL chain: fill the prompt -> call the model -> pull out the reply text
    chain: RunnableSerializable[dict, str] = prompt | llm | StrOutputParser()
    content: str = chain.invoke({"query": query})
    # Drop blank lines the model sometimes leaves between questions
    return [line.strip() for line in content.split("\n") if line.strip()]


def generate_multi_query_or_exit(query: str) -> list[str]:
    """Generates related queries, exiting with a clear message on failure.

    Args:
        query: The original query to expand.

    Returns:
        A list of related queries.
    """
    try:
        return generate_multi_query(query)
    except (ConnectionError, httpx.ConnectError):
        sys.exit(
            f"Error: could not connect to Ollama at {OLLAMA_BASE_URL}. Is `ollama serve` running?"
        )
    except httpx.TimeoutException:
        sys.exit(f"Error: Ollama did not respond within {TIMEOUT_SECONDS}s.")
    except ollama.ResponseError as exc:
        # e.g. 404 when the model has not been pulled: `ollama pull llama3.2`
        sys.exit(f"Error: Ollama returned {exc.status_code}: {exc.error}")


def print_generated_queries(aug_queries: list[str]) -> None:
    """Prints each LLM-generated related query on its own line.

    Args:
        aug_queries: The related queries generated from the original query.
    """
    for aug_query in aug_queries:
        print("\n", aug_query)


def build_joint_query(original_query: str, aug_queries: list[str]) -> list[str]:
    """Builds the multi-query list sent to Chroma.

    The original query is wrapped in a list before concatenation because
    Chroma can handle multiple queries at once.

    Args:
        original_query: The user's original question.
        aug_queries: The LLM-generated related questions.

    Returns:
        The original query followed by every related query.
    """
    return [original_query] + aug_queries


def retrieve_documents_for_joint_query(
    collection: chromadb.Collection, joint_query: list[str], n_results: int
) -> chromadb.QueryResult:
    """Retrieves documents and embeddings for every query in `joint_query`.

    Args:
        collection: The Chroma collection to query.
        joint_query: The original query plus every related query.
        n_results: How many results to request per query.

    Returns:
        The raw Chroma query result, including documents and embeddings.
    """
    return collection.query(
        query_texts=joint_query, n_results=n_results, include=["documents", "embeddings"]
    )


def deduplicate_documents(retrieved_documents_per_query: list[list[str]]) -> set[str]:
    """Collects the unique documents retrieved across all queries.

    Args:
        retrieved_documents_per_query: One documents list per query.

    Returns:
        Every distinct document text retrieved for any query.
    """
    unique_documents: set[str] = set()
    for documents in retrieved_documents_per_query:
        for document in documents:
            unique_documents.add(document)
    return unique_documents


def print_retrieved_documents_per_query(
    joint_query: list[str], retrieved_documents_per_query: list[list[str]]
) -> None:
    """Prints the documents retrieved for each query in `joint_query`.

    Args:
        joint_query: The original query plus every related query.
        retrieved_documents_per_query: One documents list per query, in the
            same order as `joint_query`.
    """
    for query_text, documents in zip(joint_query, retrieved_documents_per_query):
        print(f"Query: {query_text}")
        print("")
        print("Results:")
        for document in documents:
            print(word_wrap(document))
            print("")
        print("-" * 100)


def get_dataset_embeddings(collection: chromadb.Collection) -> EmbeddingsLike:
    """Fetches every embedding already stored in the collection.

    Args:
        collection: The Chroma collection to read from.

    Returns:
        The stored embeddings.
    """
    return collection.get(include=["embeddings"])["embeddings"]


def fit_umap_transform(dataset_embeddings: EmbeddingsLike) -> umap.UMAP:
    """Fits a 2D UMAP transform over the dataset's embeddings.

    Args:
        dataset_embeddings: Embeddings for the whole stored collection.

    Returns:
        The fitted UMAP transform, reusable to project further embeddings
        into the same 2D space.
    """
    return umap.UMAP(random_state=0, transform_seed=0).fit(dataset_embeddings)


def flatten_per_query_embeddings(retrieved_embeddings_per_query: Any) -> list[Any]:
    """Flattens per-query embedding lists into a single list for projection.

    Args:
        retrieved_embeddings_per_query: One embeddings list per query, as
            returned by Chroma for a multi-query query.

    Returns:
        All embeddings in one flat list. `Any` because flattening the nested
        union type loses the per-query structure it encoded.
    """
    return [
        embedding
        for query_embeddings in retrieved_embeddings_per_query
        for embedding in query_embeddings
    ]


def project_query_and_retrieval_embeddings(
    dataset_embeddings: EmbeddingsLike,
    flattened_retrieved_embeddings: list[Any],
    original_query_embedding: list[np.ndarray],
    joint_query_embeddings: list[np.ndarray],
    umap_transform: umap.UMAP,
) -> ProjectedMultiQueryEmbeddings:
    """Projects every embedding needed for the multi-query plot into 2D.

    Args:
        dataset_embeddings: Embeddings for the whole stored collection.
        flattened_retrieved_embeddings: Embeddings of every document
            retrieved across all queries, flattened into one list.
        original_query_embedding: Embedding of the original, un-augmented query.
        joint_query_embeddings: Embeddings of every query in `joint_query`
            (the original query plus every related query).
        umap_transform: UMAP transform fitted on `dataset_embeddings`.

    Returns:
        The 2D-projected embeddings, grouped for plotting.
    """
    return ProjectedMultiQueryEmbeddings(
        dataset=project_embeddings(dataset_embeddings, umap_transform),
        retrieved_documents=project_embeddings(flattened_retrieved_embeddings, umap_transform),
        original_query=project_embeddings(original_query_embedding, umap_transform),
        joint_queries=project_embeddings(joint_query_embeddings, umap_transform),
    )


def plot_multi_query_retrieval(projected: ProjectedMultiQueryEmbeddings, title: str) -> None:
    """Draws the dataset, retrieved documents, and all queries in 2D.

    UMAP produces the numbers; this function draws the picture.

    Args:
        projected: The 2D-projected embeddings to plot.
        title: The plot title.
    """
    plt.figure()
    plt.scatter(
        projected.dataset[:, 0],
        projected.dataset[:, 1],
        s=DATASET_POINT_SIZE,
        color=DATASET_POINT_COLOR,
    )
    plt.scatter(
        projected.joint_queries[:, 0],
        projected.joint_queries[:, 1],
        s=QUERY_POINT_SIZE,
        marker="X",
        color=JOINT_QUERY_POINT_COLOR,
    )
    plt.scatter(
        projected.retrieved_documents[:, 0],
        projected.retrieved_documents[:, 1],
        s=RETRIEVED_POINT_SIZE,
        facecolors="none",
        edgecolors=RETRIEVED_POINT_COLOR,
    )
    plt.scatter(
        projected.original_query[:, 0],
        projected.original_query[:, 1],
        s=QUERY_POINT_SIZE,
        marker="X",
        color=ORIGINAL_QUERY_POINT_COLOR,
    )
    plt.gca().set_aspect("equal", "datalim")
    plt.title(title)
    plt.axis("off")
    plt.show()


def main() -> None:
    """Runs the multi-query expansion demo end to end."""
    page_texts: list[str] = load_pdf_page_texts(PDF_PATH)
    character_chunks: list[str] = split_into_character_chunks(page_texts)
    token_chunks: list[str] = split_into_token_chunks(character_chunks)
    collection, embedding_function = build_chroma_collection(token_chunks, COLLECTION_NAME)
    run_sample_query_against_collection(collection, SAMPLE_QUERY, SAMPLE_QUERY_RESULT_COUNT)

    aug_queries: list[str] = generate_multi_query_or_exit(ORIGINAL_QUERY)
    print_generated_queries(aug_queries)
    joint_query: list[str] = build_joint_query(ORIGINAL_QUERY, aug_queries)

    joint_results: chromadb.QueryResult = retrieve_documents_for_joint_query(
        collection, joint_query, JOINT_QUERY_RESULT_COUNT
    )
    retrieved_documents_per_query: list[list[str]] = joint_results["documents"]
    # Mirrors the "de-duplicates the union" step documented in README.md; the
    # result isn't consumed further in this script.
    deduplicate_documents(retrieved_documents_per_query)
    print_retrieved_documents_per_query(joint_query, retrieved_documents_per_query)

    dataset_embeddings: EmbeddingsLike = get_dataset_embeddings(collection)
    umap_transform: umap.UMAP = fit_umap_transform(dataset_embeddings)
    original_query_embedding: list[np.ndarray] = embedding_function([ORIGINAL_QUERY])
    joint_query_embeddings: list[np.ndarray] = embedding_function(joint_query)
    flattened_retrieved_embeddings: list[Any] = flatten_per_query_embeddings(
        joint_results["embeddings"]
    )

    projected: ProjectedMultiQueryEmbeddings = project_query_and_retrieval_embeddings(
        dataset_embeddings,
        flattened_retrieved_embeddings,
        original_query_embedding,
        joint_query_embeddings,
        umap_transform,
    )
    plot_multi_query_retrieval(projected, title=ORIGINAL_QUERY)


if __name__ == "__main__":
    main()
