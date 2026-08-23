"""
Interactive chat with a local Ollama model.

This experiment builds on simple_prompt.py by allowing
the user to repeatedly send prompts to the LLM.

Each request is independent. No conversation history
is preserved between prompts.
"""

import sys

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEOUT_SECONDS = 60
DEFAULT_MODEL = "llama3.2"


def main():

    print("Interactive Chat")
    print("================")
    print("Type 'exit' to quit.\n")

    while True:
        prompt = input("You: ").strip()

        # skip current iteration if the user presesses enter without typing anything
        # so an empty prompt is not sent to the LLM server
        if not prompt:
            continue

        if prompt.lower() in ("exit", "quit"):
            print("\nGoodbye!")
            break

        try:
            payload = _ollama_request(prompt)

        except requests.exceptions.ConnectionError:
            print(
                f"\nError: could not connect to the LLM server at "
                f"{OLLAMA_URL}. Is `ollama serve` running?\n"
            )

        except requests.exceptions.Timeout:
            print(
                f"\nError: the LLM server did not respond within "
                f"{TIMEOUT_SECONDS}s.\n"
            )

        except requests.exceptions.JSONDecodeError as exc:
            # Most often means the response was streamed NDJSON, not a single object.
            print(
                f"\nError: could not decode response as JSON.\n"
                f"First 200 characters:\n{exc.doc[:200]}\n"
            )

        except requests.exceptions.HTTPError as exc:
            # e.g. 404 when the model has not been pulled: `ollama pull llama3.2`
            print(
                f"\nError: the LLM server returned "
                f"{exc.response.status_code}: "
                f"{exc.response.text.strip()}\n"
            )

        except requests.exceptions.RequestException as exc:
            print(f"\nError: request failed: {exc}\n")

        else:
            print(f"\nAssistant: {payload['response']}\n")

    return 0


def _ollama_request(prompt, model=DEFAULT_MODEL):
    """Send `prompt` to the local Ollama server and return the decoded JSON payload.

    Raises requests.exceptions.RequestException on any transport or HTTP failure.
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    sys.exit(main())
