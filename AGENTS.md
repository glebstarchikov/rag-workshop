# AGENTS.md

A Colab notebook that teaches retrieval-augmented generation to people with no coding experience. The stack is a Jupyter notebook, the Google Gemini API, ChromaDB, and sentence-transformers.

This file is the single source of agent instructions. Claude Code, Cursor, Codex, and other agents should read it first. CLAUDE.md stays a one-line pointer (`@AGENTS.md`), so the two files cannot drift. The repo is public; keep secrets out of the tree and keep the README screenshot (or the written waiver) current.

## Setup

Follow "Run it" in the README. The first cell asks for a Google AI API key. The repo does not contain one.

Follow "Run that check locally" for the same check GitHub Actions runs. The workflow pins Python 3.12. The setup cell downloads the `all-MiniLM-L6-v2` embedding model on first use. `scripts/execute_notebook.py` deletes `./rag_db` before it exits, including when the check fails.

## Checks

Run these before opening a pull request:

```bash
python -m pip install google-genai chromadb sentence-transformers pypdf
python scripts/execute_notebook.py
```

Look up flags and extra scripts in the manifest (package.json / pyproject.toml / Makefile). Do not restate them here. This repo has none. The commands above are the whole check, and they match `.github/workflows/notebook.yml`.

## Layout

`rag_workshop.ipynb` is the workshop. The sample handbook is the `SAMPLE_DOC` string in the first code cell, together with the helpers later cells call. `scripts/execute_notebook.py` is the key-free runner CI uses. `docs/notebook.png` is the screenshot in the README. `.github/workflows/notebook.yml` is the only workflow.

## Conventions

CI runs three code cells in one process: setup, the chunk preview, and the on-disk Chroma cell. Question cells call Gemini through `ask` and `answer_question`, and the runner leaves them alone. On the setup cell it skips lines that start with `!` and replaces the `getpass` line with a dummy key that only constructs the client. It then replaces `getpass.getpass` with a function that raises, so a prompt fails the job.

The runner finds those cells by one unique source string each: `def chunk_text`, `preview_chunks = chunk_text`, and `chromadb.PersistentClient`. Each string belongs in a single code cell. A second match stops the check.

The pass lines are `Embedding model ready.`, `All set. Move to the next cell.`, `Loaded <n> chunks from: The Builder's Handbook` with n at least 2, `Strategy: Fixed size`, `[Chunk 1]`, and `Saved <n> chunks to ./rag_db` with n at least 2.

Every committed code cell has empty `outputs` and a null `execution_count`. The README screenshot is `docs/notebook.png`.

The four packages are named in the setup cell's pip line, the README, and the workflow. Change them together.

## Agent skills

This repo is meant to work with [Matt Pocock's skills](https://github.com/mattpocock/skills) (`npx skills add mattpocock/skills`, or the Claude/Codex/Copilot plugin). After this file exists, run `/setup-matt-pocock-skills` once. That skill writes `docs/agents/` (issue tracker, domain docs, and triage labels if you use `/triage`) and fills in this section. Until then, treat GitHub Issues in this repo as the tracker.
