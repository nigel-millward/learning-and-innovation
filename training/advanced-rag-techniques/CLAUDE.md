# CLAUDE.md - RAG Project Guidelines

## Build/Test Commands
- Venv: uv-managed, outside the repo, at `~/.virtualenv/advanced-rag-techniques-3.1.2/` (CPython 3.12). It has no `pip`
- Activate venv: `source ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/activate`
- Install dependencies: `uv pip install -r requirements.txt` (venv active), or without activating:
  `uv pip install --python ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/python -r requirements.txt`
- Run scripts from this directory: `python <filename>.py` (paths like `data/...` are relative to it)
- Run without the matplotlib window blocking (e.g. `expansion_answer.py`): `MPLBACKEND=Agg python <filename>.py`
- `expansion_answer.py` needs a local Ollama server (`ollama serve`) with `llama3.2` pulled; see README.md
- Single test: `pytest path/to/test.py -v`

## Code Style Guidelines
- **Imports**: Group standard library, third-party, and local imports in that order
- **Formatting**: Use consistent indentation (4 spaces), max line length ~80-100 chars
- **Types**: Use type hints in function signatures
- **Naming**: 
  - Snake_case for variables and functions
  - CamelCase for classes
  - UPPERCASE for constants  
- **Documentation**: Use docstrings for all functions, following Google style
- **Error Handling**: Use try/except blocks with specific exceptions
- **Code Organization**: Keep functions focused and modular, limit side effects

## Project Structure
- Core RAG techniques in separate modules
- Utilities in helper_utils.py
- Data in data/ directory