from helper_utils import word_wrap, load_chroma
from pypdf import PdfReader
import os
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv


from pypdf import PdfReader
import numpy as np

from langchain_community.document_loaders import PyPDFLoader
from chromadb.api import ClientAPI


# Load environment variables from .env file
load_dotenv()

openai_key: str | None = os.getenv("OPENAI_API_KEY")
client: OpenAI = OpenAI(api_key=openai_key)


import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_function: SentenceTransformerEmbeddingFunction = SentenceTransformerEmbeddingFunction()


reader: PdfReader = PdfReader("data/microsoft-annual-report.pdf")
pdf_texts: list[str] = [p.extract_text().strip() for p in reader.pages]

# Filter the empty strings
pdf_texts = [text for text in pdf_texts if text]

# Note: `langchain.text_splitter` was removed upstream; `langchain_text_splitters`
# is the module these classes now live in (same fix already used by
# expansion_answer.py/expansion_queries.py in this directory).
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

character_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""], chunk_size=1000, chunk_overlap=0
)
character_split_texts: list[str] = character_splitter.split_text("\n\n".join(pdf_texts))

token_splitter: SentenceTransformersTokenTextSplitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap=0, tokens_per_chunk=256
)

token_split_texts: list[str] = []
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)

chroma_client: ClientAPI = chromadb.Client()
chroma_collection: chromadb.Collection = chroma_client.get_or_create_collection(
    "microsoft-collect", embedding_function=embedding_function
)

# extract the embeddings of the token_split_texts
ids: list[str] = [str(i) for i in range(len(token_split_texts))]

chroma_collection.add(ids=ids, documents=token_split_texts)

count: int = chroma_collection.count()

query: str = "What has been the investment in research and development?"

results: chromadb.QueryResult = chroma_collection.query(
    query_texts=query, n_results=10, include=["documents", "embeddings"]
)

# Union because this is reassigned further down from one query's hits
# (`list[str]`) to every query's hits (`list[list[str]] | None`).
retrieved_documents: list[str] | list[list[str]] | None = results["documents"][0]

for document in results["documents"][0]:
    print(word_wrap(document))
    print("")

from sentence_transformers import CrossEncoder

cross_encoder: CrossEncoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

pairs: list[list[str]] = [[query, doc] for doc in retrieved_documents]
scores: np.ndarray = cross_encoder.predict(pairs)

print("Scores:")
for score in scores:
    print(score)

print("New Ordering:")
for o in np.argsort(scores)[::-1]:
    print(o + 1)

original_query: str = (
    "What were the most important factors that contributed to increases in revenue?"
)

generated_queries: list[str] = [
    "What were the major drivers of revenue growth?",
    "Were there any new product launches that contributed to the increase in revenue?",
    "Did any changes in pricing or promotions impact the revenue growth?",
    "What were the key market trends that facilitated the increase in revenue?",
    "Did any acquisitions or partnerships contribute to the revenue growth?",
]

# concatenate the original query with the generated queries
queries: list[str] = [original_query] + generated_queries


results = chroma_collection.query(
    query_texts=queries, n_results=10, include=["documents", "embeddings"]
)
retrieved_documents = results["documents"]

# Deduplicate the retrieved documents
# Union because this is reassigned from a `set` to a `list` once dedupe is done
# (the list form is needed for the positional indexing further down).
unique_documents: set[str] | list[str] = set()
for documents in retrieved_documents:
    for document in documents:
        unique_documents.add(document)

unique_documents = list(unique_documents)

pairs = []
for doc in unique_documents:
    pairs.append([original_query, doc])

scores = cross_encoder.predict(pairs)

print("Scores:")
for score in scores:
    print(score)

print("New Ordering:")
for o in np.argsort(scores)[::-1]:
    print(o)
# ====
top_indices: np.ndarray = np.argsort(scores)[::-1][:5]
top_documents: list[str] = [unique_documents[i] for i in top_indices]

# Concatenate the top documents into a single context
context: str = "\n\n".join(top_documents)


# Generate the final answer using the OpenAI model
def generate_multi_query(query: str, context: str, model: str = "gpt-5.6-luna") -> list[str]:

    prompt: str = f"""
    You are a knowledgeable financial research assistant. 
    Your users are inquiring about an annual report. 
    """

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": f"based on the following context:\n\n{context}\n\nAnswer the query: '{query}'",
        },
    ]

    response: ChatCompletion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    # Union because the raw reply (`str | None`) is reassigned to its
    # newline-split form (`list[str]`) on the next line.
    content: str | None | list[str] = response.choices[0].message.content
    content = content.split("\n")
    return content


res: list[str] = generate_multi_query(query=original_query, context=context)
print("Final Answer:")
print(res)
