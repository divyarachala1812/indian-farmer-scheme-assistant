from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_project_assets_exist() -> None:
    required = [
        "README.md",
        "docs/architecture.md",
        "docs/evaluation.md",
        "docs/safety.md",
        "reports/figures/retrieval_evaluation.svg",
        "reports/KrishiGuide_Report.pdf",
        "reports/retrieval_evaluation.json",
        "reports/sample_answers.json",
        "scripts/create_readme_figure.py",
        "scripts/build_report.py",
    ]
    assert all((ROOT / path).exists() for path in required)
