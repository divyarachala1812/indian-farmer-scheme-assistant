.PHONY: setup ingest evaluate demo test lint all

setup:
	uv sync

ingest:
	uv run python scripts/build_knowledge_base.py

evaluate:
	uv run python scripts/evaluate_retrieval.py

demo:
	uv run python scripts/demo_queries.py

test:
	uv run pytest -q

lint:
	uv run ruff check .

all: ingest evaluate demo test lint
