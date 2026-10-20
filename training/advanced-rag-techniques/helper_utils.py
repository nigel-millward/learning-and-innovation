# helper_utils.py
from typing import Any, Callable

import numpy as np
import chromadb
import pandas as pd
import umap
from pypdf import PdfReader, PageObject


def project_embeddings(embeddings: Any, umap_transform: umap.UMAP) -> np.ndarray:
    """
    Projects the given embeddings using the provided UMAP transformer.

    Args:
    embeddings (numpy.ndarray): The embeddings to project. Callers in this
        project pass numpy arrays as well as chromadb's own (partly Optional)
        Embeddings/PyEmbeddings result types, so `Any` is the honest type here
        rather than a narrower one that would reject those real call sites.
    umap_transform (umap.UMAP): The trained UMAP transformer.

    Returns:
    numpy.ndarray: The projected embeddings.
    """
    projected_embeddings: np.ndarray = umap_transform.transform(embeddings)
    return projected_embeddings


def word_wrap(text: str, width: int = 87) -> str:
    """
    Wraps the given text to the specified width.

    Args:
    text (str): The text to wrap.
    width (int): The width to wrap the text to.

    Returns:
    str: The wrapped text.
    """
    return "\n".join([text[i : i + width] for i in range(0, len(text), width)])


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.

    Args:
    file_path (str): The path to the PDF file.

    Returns:
    str: The extracted text.
    """
    text: list[str] = []
    with open(file_path, "rb") as f:
        pdf: PdfReader = PdfReader(f)
        for page_num in range(pdf.get_num_pages()):
            page: PageObject = pdf.get_page(page_num)
            text.append(page.extract_text())
    return "\n".join(text)


def load_chroma(
    filename: str, collection_name: str, embedding_function: Callable[[str], Any]
) -> chromadb.Collection:
    """
    Loads a document from a PDF, extracts text, generates embeddings, and stores it in a Chroma collection.

    Args:
    filename (str): The path to the PDF file.
    collection_name (str): The name of the Chroma collection.
    embedding_function (callable): A function to generate embeddings.

    Returns:
    chroma.Collection: The Chroma collection with the document embeddings.
    """
    # Extract text from the PDF
    text: str = extract_text_from_pdf(filename)

    # Split text into paragraphs or chunks
    paragraphs: list[str] = text.split("\n\n")

    # Generate embeddings for each chunk
    embeddings: list[Any] = [embedding_function(paragraph) for paragraph in paragraphs]

    # Create a DataFrame to store text and embeddings
    data: dict[str, list[Any]] = {"text": paragraphs, "embeddings": embeddings}
    df: pd.DataFrame = pd.DataFrame(data)

    # Create or load the Chroma collection

    collection: chromadb.Collection = chromadb.Client().create_collection(collection_name)

    # Add the data to the Chroma collection
    for ids, row in df.iterrows():

        collection.add(ids=ids, documents=row["text"], embeddings=row["embeddings"])
        # collection.add(text=row["text"], embedding=row["embeddings"])

    return collection
