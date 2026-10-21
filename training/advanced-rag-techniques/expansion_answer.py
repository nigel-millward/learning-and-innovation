"""Hypothetical Document Embeddings (HyDE) query-expansion demo.

Pipeline overview:
1. Embedding pipeline: PDF -> chunks -> embedding model -> stored in Chroma.
   This just builds the searchable index.
2. Retrieval with query expansion: this is part of RAG - specifically the
   "R" (Retrieval) step, enhanced with HyDE. It takes a question, hallucinates
   an answer, embeds it, and queries Chroma to get real relevant chunks back.

Missing for full RAG: the "G" (Generation) step - feeding retrieved chunks
back into the LLM to synthesize a final answer. This script stops at
retrieval + visualizing the results.

Setup: local Ollama server (same setup as experiments/ai/01-llm-api)
    brew install ollama  ->  ollama serve  ->  ollama pull llama3.2
"""

import sys
from typing import NamedTuple

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

PDF_PATH: str = "data/microsoft-annual-report.pdf"
COLLECTION_NAME: str = "microsoft-collection"

CHARACTER_CHUNK_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " ", ""]
CHARACTER_CHUNK_SIZE: int = 1000
CHARACTER_CHUNK_OVERLAP: int = 0
TOKENS_PER_CHUNK: int = 256
TOKEN_CHUNK_OVERLAP: int = 0

# Sanity-check query used only to demonstrate that the collection answers
# queries before the HyDE flow runs; its result is not used further.
SAMPLE_QUERY: str = "What was the total revenue for the year?"
SAMPLE_QUERY_RESULT_COUNT: int = 5

ORIGINAL_QUERY: str = (
    "What was the total profit for the year, and how does it compare to the previous year?"
)
HYDE_RESULT_COUNT: int = 5

DATASET_POINT_SIZE: int = 10
RETRIEVED_POINT_SIZE: int = 100
QUERY_POINT_SIZE: int = 150
DATASET_POINT_COLOR: str = "gray"
RETRIEVED_POINT_COLOR: str = "g"
ORIGINAL_QUERY_POINT_COLOR: str = "r"
AUGMENTED_QUERY_POINT_COLOR: str = "orange"


