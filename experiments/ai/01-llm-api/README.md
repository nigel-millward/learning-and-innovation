# 01 - LLM API

## Objective

Learn how an application communicates with a Large Language Model.


## setup

install
brew install ollama

start the server
ollama serve

pull a model
ollama run llama3.2

test
curl http://localhost:11434/api/generate \
-d '{
"model":"llama3.2",
"prompt":"What is Snowflake?"
}'

## Experiments

### 01-simple-prompt

Single request and response.

Learning:
API call
Error handling
JSON response

### 02-interactive-chat

Interactive console application.

Learning:
- User interaction
- Repeated requests

### 03-conversation-history

Maintains conversation history.

Learning:
- Context
- Memory
- Token growth

## Architecture

Python
  |
Ollama
  |
Llama 3.2
  |
Response

## Key Learning Outcomes

- What an LLM API looks like
- Prompt construction
- Response handling
- Context management
- Foundation for agents