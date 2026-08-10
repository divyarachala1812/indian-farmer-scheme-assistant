from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_MANIFEST = ROOT / "data" / "sources" / "source_manifest.json"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
EVALUATION_FILE = ROOT / "data" / "evaluation" / "questions.json"

CHUNK_SIZE = 1100
CHUNK_OVERLAP = 180