class ProjectedHydeEmbeddings(NamedTuple):
    """2D UMAP projections needed to draw one HyDE retrieval plot."""

    dataset: np.ndarray
    retrieved_documents: np.ndarray
    original_query: np.ndarray
    augmented_query: np.ndarray


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
    demonstrate the collection works before the HyDE flow runs.

    Args:
        collection: The Chroma collection to query.
        query_text: The query text.
        n_results: How many results to request.

    Returns:
        The raw Chroma query result.
    """
    return collection.query(query_texts=[query_text], n_results=n_results)


def augment_query_generated(query: str, model: str = OLLAMA_MODEL) -> str:
    """Ask the local LLM for a hypothetical answer to `query`.

    Args:
        query: The user's question.
        model: The Ollama model name; it must already be pulled.

    Returns:
        The generated answer text.
    """
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful expert financial research assistant. "
                "Provide an example answer to the given question, that might be "
                "found in a document like an annual report.",
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
    return chain.invoke({"query": query})


def generate_hypothetical_answer_or_exit(query: str) -> str:
    """Generates a hypothetical answer, exiting with a clear message on failure.

    Args:
        query: The user's question.

    Returns:
        The generated answer text.
    """
    try:
        return augment_query_generated(query)
    except (ConnectionError, httpx.ConnectError):
        sys.exit(
            f"Error: could not connect to Ollama at {OLLAMA_BASE_URL}. Is `ollama serve` running?"
        )
    except httpx.TimeoutException:
        sys.exit(f"Error: Ollama did not respond within {TIMEOUT_SECONDS}s.")
    except ollama.ResponseError as exc:
        # e.g. 404 when the model has not been pulled: `ollama pull llama3.2`
        sys.exit(f"Error: Ollama returned {exc.status_code}: {exc.error}")


def build_hyde_query(original_query: str, hypothetical_answer: str) -> str:
    """Joins the original query with its generated hypothetical answer.

    Args:
        original_query: The user's original question.
        hypothetical_answer: The LLM's hallucinated answer to that question.

    Returns:
        The combined text used as the HyDE retrieval query.
    """
    return f"{original_query} {hypothetical_answer}"


def retrieve_documents_for_hyde_query(
    collection: chromadb.Collection, hyde_query: str, n_results: int
) -> chromadb.QueryResult:
    """Retrieves documents and embeddings for the combined HyDE query.

    Args:
        collection: The Chroma collection to query.
        hyde_query: The original query joined with its hypothetical answer.
        n_results: How many results to request.

    Returns:
        The raw Chroma query result, including documents and embeddings.
    """
    return collection.query(
        query_texts=hyde_query, n_results=n_results, include=["documents", "embeddings"]
    )


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


def project_query_and_retrieval_embeddings(
    dataset_embeddings: EmbeddingsLike,
    retrieved_embeddings: EmbeddingsLike,
    original_query_embedding: list[np.ndarray],
    augmented_query_embedding: list[np.ndarray],
    umap_transform: umap.UMAP,
) -> ProjectedHydeEmbeddings:
    """Projects every embedding needed for the HyDE plot into the same 2D space.

    Args:
        dataset_embeddings: Embeddings for the whole stored collection.
        retrieved_embeddings: Embeddings of the documents retrieved for the
            HyDE query.
        original_query_embedding: Embedding of the original, un-augmented query.
        augmented_query_embedding: Embedding of the joint HyDE query.
        umap_transform: UMAP transform fitted on `dataset_embeddings`.

    Returns:
        The 2D-projected embeddings, grouped for plotting.
    """
    return ProjectedHydeEmbeddings(
        dataset=project_embeddings(dataset_embeddings, umap_transform),
        retrieved_documents=project_embeddings(retrieved_embeddings, umap_transform),
        original_query=project_embeddings(original_query_embedding, umap_transform),
        augmented_query=project_embeddings(augmented_query_embedding, umap_transform),
    )


def plot_hyde_retrieval(projected: ProjectedHydeEmbeddings, title: str) -> None:
    """Draws the dataset, retrieved documents, and both queries in 2D.

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
    plt.scatter(
        projected.augmented_query[:, 0],
        projected.augmented_query[:, 1],
        s=QUERY_POINT_SIZE,
        marker="X",
        color=AUGMENTED_QUERY_POINT_COLOR,
    )
    plt.gca().set_aspect("equal", "datalim")
    plt.title(title)
    plt.axis("off")
    plt.show()


def main() -> None:
    """Runs the HyDE query-expansion demo end to end."""
    page_texts: list[str] = load_pdf_page_texts(PDF_PATH)
    character_chunks: list[str] = split_into_character_chunks(page_texts)
    token_chunks: list[str] = split_into_token_chunks(character_chunks)
    collection, embedding_function = build_chroma_collection(token_chunks, COLLECTION_NAME)
    run_sample_query_against_collection(collection, SAMPLE_QUERY, SAMPLE_QUERY_RESULT_COUNT)

    hypothetical_answer: str = generate_hypothetical_answer_or_exit(ORIGINAL_QUERY)
    hyde_query: str = build_hyde_query(ORIGINAL_QUERY, hypothetical_answer)
    print(word_wrap(hyde_query))

    hyde_results: chromadb.QueryResult = retrieve_documents_for_hyde_query(
        collection, hyde_query, HYDE_RESULT_COUNT
    )
    retrieved_embeddings: EmbeddingsLike = hyde_results["embeddings"][0]

    dataset_embeddings: EmbeddingsLike = get_dataset_embeddings(collection)
    umap_transform: umap.UMAP = fit_umap_transform(dataset_embeddings)
    original_query_embedding: list[np.ndarray] = embedding_function([ORIGINAL_QUERY])
    augmented_query_embedding: list[np.ndarray] = embedding_function([hyde_query])

    projected: ProjectedHydeEmbeddings = project_query_and_retrieval_embeddings(
        dataset_embeddings,
        retrieved_embeddings,
        original_query_embedding,
        augmented_query_embedding,
        umap_transform,
    )
    plot_hyde_retrieval(projected, title=ORIGINAL_QUERY)


if __name__ == "__main__":
    main()
