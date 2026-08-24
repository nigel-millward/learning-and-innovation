"""
Conversation history with a local Ollama model.

This experiment builds on 02_interactive_chat.py, which sent each prompt
independently, so the model could not refer back to anything said earlier.

The difference is the endpoint. 01 and 02 used /api/generate, which takes a
single `prompt` string. This script uses /api/chat, which takes a `messages`
list -- the whole conversation, resent on every request.

The model itself is still stateless. The history lives in this process, in the
`messages` list, and is uploaded again in full each turn. That is what "context"
means in practice, and it is why the prompt token count grows every turn.
"""

import sys

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
TIMEOUT_SECONDS = 60
DEFAULT_MODEL = "llama3.2"

SYSTEM_PROMPT = "You are a concise, helpful assistant. Keep answers under 150 words."

# Each exchange is two messages (user + assistant). Once the history exceeds
# this many exchanges the oldest are dropped: the context window is finite, and
# every token resent is a token paid for. Dropping them is what makes the model
# "forget" -- try asking about something from the start of a long conversation.
MAX_HISTORY_TURNS = 10


def main():

    print("Conversation History")
    print("====================")
    print("Type 'exit' to quit, '/reset' to clear the history, '/history' to show it.\n")

    # The system message is not part of the conversation proper, so it is held
    # separately and prepended at request time. That keeps the trimming below
    # simple -- it can never accidentally drop the instructions.
    messages = []

    while True:
        prompt = input("You: ").strip()

        # skip current iteration if the user presses enter without typing anything
        # so an empty prompt is not sent to the LLM server
        if not prompt:
            continue

        if prompt.lower() in ("exit", "quit"):
            print("\nGoodbye!")
            break

        if prompt.lower() == "/reset":
            messages.clear()
            print("\nHistory cleared. The model now knows nothing of what came before.\n")
            continue

        if prompt.lower() == "/history":
            _print_history(messages)
            continue

        messages.append({"role": "user", "content": prompt})

        try:
            payload = _ollama_chat(messages)

        except requests.exceptions.ConnectionError:
            messages.pop()
            print(
                f"\nError: could not connect to the LLM server at "
                f"{OLLAMA_URL}. Is `ollama serve` running?\n"
            )

        except requests.exceptions.Timeout:
            messages.pop()
            print(
                f"\nError: the LLM server did not respond within "
                f"{TIMEOUT_SECONDS}s. A long history makes this more likely.\n"
            )

        except requests.exceptions.JSONDecodeError as exc:
            messages.pop()
            # Most often means the response was streamed NDJSON, not a single object.
            print(
                f"\nError: could not decode response as JSON.\n"
                f"First 200 characters:\n{exc.doc[:200]}\n"
            )

        except requests.exceptions.HTTPError as exc:
            messages.pop()
            # e.g. 404 when the model has not been pulled: `ollama pull llama3.2`
            print(
                f"\nError: the LLM server returned "
                f"{exc.response.status_code}: "
                f"{exc.response.text.strip()}\n"
            )

        except requests.exceptions.RequestException as exc:
            messages.pop()
            print(f"\nError: request failed: {exc}\n")

        else:
            # Only reached on success. The reply is appended so the *next*
            # request carries it, which is the whole point of the experiment.
            #
            # Note the pop() in every except branch above: without it a failed
            # turn would leave a user message with no assistant reply, and every
            # later request would be sent with a malformed history.
            reply = payload["message"]["content"]
            messages.append({"role": "assistant", "content": reply})

            print(f"\nAssistant: {reply}\n")
            _print_token_usage(payload, messages)

            _trim_history(messages)

    return 0


def _ollama_chat(messages, model=DEFAULT_MODEL):
    """Send the whole conversation to the local Ollama server, return the JSON payload.

    Unlike /api/generate, /api/chat takes a list of {"role", "content"} messages
    rather than a single prompt string. Nothing is stored server side, so the
    full history has to be sent on every call.

    Raises requests.exceptions.RequestException on any transport or HTTP failure.
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "stream": False,
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _print_token_usage(payload, messages):
    """Show the cost of the context window.

    prompt_eval_count is the tokens read (the history plus this question) and
    eval_count is the tokens written (the answer). Watch the first number climb
    every turn while the second stays roughly flat -- that growth is what
    eventually forces summarising, windowing, or retrieval.
    """
    prompt_tokens = payload.get("prompt_eval_count", 0)
    reply_tokens = payload.get("eval_count", 0)

    print(
        f"  [history: {len(messages) // 2} exchanges | "
        f"prompt: {prompt_tokens} tokens | "
        f"reply: {reply_tokens} tokens | "
        f"total: {prompt_tokens + reply_tokens} tokens]\n"
    )


def _print_history(messages):
    """Print the exact list that gets sent to the model on the next request."""
    if not messages:
        print("\nHistory is empty.\n")
        return

    print(f"\nHistory ({len(messages)} messages, oldest first):")
    for message in messages:
        content = message["content"].replace("\n", " ")
        if len(content) > 70:
            content = content[:70] + "..."
        print(f"  {message['role']:>9}: {content}")
    print()


def _trim_history(messages):
    """Drop the oldest exchanges once the history grows past MAX_HISTORY_TURNS.

    A crude strategy, chosen because it is easy to see happening: the model
    loses the start of the conversation. Better approaches -- summarising the
    dropped turns, or retrieving only the relevant ones -- come later, in
    04-rag-over-docs and 06-agent-with-memory.
    """
    max_messages = MAX_HISTORY_TURNS * 2

    if len(messages) > max_messages:
        dropped = len(messages) - max_messages
        del messages[:dropped]
        print(
            f"  [trimmed {dropped} message(s) from the start of the history to "
            f"stay within {MAX_HISTORY_TURNS} exchanges]\n"
        )


if __name__ == "__main__":
    sys.exit(main())
