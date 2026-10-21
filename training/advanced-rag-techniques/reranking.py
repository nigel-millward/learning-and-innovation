"""Cross-encoder re-ranking demo for RAG retrieval, with full generation.

Pipeline overview:
1. Embedding pipeline: PDF -> chunks -> embedding model -> stored in Chroma.
   This just builds the searchable index.
2. Scenario A - single-query re-ranking: retrieve Chroma's top 10 matches for
   one query, then re-score them with a cross-encoder and print both
   orderings side by side, to show how re-ranking changes the result order.
3. Scenario B - multi-query retrieval with re-ranking and generation: this is
   a full RAG pass. It retrieves documents for the original query plus
   several related queries, de-duplicates them, re-ranks the unique set with
   the cross-encoder, and feeds the top results to an OpenAI chat model to
   synthesize a final answer (the "G" step).

Setup: an `OPENAI_API_KEY` must be available, either in the environment or in
a local `.env` file (see python-dotenv).
"""

import os
from pathlib import Path

import numpy as np
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from pypdf import PdfReader
from sentence_transformers import CrossEncoder

import chromadb
from helper_utils import word_wrap

# Resolved relative to this file (not the process cwd) so the script works
# regardless of how/where it's launched from (e.g. VS Code debugger defaults
# to the workspace root as cwd).
PDF_PATH: str = str(Path(__file__).resolve().parent / "data" / "microsoft-annual-report.pdf")
COLLECTION_NAME: str = "microsoft-collect"

CHARACTER_CHUNK_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " ", ""]
CHARACTER_CHUNK_SIZE: int = 1000
CHARACTER_CHUNK_OVERLAP: int = 0
TOKENS_PER_CHUNK: int = 256
TOKEN_CHUNK_OVERLAP: int = 0

CROSS_ENCODER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

SINGLE_QUERY: str = "What has been the investment in research and development?"
SINGLE_QUERY_RESULT_COUNT: int = 10

ORIGINAL_QUERY: str = (
    "What were the most important factors that contributed to increases in revenue?"
)
GENERATED_QUERIES: list[str] = [
    "What were the major drivers of revenue growth?",
    "Were there any new product launches that contributed to the increase in revenue?",
    "Did any changes in pricing or promotions impact the revenue growth?",
    "What were the key market trends that facilitated the increase in revenue?",
    "Did any acquisitions or partnerships contribute to the revenue growth?",
]
MULTI_QUERY_RESULT_COUNT: int = 10
TOP_RERANKED_DOCUMENT_COUNT: int = 5

ANSWER_MODEL: str = "gpt-5.6-luna"
ANSWER_SYSTEM_PROMPT: str = (
    "You are a knowledgeable financial research assistant. "
    "Your users are inquiring about an annual report."
)


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


def build_chroma_collection(token_chunks: list[str], collection_name: str) -> chromadb.Collection:
    """Embeds chunks and stores them in a new in-memory Chroma collection.

    Args:
        token_chunks: Token-limited text chunks to embed and store.
        collection_name: Name to give the Chroma collection.

    Returns:
        The populated collection.
    """
    embedding_function: SentenceTransformerEmbeddingFunction = (
        SentenceTransformerEmbeddingFunction()
    )
    chroma_client: chromadb.ClientAPI = chromadb.Client()
    collection: chromadb.Collection = chroma_client.get_or_create_collection(
        collection_name, embedding_function=embedding_function
    )
    chunk_ids: list[str] = [str(index) for index in range(len(token_chunks))]
    collection.add(ids=chunk_ids, documents=token_chunks)
    return collection


def retrieve_documents_for_queries(
    collection: chromadb.Collection, query_texts: str | list[str], n_results: int
) -> chromadb.QueryResult:
    """Retrieves documents and embeddings for one or more queries.

    Args:
        collection: The Chroma collection to query.
        query_texts: A single query, or a list of queries to run together.
        n_results: How many results to request per query.

    Returns:
        The raw Chroma query result, including documents and embeddings.
    """
    return collection.query(
        query_texts=query_texts, n_results=n_results, include=["documents", "embeddings"]
    )


def print_retrieved_documents(documents: list[str]) -> None:
    """Prints each document, word-wrapped, separated by a blank line.

    Args:
        documents: The document texts to print.
    """
    for document in documents:
        print(word_wrap(document))
        print("")


def deduplicate_documents(documents_per_query: list[list[str]]) -> list[str]:
    """Flattens per-query document results into a de-duplicated list.

    Args:
        documents_per_query: The retrieved documents for each query, as
            returned by Chroma when querying with multiple query texts.

    Returns:
        Every distinct document across all queries. Order is not
        significant; results are re-ranked by the cross-encoder afterwards.
    """
    unique_documents: set[str] = set()
    for documents in documents_per_query:
        unique_documents.update(documents)
    return list(unique_documents)


