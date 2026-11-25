# AGENTS.md

A Colab notebook that teaches retrieval-augmented generation (RAG) to people with no coding experience: they paste a free Gemini key, ask questions about a sample handbook, then upload their own document and watch retrieval and hallucination at work. Python, with the Gemini API, ChromaDB and sentence-transformers.

Write new agent instructions here. CLAUDE.md stays the single line `@AGENTS.md`.

## Checks

Before you finish, run what CI runs, in a Python 3.12 venv: `python -m pip install google-genai chromadb sentence-transformers pypdf && python scripts/execute_notebook.py`. It ends with `OK`.

That check runs only the setup, chunk-preview and on-disk Chroma cells. Every other code cell calls Gemini with the learner's key or uses Colab's file picker, so neither CI nor the local check runs them. When you change one of those cells, say in the PR that it was not run, so Gleb runs it in Colab before merging: the README's Colab link opens main.

## Layout

- The first code cell is both setup and library: it installs the packages, asks for the key, and defines `SAMPLE_DOC` and the helpers later cells call (`chunk_text`, `load_document`, `ask`, `answer_question`).

## Conventions

- Write markdown cells and code comments for someone who has never coded: plain words and everyday comparisons, as the existing cells do. Open each new code cell with `#@title <what it does> { display-mode: "form" }`, so learners see a form, not code.
- Keep the key prompt as the one line `GOOGLE_API_KEY = getpass.getpass(...)` in the setup cell. The repo is public, so no key is ever committed. `scripts/execute_notebook.py` replaces that whole line with `GOOGLE_API_KEY = "not-used-for-this-run"`, so keep the name and keep the call on one line; any other way of reading the key breaks CI. The runner drops only the setup cell's `!` lines and runs the rest of its three cells as plain Python, so shell lines in the setup cell start with `!` (never `%pip`), and the chunk-preview and Chroma cells hold no `!` or `%` lines at all.
- The runner finds its cells by the marker strings that `run()` passes to `_find` in `scripts/execute_notebook.py`, and stops if a marker is in no code cell or in more than one. Keep each marker in exactly one code cell.
- Commit the notebook with every code cell's `outputs` empty and `execution_count` null. Clear them after you run it locally.
- The four packages are named in the setup cell's `!pip` line, the Checks command above, the README's "Run that check locally" and `.github/workflows/notebook.yml`; change all four together. The README also names the Gemini model, which is `MODEL_NAME` in the setup cell.
