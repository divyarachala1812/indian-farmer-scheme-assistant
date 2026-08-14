from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "figures"
WIDTH, HEIGHT = 1600, 900
BLACK = "#111111"
GREY = "#666666"
LIGHT = "#d9d9d9"
MID = "#8a8a8a"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else FONT, size)


def canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    draw.text((90, 55), title, fill=BLACK, font=font(42, True))
    draw.text((90, 112), subtitle, fill=GREY, font=font(24))
    draw.line((90, 158, WIDTH - 90, 158), fill=BLACK, width=2)
    return image, draw


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int = 23) -> None:
    draw.text(xy, text, fill=BLACK, font=font(size))


def save(image: Image.Image, name: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / name, quality=95)


def overall_metrics(metrics: dict) -> None:
    values = [
        ("Hit@1", metrics["hit_at_1"]),
        ("Hit@3", metrics["hit_at_3"]),
        ("MRR", metrics["mean_reciprocal_rank"]),
        ("Term coverage", metrics["mean_expected_term_coverage_at_3"]),
        ("Cited answers", 1.0 if metrics["all_answers_have_citations"] else 0.0),
    ]
    image, draw = canvas(
        "Retrieval evaluation metrics",
        f"Declared test set: {metrics['question_count']} questions; higher is better",
    )
    baseline, chart_height = 750, 480
    for index, (name, value) in enumerate(values):
        left = 145 + index * 285
        top = baseline - int(value * chart_height)
        draw.rectangle((left, top, left + 145, baseline), outline=BLACK, fill="#bdbdbd", width=2)
        draw.text(
            (left + 72, top - 48), f"{value:.3f}", anchor="mm", fill=BLACK, font=font(25, True)
        )
        draw.text((left + 72, baseline + 35), name, anchor="mm", fill=BLACK, font=font(22))
    draw.line((105, baseline, WIDTH - 90, baseline), fill=BLACK, width=2)
    save(image, "01_retrieval_metrics.png")


def coverage_by_question(metrics: dict) -> None:
    results = metrics["results"]
    image, draw = canvas(
        "Expected-term coverage by question",
        "Coverage in the top three retrieved chunks; q15 is the only partial match",
    )
    left, top, cell_w, cell_h = 105, 235, 235, 120
    for index, result in enumerate(results):
        row, column = divmod(index, 6)
        x, y = left + column * cell_w, top + row * (cell_h + 75)
        value = float(result["term_coverage_at_3"])
        fill = "#bdbdbd" if value == 1 else "#efefef"
        draw.rectangle((x, y, x + 185, y + cell_h), fill=fill, outline=BLACK, width=2)
        draw.text((x + 92, y + 38), result["id"], anchor="mm", fill=BLACK, font=font(22, True))
        draw.text((x + 92, y + 82), f"{value:.2f}", anchor="mm", fill=BLACK, font=font(29))
    label(
        draw,
        (105, 810),
        "17 questions reached full term coverage; q15 reached 0.50 despite retrieving the correct source first.",
        22,
    )
    save(image, "02_question_coverage.png")


def source_test_distribution(metrics: dict) -> None:
    counts = Counter(result["expected_source"] for result in metrics["results"])
    display = {
        "pm_kisan": "PM-KISAN",
        "pmfby": "PMFBY",
        "soil_health_frequency": "Soil Health Card: cycle",
        "soil_health_parameters": "Soil Health Card: parameters",
        "soil_health_sampling": "Soil Health Card: sampling",
        "enam": "e-NAM",
        "kcc": "Kisan Credit Card",
    }
    items = [(display[key], value) for key, value in counts.items()]
    image, draw = canvas(
        "Evaluation coverage by official source",
        "Question counts show which source areas are represented in the declared evaluation",
    )
    max_value = max(value for _, value in items)
    for index, (name, value) in enumerate(items):
        y = 215 + index * 82
        bar_width = int(value / max_value * 720)
        draw.text((105, y + 17), name, fill=BLACK, font=font(22))
        draw.rectangle((535, y, 535 + bar_width, y + 48), fill="#bdbdbd", outline=BLACK, width=2)
        draw.text((555 + bar_width, y + 8), str(value), fill=BLACK, font=font(24, True))
    label(
        draw,
        (105, 810),
        "The test set covers all seven indexed source items rather than reporting only one scheme.",
        22,
    )
    save(image, "03_source_distribution.png")


def citation_counts(metrics: dict) -> None:
    counts = Counter(int(result["citation_count"]) for result in metrics["results"])
    image, draw = canvas(
        "Citation completeness test",
        "Number of citations returned by each evaluated answer",
    )
    values = sorted(counts.items())
    baseline = 730
    for index, (citation_count, answers) in enumerate(values):
        left = 340 + index * 430
        height = answers * 30
        draw.rectangle(
            (left, baseline - height, left + 220, baseline), fill="#bdbdbd", outline=BLACK, width=2
        )
        draw.text(
            (left + 110, baseline - height - 45),
            str(answers),
            anchor="mm",
            fill=BLACK,
            font=font(29, True),
        )
        draw.text(
            (left + 110, baseline + 45),
            f"{citation_count} citation{'s' if citation_count != 1 else ''}",
            anchor="mm",
            fill=BLACK,
            font=font(24),
        )
    label(
        draw,
        (105, 820),
        "Every evaluated answer included at least one official-source citation; no uncited answer was observed.",
        22,
    )
    save(image, "04_citation_counts.png")


def rank_and_language(metrics: dict) -> None:
    results = metrics["results"]
    language = {"English": 0, "Hindi": 0, "Hinglish": 0}
    for result in results:
        query = result["query"]
        if any("\u0900" <= character <= "\u097f" for character in query):
            language["Hindi"] += 1
        elif result["id"] == "q18":
            language["Hinglish"] += 1
        else:
            language["English"] += 1
    image, draw = canvas(
        "Rank and language stress checks",
        "The expected source ranked first for every question, including Hindi and Hinglish cases",
    )
    draw.rectangle((105, 230, 735, 640), outline=BLACK, width=2)
    draw.text((420, 290), "Expected-source rank", anchor="mm", fill=BLACK, font=font(30, True))
    draw.text((420, 405), "18 / 18", anchor="mm", fill=BLACK, font=font(72, True))
    draw.text(
        (420, 505),
        "questions ranked the correct source first",
        anchor="mm",
        fill=GREY,
        font=font(24),
    )
    x = 920
    for name, value in language.items():
        draw.text((x, 260), name, anchor="mm", fill=BLACK, font=font(24, True))
        height = value * 24
        draw.rectangle((x - 80, 650 - height, x + 80, 650), fill="#bdbdbd", outline=BLACK, width=2)
        draw.text((x, 690), str(value), anchor="mm", fill=BLACK, font=font(28))
        x += 250
    label(
        draw,
        (105, 815),
        "The language sample is intentionally small: 15 English, 2 Hindi and 1 Hinglish question.",
        22,
    )
    save(image, "05_rank_language_checks.png")


def main() -> None:
    metrics = json.loads((ROOT / "reports" / "retrieval_evaluation.json").read_text())
    overall_metrics(metrics)
    coverage_by_question(metrics)
    source_test_distribution(metrics)
    citation_counts(metrics)
    rank_and_language(metrics)
    print("Wrote five evaluation figures")


if __name__ == "__main__":
    main()
