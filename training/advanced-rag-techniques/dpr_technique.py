"""Dense Passage Retrieval (DPR) demo.

Encodes a query and a fixed set of candidate passages with separate DPR
question/context encoders, then finds the passage whose embedding is most
similar (by cosine similarity) to the query embedding.
"""

import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizer,
    DPRQuestionEncoder,
    DPRQuestionEncoderTokenizer,
)

QUESTION_ENCODER_MODEL_NAME: str = "facebook/dpr-question_encoder-single-nq-base"
CONTEXT_ENCODER_MODEL_NAME: str = "facebook/dpr-ctx_encoder-single-nq-base"

QUERY: str = "capital of africa?"
PASSAGES: list[str] = [
    "Paris is the capital of France.",
    "Berlin is the capital of Germany.",
    "Madrid is the capital of Spain.",
    "Rome is the capital of Italy.",
    "Maputo is the capital of Mozambique.",
    "To be or not to be, that is the question.",
    "The quick brown fox jumps over the lazy dog.",
    "Grace Hopper was an American computer scientist and United States Navy rear admiral. who was a pioneer of computer programming, and one of the first programmers of the Harvard Mark I computer. inventor of the first compiler for a computer programming language.",
]


def load_question_encoder() -> tuple[DPRQuestionEncoder, DPRQuestionEncoderTokenizer]:
    """Loads the pre-trained DPR question encoder and its tokenizer.

    Returns:
        The question encoder model and matching tokenizer.
    """
    encoder: DPRQuestionEncoder = DPRQuestionEncoder.from_pretrained(QUESTION_ENCODER_MODEL_NAME)
    tokenizer: DPRQuestionEncoderTokenizer = DPRQuestionEncoderTokenizer.from_pretrained(
        QUESTION_ENCODER_MODEL_NAME
    )
    return encoder, tokenizer


def load_context_encoder() -> tuple[DPRContextEncoder, DPRContextEncoderTokenizer]:
    """Loads the pre-trained DPR context encoder and its tokenizer.

    Returns:
        The context encoder model and matching tokenizer.
    """
    encoder: DPRContextEncoder = DPRContextEncoder.from_pretrained(CONTEXT_ENCODER_MODEL_NAME)
    tokenizer: DPRContextEncoderTokenizer = DPRContextEncoderTokenizer.from_pretrained(
        CONTEXT_ENCODER_MODEL_NAME
    )
    return encoder, tokenizer


def encode_query(
    encoder: DPRQuestionEncoder, tokenizer: DPRQuestionEncoderTokenizer, query: str
) -> torch.Tensor:
    """Encodes a query into a single DPR embedding.

    Args:
        encoder: The DPR question encoder.
        tokenizer: The tokenizer matching `encoder`.
        query: The question text to encode.

    Returns:
        The query embedding, shaped `(1, hidden_size)`.
    """
    query_inputs = tokenizer(query, return_tensors="pt")
    return encoder(**query_inputs).pooler_output


def encode_passages(
    encoder: DPRContextEncoder, tokenizer: DPRContextEncoderTokenizer, passages: list[str]
) -> torch.Tensor:
    """Encodes each passage into a DPR embedding and stacks the results.

    Args:
        encoder: The DPR context encoder.
        tokenizer: The tokenizer matching `encoder`.
        passages: The candidate passage texts to encode.

    Returns:
        The stacked passage embeddings, shaped `(len(passages), hidden_size)`,
        in the same order as `passages`.
    """
    passage_embeddings: list[torch.Tensor] = []
    for passage in passages:
        passage_inputs = tokenizer(passage, return_tensors="pt")
        passage_embeddings.append(encoder(**passage_inputs).pooler_output)
    return torch.cat(passage_embeddings, dim=0)


def compute_similarities(
    query_embedding: torch.Tensor, passage_embeddings: torch.Tensor
) -> np.ndarray:
    """Computes the cosine similarity between a query and each passage.

    Args:
        query_embedding: The query embedding, shaped `(1, hidden_size)`.
        passage_embeddings: The passage embeddings, shaped
            `(num_passages, hidden_size)`.

    Returns:
        A similarity score per passage, shaped `(1, num_passages)`.
    """
    return cosine_similarity(query_embedding.detach().numpy(), passage_embeddings.detach().numpy())


def find_most_similar_passage(passages: list[str], similarities: np.ndarray) -> str:
    """Selects the passage with the highest similarity score.

    Args:
        passages: The candidate passage texts.
        similarities: A similarity score per passage, in the same order.

    Returns:
        The passage text with the highest score.
    """
    most_similar_index: np.intp = np.argmax(similarities)
    return passages[most_similar_index]


def main() -> None:
    """Runs the DPR retrieval demo end to end."""
    question_encoder, question_tokenizer = load_question_encoder()
    context_encoder, context_tokenizer = load_context_encoder()

    query_embedding: torch.Tensor = encode_query(question_encoder, question_tokenizer, QUERY)
    passage_embeddings: torch.Tensor = encode_passages(context_encoder, context_tokenizer, PASSAGES)

    similarities: np.ndarray = compute_similarities(query_embedding, passage_embeddings)
    print("Similarities:", similarities)

    most_similar_passage: str = find_most_similar_passage(PASSAGES, similarities)
    print("Most relevant passage:", most_similar_passage)


if __name__ == "__main__":
    main()
