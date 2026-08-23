"""
This script demonstrates how to make a simple API call to a local LLM (Large Language Model) server.
It sends a prompt to the server and prints the generated response.
"""

import json
import sys

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEOUT_SECONDS = 60


def main():
    try:
        payload = call_ollama("Explain what a Large Language Model is in simple terms in under 300 words")
    except requests.exceptions.ConnectionError:
        print(f"Error: could not connect to the LLM server at {OLLAMA_URL}. Is `ollama serve` running?")
        return 1
    except requests.exceptions.Timeout:
        print(f"Error: the LLM server did not respond within {TIMEOUT_SECONDS}s.")
        return 1
    except requests.exceptions.HTTPError as exc:
        # e.g. 404 when the model has not been pulled: `ollama pull llama3.2`
        print(f"Error: the LLM server returned {exc.response.status_code}: {exc.response.text.strip()}")
        return 1
    except json.JSONDecodeError as exc:
        # Most often means the response was streamed NDJSON, not a single object.
        print(f"Error: could not decode the response as JSON. First 200 chars:\n{exc.doc[:200]}")
        return 1
    except requests.exceptions.RequestException as exc:
        print(f"Error: request to the LLM server failed: {exc}")
        return 1
    except Exception as exc:
        print(f"Error: an unexpected error occurred: {exc}")
        return 1

    print(payload["response"])
    return 0


def call_ollama(prompt, model="llama3.2"):
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
