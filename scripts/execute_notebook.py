"""Run the notebook cells that do not need a Google AI API key.

The question cells call Gemini. They need a free key from AI Studio, and
this repo does not have one, so those cells are not run.

What does run, from rag_workshop.ipynb:

- the setup cell (the Colab pip line is skipped, and the key prompt is
  replaced so the script does not block on input)
- the chunk-preview cell
- the cell that writes a Chroma collection with PersistentClient

Prints OK when the sample handbook was embedded and previewed.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "rag_workshop.ipynb"

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")


def _source(cell: dict) -> str:
    raw = cell["source"]
    return "".join(raw) if isinstance(raw, list) else raw


def _find(cells: list, marker: str) -> dict:
    matches = [c for c in cells if c.get("cell_type") == "code" and marker in _source(c)]
    if len(matches) != 1:
        raise SystemExit(f"expected one code cell containing {marker!r}, found {len(matches)}")
    return matches[0]


def _setup_source(cell: dict) -> str:
    """Turn the setup cell into plain Python.

    The notebook's first line is an IPython pip magic, and the key is read
    with getpass, which would hang a job with no terminal. Gemini is not
    called on this path. The dummy key only has to construct the client.
    """
    lines = []
    for line in _source(cell).splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("!"):
            continue
        if "getpass.getpass" in line:
            lines.append('GOOGLE_API_KEY = "not-used-for-this-run"\n')
            continue
        lines.append(line)
    return "".join(lines)


def run() -> dict[str, str]:
    os.chdir(ROOT)
    nb = json.loads(NOTEBOOK.read_text())
    if nb.get("nbformat") != 4:
        raise SystemExit(f"unexpected nbformat: {nb.get('nbformat')}")
    cells = nb["cells"]
    setup = _find(cells, "def chunk_text")
    preview = _find(cells, "preview_chunks = chunk_text")
    persist = _find(cells, "chromadb.PersistentClient")

    # Fail fast if a cell still tries to prompt. Never hang CI.
    import getpass

    def _refuse_prompt(*_args, **_kwargs):
        raise RuntimeError("getpass was called; this script does not read an API key")

    getpass.getpass = _refuse_prompt

    namespace: dict = {"__name__": "__main__"}
    outputs = {}
    for name, src in (
        ("setup", _setup_source(setup)),
        ("preview", _source(preview)),
        ("persist", _source(persist)),
    ):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                exec(src, namespace)
        except Exception:
            sys.stdout.write(buf.getvalue())
            traceback.print_exc()
            raise SystemExit(1)
        outputs[name] = buf.getvalue()
    return outputs


def main() -> None:
    try:
        outputs = run()
        db = ROOT / "rag_db"
        wrote = db.is_dir() and any(db.rglob("*"))
        if not wrote:
            print("FAILED: ./rag_db was not written", file=sys.stderr)
            raise SystemExit(1)
    finally:
        shutil.rmtree(ROOT / "rag_db", ignore_errors=True)

    for name in ("setup", "preview", "persist"):
        sys.stdout.write(outputs[name])
        if not outputs[name].endswith("\n"):
            sys.stdout.write("\n")

    errors = []
    setup_out = outputs["setup"]
    if "Embedding model ready." not in setup_out:
        errors.append("setup did not report the embedding model ready")
    if "All set. Move to the next cell." not in setup_out:
        errors.append("setup did not finish")
    loaded = re.search(r"Loaded (\d+) chunks from: The Builder's Handbook", setup_out)
    if not loaded or int(loaded.group(1)) < 2:
        errors.append("sample handbook was not indexed")
    preview_out = outputs["preview"]
    if "Strategy: Fixed size" not in preview_out or "[Chunk 1]" not in preview_out:
        errors.append("chunk preview did not print")
    saved = re.search(r"Saved (\d+) chunks to \./rag_db", outputs["persist"])
    if not saved or int(saved.group(1)) < 2:
        errors.append("on-disk Chroma cell did not save chunks")
    if errors:
        print("FAILED: " + "; ".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print("OK")


if __name__ == "__main__":
    main()
