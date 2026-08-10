from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_portfolio_assets_exist() -> None:
    required = [
        "README.md",
        "docs/architecture.md",
        "docs/evaluation.md",
        "docs/safety.md",
        "reports/retrieval_evaluation.json",
        "reports/sample_answers.json",
    ]
    assert all((ROOT / path).exists() for path in required)