def score_query_document_pairs(
    cross_encoder: CrossEncoder, query: str, documents: list[str]
) -> np.ndarray:
    """Scores how relevant each document is to a query using a cross-encoder.

    Args:
        cross_encoder: The cross-encoder model to score with.
        query: The query to score documents against.
        documents: The candidate documents to score.

    Returns:
        A relevance score per document, in the same order as `documents`.
    """
    pairs: list[list[str]] = [[query, document] for document in documents]
    return cross_encoder.predict(pairs)


def print_scores(scores: np.ndarray) -> None:
    """Prints each relevance score on its own line, preceded by a heading.

    Args:
        scores: The relevance scores to print.
    """
    print("Scores:")
    for score in scores:
        print(score)


def print_new_ordering(scores: np.ndarray, start_index: int = 0) -> None:
    """Prints document indices from most to least relevant, by score.

    Args:
        scores: The relevance scores to rank by.
        start_index: Added to every printed index. Use `0` when printing an
            index into a document list, or `1` when printing a human-facing
            rank position.
    """
    print("New Ordering:")
    for index in np.argsort(scores)[::-1]:
        print(index + start_index)


def select_top_reranked_documents(
    documents: list[str], scores: np.ndarray, top_n: int
) -> list[str]:
    """Selects the highest-scoring documents, most relevant first.

    Args:
        documents: The candidate documents.
        scores: A relevance score per document, in the same order.
        top_n: How many top-scoring documents to return.

    Returns:
        The `top_n` documents with the highest scores, ordered by score
        descending.
    """
    top_indices: np.ndarray = np.argsort(scores)[::-1][:top_n]
    return [documents[index] for index in top_indices]


def build_openai_client() -> OpenAI:
    """Builds an OpenAI client, loading credentials from the environment.

    Returns:
        An OpenAI client configured with `OPENAI_API_KEY`.
    """
    load_dotenv()
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_answer_from_context(
    client: OpenAI, query: str, context: str, model: str = ANSWER_MODEL
) -> list[str]:
    """Asks an OpenAI chat model to answer `query` using the given context.

    Args:
        client: The OpenAI client to send the request through.
        query: The user's question.
        context: The re-ranked document text to answer the question from.
        model: The chat model to use.

    Returns:
        The model's reply, split into lines.

    Raises:
        ValueError: If the model returned no content.
    """
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"based on the following context:\n\n{context}\n\nAnswer the query: '{query}'",
        },
    ]
    response: ChatCompletion = client.chat.completions.create(model=model, messages=messages)
    content: str | None = response.choices[0].message.content
    if content is None:
        raise ValueError(f"OpenAI model '{model}' returned no content.")
    return content.split("\n")


def main() -> None:
    """Runs the cross-encoder re-ranking demo end to end."""
    page_texts: list[str] = load_pdf_page_texts(PDF_PATH)
    character_chunks: list[str] = split_into_character_chunks(page_texts)
    token_chunks: list[str] = split_into_token_chunks(character_chunks)
    collection: chromadb.Collection = build_chroma_collection(token_chunks, COLLECTION_NAME)

    cross_encoder: CrossEncoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)

    # Scenario A: re-rank a single query's results and compare orderings.
    single_query_results: chromadb.QueryResult = retrieve_documents_for_queries(
        collection, SINGLE_QUERY, SINGLE_QUERY_RESULT_COUNT
    )
    retrieved_documents: list[str] = single_query_results["documents"][0]
    print_retrieved_documents(retrieved_documents)

    single_query_scores: np.ndarray = score_query_document_pairs(
        cross_encoder, SINGLE_QUERY, retrieved_documents
    )
    print_scores(single_query_scores)
    print_new_ordering(single_query_scores, start_index=1)

    # Scenario B: multi-query retrieval, de-duplication, re-ranking, and
    # answer generation from the top re-ranked documents.
    queries: list[str] = [ORIGINAL_QUERY] + GENERATED_QUERIES
    multi_query_results: chromadb.QueryResult = retrieve_documents_for_queries(
        collection, queries, MULTI_QUERY_RESULT_COUNT
    )
    unique_documents: list[str] = deduplicate_documents(multi_query_results["documents"])

    multi_query_scores: np.ndarray = score_query_document_pairs(
        cross_encoder, ORIGINAL_QUERY, unique_documents
    )
    print_scores(multi_query_scores)
    print_new_ordering(multi_query_scores, start_index=0)

    top_documents: list[str] = select_top_reranked_documents(
        unique_documents, multi_query_scores, TOP_RERANKED_DOCUMENT_COUNT
    )
    context: str = "\n\n".join(top_documents)

    client: OpenAI = build_openai_client()
    final_answer: list[str] = generate_answer_from_context(client, ORIGINAL_QUERY, context)
    print("Final Answer:")
    print(final_answer)


if __name__ == "__main__":
    main()
