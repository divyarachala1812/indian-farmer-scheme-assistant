from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "reports" / "retrieval_evaluation.json"
OUTPUT_PATH = ROOT / "reports" / "figures" / "retrieval_evaluation.svg"


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    values = [
        ("Hit@1", float(metrics["hit_at_1"])),
        ("Hit@3", float(metrics["hit_at_3"])),
        ("MRR", float(metrics["mean_reciprocal_rank"])),
        ("Term coverage", float(metrics["mean_expected_term_coverage_at_3"])),
        ("Cited answers", 1.0 if metrics["all_answers_have_citations"] else 0.0),
    ]

    bars = []
    baseline = 540
    max_height = 320
    for index, (label, value) in enumerate(values):
        x = 105 + index * 220
        height = value * max_height
        y = baseline - height
        colour = "#2A9D8F" if value >= 0.99 else "#F4A261"
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="132" height="{height:.1f}" '
            f'rx="12" fill="{colour}"/>'
            f'<text x="{x + 66}" y="{y - 18:.1f}" text-anchor="middle" '
            f'class="value">{value:.3f}</text>'
            f'<text x="{x + 66}" y="580" text-anchor="middle" '
            f'class="label">{label}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#102A2E"/>
      <stop offset="100%" stop-color="#183F43"/>
    </linearGradient>
  </defs>
  <style>
    .title {{ fill: #F5FAF7; font: 700 40px Arial, sans-serif; }}
    .subtitle {{ fill: #C7D8D3; font: 22px Arial, sans-serif; }}
    .value {{ fill: #F5FAF7; font: 700 25px Arial, sans-serif; }}
    .label {{ fill: #E7F0ED; font: 19px Arial, sans-serif; }}
    .note {{ fill: #AFC5BF; font: 17px Arial, sans-serif; }}
  </style>
  <rect width="1280" height="720" rx="24" fill="url(#background)"/>
  <text x="80" y="75" class="title">Retrieval evaluation</text>
  <text x="80" y="112" class="subtitle">18 questions · 5 scheme areas · 406 indexed chunks</text>
  <line x1="80" y1="540" x2="1200" y2="540" stroke="#799792" stroke-width="2"/>
  {"".join(bars)}
  <text x="80" y="660" class="note">Curated project test set; results do not establish general question answering accuracy.</text>
</svg>
"""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
