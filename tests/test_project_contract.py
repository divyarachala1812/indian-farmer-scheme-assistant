from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_portfolio_assets_exist() -> None:
    required = [
        "README.md",
        "docs/architecture.md",
        "docs/evaluation.md",
        "docs/safety.md",
        "reports/figures/retrieval_evaluation.svg",
        "reports/Indian_Farmer_Scheme_Assistant_Report.pdf",
        "reports/retrieval_evaluation.json",
        "reports/sample_answers.json",
        "scripts/create_readme_figure.py",
        "scripts/build_report.py",
    ]
    assert all((ROOT / path).exists() for path in required)
