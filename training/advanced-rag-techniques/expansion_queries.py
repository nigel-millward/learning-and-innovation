import sys
from typing import Any

import httpx
import numpy as np
import ollama
import umap
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import ChatOllama
from pypdf import PdfReader

from chromadb.api import ClientAPI
from chromadb.api.types import PyEmbeddings
from helper_utils import project_embeddings, word_wrap


################################################################################################
### Setup: local Ollama server (same setup as experiments/ai/01-llm-api)
###   brew install ollama  ->  ollama serve  ->  ollama pull llama3.2
################################################################################################
OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "llama3.2"
TIMEOUT_SECONDS: int = 60


################################################################################################
### Extract Text from PDF & filter empty strings
################################################################################################
reader: PdfReader = PdfReader("data/microsoft-annual-report.pdf")
pdf_texts: list[str] = [p.extract_text().strip() for p in reader.pages]

# Filter the empty strings
pdf_texts = [text for text in pdf_texts if text]

################################################################################################
### Split the text into chunks
################################################################################################
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

character_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""], chunk_size=1000, chunk_overlap=0
)
character_split_texts: list[str] = character_splitter.split_text("\n\n".join(pdf_texts))

################################################################################################
### Split chunks into maximum token size, as LLMs have token limits
################################################################################################

token_splitter: SentenceTransformersTokenTextSplitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap=0, tokens_per_chunk=256
)

token_split_texts: list[str] = []
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)


################################################################################################
### Use chrome db to to create vectors and then store them in the collection
################################################################################################
# now we import chromadb and the SentenceTransformerEmbeddingFunction
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


embedding_function: SentenceTransformerEmbeddingFunction = SentenceTransformerEmbeddingFunction()
# print(embedding_function([token_split_texts[10]]))

# we then instantiate the Chroma client and create a collection called "microsoft-collection"
chroma_client: ClientAPI = chromadb.Client()
chroma_collection: chromadb.Collection = chroma_client.create_collection(
    "microsoft-collection", embedding_function=embedding_function
)

# extract the embeddings of the token_split_texts
ids: list[str] = [str(i) for i in range(len(token_split_texts))]

chroma_collection.add(ids=ids, documents=token_split_texts)
chroma_collection.count()

query: str = "What was the total revenue for the year?"

results: chromadb.QueryResult = chroma_collection.query(query_texts=[query], n_results=5)
# Union because this is reassigned further down from one query's hits
# (`list[str]`) to every query's hits (`list[list[str]] | None`).
retrieved_documents: list[str] | list[list[str]] | None = results["documents"][0]

# for document in retrieved_documents:
#     print(word_wrap(document))
#     print("\n")



################################################################################################
### Generate multiple related queries based on the original query
################################################################################################
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


original_query: str = (
    "What details can you provide about the factors that led to revenue growth?"
)
try:
    aug_queries: list[str] = generate_multi_query(original_query)
except (ConnectionError, httpx.ConnectError):
    sys.exit(f"Error: could not connect to Ollama at {OLLAMA_BASE_URL}. Is `ollama serve` running?")
except httpx.TimeoutException:
    sys.exit(f"Error: Ollama did not respond within {TIMEOUT_SECONDS}s.")
except ollama.ResponseError as exc:
    # e.g. 404 when the model has not been pulled: `ollama pull llama3.2`
    sys.exit(f"Error: Ollama returned {exc.status_code}: {exc.error}")

# 1. First step show the augmented queries
for query in aug_queries:
    print("\n", query)

# 2. concatenate the original query with the augmented queries
joint_query: list[str] = [
    original_query
] + aug_queries  # original query is in a list because chroma can actually handle multiple queries, so we add it in a list

# print("======> \n\n", joint_query)

results = chroma_collection.query(
    query_texts=joint_query, n_results=5, include=["documents", "embeddings"]
)
retrieved_documents = results["documents"]

# Deduplicate the retrieved documents
unique_documents: set[str] = set()
for documents in retrieved_documents:
    for document in documents:
        unique_documents.add(document)


# output the results documents
for i, documents in enumerate(retrieved_documents):
    print(f"Query: {joint_query[i]}")
    print("")
    print("Results:")
    for doc in documents:
        print(word_wrap(doc))
        print("")
    print("-" * 100)

embeddings: chromadb.Embeddings | PyEmbeddings | np.ndarray | None = chroma_collection.get(include=["embeddings"])["embeddings"]
umap_transform: umap.UMAP = umap.UMAP(random_state=0, transform_seed=0).fit(embeddings)
projected_dataset_embeddings: np.ndarray = project_embeddings(embeddings, umap_transform)

# 4. We can also visualize the results in the embedding space
original_query_embedding: list[np.ndarray] = embedding_function([original_query])
augmented_query_embeddings: list[np.ndarray] = embedding_function(joint_query)


project_original_query: np.ndarray = project_embeddings(original_query_embedding, umap_transform)
project_augmented_queries: np.ndarray = project_embeddings(
    augmented_query_embeddings, umap_transform
)

# This mirrors chromadb's own `QueryResult["embeddings"]` declaration; the
# flattened `result_embeddings` below is `Any` because collapsing that union
# loses the per-query structure it encoded.
retrieved_embeddings: (
    list[chromadb.Embeddings] | list[PyEmbeddings] | list[np.ndarray] | None
) = results["embeddings"]
result_embeddings: list[Any] = [item for sublist in retrieved_embeddings for item in sublist]

projected_result_embeddings: np.ndarray = project_embeddings(result_embeddings, umap_transform)

import matplotlib.pyplot as plt


# Plot the projected query and retrieved documents in the embedding space
plt.figure()
plt.scatter(
    projected_dataset_embeddings[:, 0],
    projected_dataset_embeddings[:, 1],
    s=10,
    color="gray",
)
plt.scatter(
    project_augmented_queries[:, 0],
    project_augmented_queries[:, 1],
    s=150,
    marker="X",
    color="orange",
)
plt.scatter(
    projected_result_embeddings[:, 0],
    projected_result_embeddings[:, 1],
    s=100,
    facecolors="none",
    edgecolors="g",
)
plt.scatter(
    project_original_query[:, 0],
    project_original_query[:, 1],
    s=150,
    marker="X",
    color="r",
)

plt.gca().set_aspect("equal", "datalim")
plt.title(f"{original_query}")
plt.axis("off")
plt.show()  # display the plot
