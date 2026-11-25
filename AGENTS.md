# AGENTS.md

A Colab notebook that teaches retrieval-augmented generation (RAG) to people with no coding experience: they paste a free Gemini key, ask questions about a sample handbook, then upload their own document and watch retrieval and hallucination at work. Python, with the Gemini API, ChromaDB and sentence-transformers.

Write new agent instructions here. CLAUDE.md stays the single line `@AGENTS.md`.

## Checks

Before you finish, run what CI runs, in a Python 3.12 venv: `python -m pip install google-genai chromadb sentence-transformers pypdf && python scripts/execute_notebook.py`. It ends with `OK`.

That check runs only the setup, chunk-preview and on-disk Chroma cells. Every other code cell calls Gemini with the learner's key or uses Colab's file picker, so nothing here runs it. When you change one of those cells, say in the PR that it was not run.

## Layout

- The first code cell is both setup and library: it installs the packages, asks for the key, and defines `SAMPLE_DOC` and the helpers later cells call (`chunk_text`, `load_document`, `ask`, `answer_question`).

## Conventions

- Write markdown cells and code comments for someone who has never coded: plain words and everyday comparisons, as the existing cells do. Each code cell opens with a `#@title` line, and `{ display-mode: "form" }` on it shows learners a form instead of code.
- Keep the key prompt as the `getpass.getpass` line in the setup cell. The repo is public, so the key never enters it, and `scripts/execute_notebook.py` swaps exactly that line for a dummy key; any other way of reading the key breaks CI.
- The runner finds its cells by the marker strings that `run()` passes to `_find` in `scripts/execute_notebook.py`, and stops if a marker is in no code cell or in two. Keep each marker in exactly one code cell.
- Commit the notebook with every code cell's `outputs` empty and `execution_count` null. Clear them after you run it locally.
- The four packages are named in the setup cell's `!pip` line, the README's "Run that check locally" and `.github/workflows/notebook.yml`; change all three together. The README also names the Gemini model, which is `MODEL_NAME` in the setup cell.
