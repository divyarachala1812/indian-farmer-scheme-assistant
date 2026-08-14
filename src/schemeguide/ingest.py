from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from schemeguide.config import CHUNK_OVERLAP, CHUNK_SIZE, PROCESSED_DIR, RAW_DIR, SOURCE_MANIFEST


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    publisher: str
    url: str
    format: str


def load_sources() -> list[Source]:
    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    return [Source(**source) for source in payload["sources"]]


def _normalise(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _download(source: Source) -> tuple[Path, str]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    suffix = ".pdf" if source.format == "pdf" else ".html"
    path = RAW_DIR / f"{source.id}{suffix}"
    response = requests.get(
        source.url,
        timeout=180,
        headers={"User-Agent": "Mozilla/5.0 (compatible; schemeguide-research/1.0)"},
    )
    response.raise_for_status()
    path.write_bytes(response.content)
    return path, hashlib.sha256(response.content).hexdigest()


def _pdf_sections(path: Path) -> list[tuple[str, int | None]]:
    reader = PdfReader(path)
    sections = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = _normalise(page.extract_text() or "")
        if len(text) >= 40:
            sections.append((text, page_number))
    return sections


def _html_sections(path: Path) -> list[tuple[str, int | None]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for node in soup(["script", "style", "noscript", "svg"]):
        node.decompose()
    main = (
        soup.select_one("#annual")
        or soup.select_one("main")
        or soup.select_one(".container")
        or soup.body
        or soup
    )
    parts = []
    for node in main.select("h1, h2, h3, h4, p, li"):
        text = _normalise(node.get_text(" ", strip=True))
        if len(text) >= 20:
            parts.append(text)
    if len(" ".join(parts)) < 200:
        parts = [_normalise(main.get_text("\n", strip=True))]
    return [("\n".join(parts), None)]


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = _normalise(text)
    if len(text) <= size:
        return [text] if text else []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(
                text.rfind("\n", start + size // 2, end), text.rfind(". ", start + size // 2, end)
            )
            if boundary > start:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        next_start = max(0, end - overlap)
        if next_start <= start:
            next_start = end
        start = next_start
    return chunks


def build_corpus() -> list[dict[str, object]]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chunks: list[dict[str, object]] = []
    acquisition: list[dict[str, object]] = []
    for source in load_sources():
        path, digest = _download(source)
        sections = _pdf_sections(path) if source.format == "pdf" else _html_sections(path)
        source_count = 0
        for text, page in sections:
            for local_index, chunk in enumerate(chunk_text(text), start=1):
                source_count += 1
                chunks.append(
                    {
                        "chunk_id": f"{source.id}-{page or 0:03d}-{local_index:02d}",
                        "source_id": source.id,
                        "title": source.title,
                        "publisher": source.publisher,
                        "url": source.url,
                        "page": page,
                        "text": chunk,
                    }
                )
        acquisition.append(
            {
                "source_id": source.id,
                "file": path.name,
                "sha256": digest,
                "chunks": source_count,
            }
        )

    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    chunks_path.write_text(
        "\n".join(json.dumps(chunk, ensure_ascii=False) for chunk in chunks) + "\n",
        encoding="utf-8",
    )
    (PROCESSED_DIR / "acquisition_manifest.json").write_text(
        json.dumps({"sources": acquisition, "total_chunks": len(chunks)}, indent=2),
        encoding="utf-8",
    )
    return chunks


def load_chunks() -> list[dict[str, object]]:
    path = PROCESSED_DIR / "chunks.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
