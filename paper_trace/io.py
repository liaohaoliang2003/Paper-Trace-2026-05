from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict


class InputReadError(RuntimeError):
    pass


def safe_stem(name: str) -> str:
    stem = Path(name).stem.lower() or "paper"
    stem = re.sub(r"[^a-z0-9._-]+", "-", stem).strip("-._")
    return stem or "paper"


def read_input_text(path: Path) -> str:
    path = Path(path)
    if not path.exists():
        raise InputReadError(f"Input file does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _read_pdf(path)
    raise InputReadError("Only .txt, .md, and .pdf inputs are supported")


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise InputReadError("PDF parsing requires optional dependency 'pypdf'. Install it or provide a .txt file.") from exc
    try:
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise InputReadError(f"Failed to parse PDF: {exc}") from exc
    if not text.strip():
        raise InputReadError("PDF text extraction returned empty text. Provide an extracted .txt file.")
    return text


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ensure_output_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
