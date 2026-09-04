#!/usr/bin/env python
"""Download a paper PDF and extract text on Windows, macOS, or Linux."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a PDF, verify it, and extract readable text."
    )
    parser.add_argument("pdf_url")
    parser.add_argument("pdf_name", help="Safe output slug without an extension")
    parser.add_argument(
        "--project-dir",
        help="Output project root; defaults to RESEARCH_PROJECT_DIR, CLAUDE_PROJECT_DIR, or cwd",
    )
    return parser.parse_args()


def project_dir(explicit: str | None) -> Path:
    value = (
        explicit
        or os.environ.get("RESEARCH_PROJECT_DIR")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )
    return Path(value).expanduser().resolve()


def safe_slug(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}", value):
        raise ValueError(
            "pdf_name must be 1-120 characters using letters, digits, dot, underscore, or hyphen"
        )
    return value


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 WAMResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    if not payload.lstrip().startswith(b"%PDF-"):
        raise RuntimeError("downloaded response is not a PDF")
    destination.write_bytes(payload)


def extract_with_pdftotext(source: Path, destination: Path) -> str | None:
    executable = shutil.which("pdftotext")
    if not executable:
        return None
    for layout_args, label in ((["-layout"], "pdftotext -layout"), ([], "pdftotext")):
        result = subprocess.run(
            [executable, *layout_args, str(source), str(destination)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and destination.exists() and destination.stat().st_size:
            return label
    return None


def extract_with_python(source: Path, destination: Path) -> str | None:
    try:
        import fitz

        document = fitz.open(source)
        text = "\n\n".join(page.get_text() for page in document)
        label = "pymupdf"
    except Exception:
        try:
            import pdfplumber

            with pdfplumber.open(source) as document:
                text = "\n\n".join((page.extract_text() or "") for page in document.pages)
            label = "pdfplumber"
        except Exception:
            return None
    if not text.strip():
        return None
    destination.write_text(text, encoding="utf-8")
    return label


def main() -> int:
    args = parse_args()
    try:
        slug = safe_slug(args.pdf_name)
        papers_dir = project_dir(args.project_dir) / "papers"
        papers_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = papers_dir / f"{slug}.pdf"
        text_path = papers_dir / f"{slug}.txt"
        download(args.pdf_url, pdf_path)
        extractor = extract_with_pdftotext(pdf_path, text_path)
        if extractor is None:
            extractor = extract_with_python(pdf_path, text_path)
        if extractor is None:
            raise RuntimeError("no working PDF text extractor produced output")
        print(
            f"ok: extractor={extractor} pdf_bytes={pdf_path.stat().st_size} "
            f"txt_bytes={text_path.stat().st_size}"
        )
        print(text_path)
        return 0
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
