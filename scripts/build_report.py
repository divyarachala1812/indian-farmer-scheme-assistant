from __future__ import annotations

import json
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "Indian_Farmer_Scheme_Assistant_Report.pdf"
METRICS_PATH = ROOT / "reports" / "retrieval_evaluation.json"
SAMPLES_PATH = ROOT / "reports" / "sample_answers.json"

NAVY = colors.HexColor("#12372A")
GREEN = colors.HexColor("#2A9D6F")
SAFFRON = colors.HexColor("#F4A261")
LIGHT = colors.HexColor("#EDF5EF")
INK = colors.HexColor("#26352E")
MUTED = colors.HexColor("#62736B")

BASE = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "CoverTitle",
    parent=BASE["Title"],
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=34,
    textColor=colors.white,
    alignment=TA_CENTER,
    spaceAfter=18,
)
SUBTITLE = ParagraphStyle(
    "CoverSubtitle",
    parent=BASE["BodyText"],
    fontName="Helvetica",
    fontSize=13,
    leading=19,
    textColor=colors.HexColor("#D7E7DE"),
    alignment=TA_CENTER,
)
H1 = ParagraphStyle(
    "PageTitle",
    parent=BASE["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    textColor=NAVY,
    spaceAfter=12,
)
H2 = ParagraphStyle(
    "SectionTitle",
    parent=BASE["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=GREEN,
    spaceBefore=6,
    spaceAfter=6,
)
BODY = ParagraphStyle(
    "Body",
    parent=BASE["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13.5,
    textColor=INK,
    spaceAfter=8,
)
SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=8.2,
    leading=10.5,
    textColor=MUTED,
)
CODE = ParagraphStyle(
    "Code",
    parent=BASE["Code"],
    fontName="Courier",
    fontSize=7.8,
    leading=10.5,
    textColor=INK,
    backColor=LIGHT,
    borderPadding=7,
)


def report_table(rows: list[list[str]], widths: list[float]) -> Table:
    prepared = [[Paragraph(str(cell), SMALL) for cell in row] for row in rows]
    table = Table(prepared, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C9BE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(f"<font color='#2A9D6F'>●</font> {item}", BODY) for item in items]


def evaluation_chart(metrics: dict[str, object]) -> Drawing:
    values = [
        ("Hit@1", float(metrics["hit_at_1"])),
        ("Hit@3", float(metrics["hit_at_3"])),
        ("MRR", float(metrics["mean_reciprocal_rank"])),
        ("Coverage", float(metrics["mean_expected_term_coverage_at_3"])),
        ("Citations", 1.0 if metrics["all_answers_have_citations"] else 0.0),
    ]
    drawing = Drawing(500, 260)
    drawing.add(Rect(0, 0, 500, 260, rx=12, ry=12, fillColor=NAVY, strokeColor=None))
    drawing.add(
        String(24, 226, "Declared retrieval evaluation", fontSize=17, fillColor=colors.white)
    )
    drawing.add(
        String(
            24,
            205,
            "18 questions | 5 scheme areas | 406 indexed chunks",
            fontSize=9.5,
            fillColor=colors.HexColor("#D7E7DE"),
        )
    )
    for index, (label, value) in enumerate(values):
        x = 30 + index * 94
        height = value * 125
        colour = GREEN if value >= 0.99 else SAFFRON
        drawing.add(Rect(x, 48, 60, height, rx=6, ry=6, fillColor=colour, strokeColor=None))
        drawing.add(
            String(
                x + 30,
                184,
                f"{value:.3f}",
                textAnchor="middle",
                fontSize=10,
                fillColor=colors.white,
            )
        )
        drawing.add(
            String(
                x + 30,
                28,
                label,
                textAnchor="middle",
                fontSize=8.5,
                fillColor=colors.white,
            )
        )
    return drawing


def decorate_page(pdf_canvas, doc) -> None:
    page = doc.page
    width, height = A4
    pdf_canvas.saveState()
    if page == 1:
        pdf_canvas.setFillColor(NAVY)
        pdf_canvas.rect(0, 0, width, height, fill=1, stroke=0)
        pdf_canvas.setFillColor(SAFFRON)
        pdf_canvas.rect(28 * mm, height - 45 * mm, 45 * mm, 2.5 * mm, fill=1, stroke=0)
    else:
        pdf_canvas.setFillColor(NAVY)
        pdf_canvas.rect(0, height - 16 * mm, width, 16 * mm, fill=1, stroke=0)
        pdf_canvas.setFillColor(colors.white)
        pdf_canvas.setFont("Helvetica-Bold", 8.5)
        pdf_canvas.drawString(18 * mm, height - 10.5 * mm, "INDIAN FARMER SCHEME ASSISTANT")
        pdf_canvas.setFillColor(MUTED)
        pdf_canvas.setFont("Helvetica", 8)
        pdf_canvas.drawString(18 * mm, 11 * mm, "Divya Rachala | Data Science Portfolio")
        pdf_canvas.drawRightString(width - 18 * mm, 11 * mm, f"Page {page} of 10")
    pdf_canvas.restoreState()


def build_report() -> Path:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    soil_sample = samples[1]

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=23 * mm,
        bottomMargin=18 * mm,
        title="Indian Farmer Scheme Assistant",
        author="Divya Rachala",
        subject="Applied AI and information retrieval portfolio project report",
    )
    story = []

    story.extend(
        [
            Spacer(1, 62 * mm),
            Paragraph("Indian Farmer<br/>Scheme Assistant", TITLE),
            Paragraph(
                "Citation-grounded retrieval over official Indian agriculture sources",
                SUBTITLE,
            ),
            Spacer(1, 25 * mm),
            report_table(
                [
                    ["Portfolio summary", "Verified result"],
                    ["Corpus", "406 chunks from seven official source items"],
                    ["Coverage", "PM-KISAN, PMFBY, Soil Health Card, e-NAM, KCC"],
                    ["Evaluation", "18 questions | Hit@1 1.000 | Citation completeness 100%"],
                    ["Author", "Divya Rachala | August 2026"],
                ],
                [48 * mm, 100 * mm],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Executive brief", H1),
            Paragraph(
                "Official farmer-scheme information is distributed across ministry PDFs, programme portals, FAQs, and RBI circulars. This project creates a compact evidence-first assistant that retrieves a relevant official passage and keeps the source visible.",
                BODY,
            ),
            report_table(
                [
                    ["Design choice", "Reason"],
                    ["Official-source registry", "Limits the corpus to traceable publishers"],
                    [
                        "Hybrid lexical retrieval",
                        "Balances exact policy phrases and spelling variation",
                    ],
                    ["Extractive answers", "Reduces unsupported paraphrasing of financial rules"],
                    ["Page-aware citations", "Lets a reviewer inspect the supporting passage"],
                    ["Mandatory warning", "Reminds users to verify current rules and deadlines"],
                ],
                [48 * mm, 100 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph("Portfolio value", H2),
            *bullets(
                [
                    "Demonstrates document ingestion, retrieval, evaluation, and safety design.",
                    "Handles English, Hindi, and Hinglish test queries within a declared scope.",
                    "Reports a small curated test honestly rather than claiming general accuracy.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Problem, scope, and intended users", H1),
            Paragraph(
                "The assistant supports source discovery and passage retrieval. It does not decide eligibility, submit an application, recommend a loan or insurance product, or replace the latest official portal.",
                BODY,
            ),
            report_table(
                [
                    ["Scheme area", "Indexed official material"],
                    ["PM-KISAN", "Revised operational guidelines"],
                    ["PMFBY", "Revised crop-insurance operational guidelines"],
                    ["Soil Health Card", "Official FAQs on cycle, parameters, and sampling"],
                    ["e-NAM", "Government of India market explainer"],
                    ["Kisan Credit Card", "Reserve Bank of India master circular"],
                ],
                [48 * mm, 100 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Primary users", H2),
            *bullets(
                [
                    "A farmer or student locating the official source for a scheme question.",
                    "A reviewer checking how citations and safety controls are implemented.",
                    "A hiring manager assessing applied NLP and retrieval fundamentals.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Source corpus and provenance", H1),
            Paragraph(
                "The source manifest stores a stable ID, title, publisher, URL, and document type for every item. Acquisition records a SHA-256 checksum. Raw documents and extracted chunks remain local so the repository does not redistribute full government publications.",
                BODY,
            ),
            report_table(
                [
                    ["Control", "Implementation"],
                    ["Publisher boundary", "Ministries, programme portals, PIB, and RBI"],
                    ["Version trace", "Source title and URL stored in a versioned manifest"],
                    ["Acquisition trace", "Checksum recorded after download"],
                    ["Page lineage", "PDF page number retained on every extracted chunk"],
                    ["Repository size", "Raw documents and trained index are ignored and rebuilt"],
                ],
                [48 * mm, 100 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph(
                "Source freshness remains a risk. Rebuilding refreshes documents, but the user must still verify publication dates, eligibility, amounts, and deadlines on the cited portal.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Ingestion, extraction, and chunking", H1),
            report_table(
                [
                    ["Stage", "Method", "Output"],
                    ["Acquire", "Download from manifest and hash", "Local raw file and checksum"],
                    ["Extract PDF", "Read page by page", "Text with page metadata"],
                    [
                        "Extract HTML",
                        "Remove scripts and presentation elements",
                        "Main content text",
                    ],
                    ["Normalise", "Collapse whitespace and clean boilerplate", "Consistent text"],
                    ["Chunk", "About 1,100 characters with overlap", "406 evidence chunks"],
                ],
                [36 * mm, 67 * mm, 45 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Engineering lessons", H2),
            *bullets(
                [
                    "A dynamic e-NAM page returned navigation rather than the visible FAQ content.",
                    "A broad HTML cleanup rule initially removed RBI content wrapped in a form.",
                    "Per-source chunk counts exposed both ingestion problems before evaluation.",
                    "A static PIB explainer and a targeted RBI content selector corrected the corpus.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Hybrid retrieval and answer composition", H1),
            report_table(
                [
                    ["Component", "Configuration", "Role"],
                    [
                        "Word TF-IDF",
                        "Unigrams and bigrams, 68% weight",
                        "Exact scheme and policy phrases",
                    ],
                    [
                        "Character TF-IDF",
                        "3-5 character n-grams, 32% weight",
                        "Spelling and mixed-language robustness",
                    ],
                    [
                        "Query expansion",
                        "Transparent Hindi and Hinglish dictionary",
                        "Domain term bridging",
                    ],
                    ["Sentence ranker", "Question-to-sentence TF-IDF", "Select concise evidence"],
                    [
                        "Answer contract",
                        "At most two statements plus citations",
                        "Traceable output",
                    ],
                ],
                [38 * mm, 57 * mm, 53 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Why extractive", H2),
            Paragraph(
                "For benefit amounts, premiums, eligibility, and credit guidance, a fluent unsupported answer is more harmful than a short official excerpt. The current design keeps every factual answer attached to inherited source metadata.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Evaluation design and results", H1),
            Paragraph(
                "The declared set contains 18 source-labelled questions across five scheme areas, including two Hindi questions and one Hinglish question. Each item has an expected source and evidence terms.",
                BODY,
            ),
            evaluation_chart(metrics),
            Spacer(1, 5 * mm),
            Paragraph(
                "The expected official source ranks first for every declared question. Expected-term coverage is 0.972 because PDF extraction and chunk boundaries can separate a phrase even when the correct page is retrieved. The test is curated and does not establish general question-answering accuracy.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    answer_text = soil_sample["answer"].replace("\n", "\n")
    story.extend(
        [
            Paragraph("Citation-grounded answer example", H1),
            Paragraph(f"<b>Question:</b> {soil_sample['query']}", BODY),
            Preformatted(answer_text, CODE),
            Spacer(1, 6 * mm),
            report_table(
                [
                    ["Citation field", "Example"],
                    ["Source", soil_sample["citations"][0]["title"]],
                    ["Publisher", soil_sample["citations"][0]["publisher"]],
                    ["URL", soil_sample["citations"][0]["url"]],
                ],
                [40 * mm, 108 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                "The assistant returns a supported passage, source metadata, and a freshness warning. It does not request Aadhaar, banking details, land records, or personal eligibility profiles.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Limitations and responsible use", H1),
            report_table(
                [
                    ["Limitation", "Effect", "Improvement"],
                    [
                        "Small source set",
                        "Cannot answer every scheme question",
                        "Add governed sources",
                    ],
                    [
                        "Curated test",
                        "Metrics may overstate general performance",
                        "Independent evaluation",
                    ],
                    ["Lexical retrieval", "May miss semantic paraphrases", "Compare embeddings"],
                    ["No confidence threshold", "Weak matches may still return", "Add abstention"],
                    ["Policy freshness", "Rules can change", "Version monitoring"],
                    ["PDF tables", "Extracted rows can be dense", "Structured table parsing"],
                ],
                [38 * mm, 57 * mm, 53 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Responsible-use boundary", H2),
            *bullets(
                [
                    "Do not treat an answer as an eligibility or approval decision.",
                    "Do not use the assistant as legal, financial, or insurance advice.",
                    "Always verify current amounts, dates, and application steps at the cited source.",
                    "Do not claim broad multilingual understanding from three cross-script test items.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Reproducibility, evidence, and interview value", H1),
            report_table(
                [
                    ["Step", "Command or artifact"],
                    ["Environment", "uv sync"],
                    ["Build corpus", "uv run python scripts/build_knowledge_base.py"],
                    ["Evaluate", "uv run python scripts/evaluate_retrieval.py"],
                    ["Create examples", "uv run python scripts/demo_queries.py"],
                    ["Verify", "uv run pytest -q and uv run ruff check ."],
                    ["Evidence", "reports/retrieval_evaluation.json and sample_answers.json"],
                ],
                [42 * mm, 106 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph("Skills demonstrated", H2),
            *bullets(
                [
                    "Official-source acquisition, checksums, PDF and HTML extraction, and chunking.",
                    "NLP vectorisation, hybrid ranking, mixed-language query handling, and citations.",
                    "Retrieval evaluation, error analysis, tests, packaging, and safety documentation.",
                ]
            ),
            Paragraph("Primary official publishers", H2),
            *bullets(
                [
                    "Ministry of Agriculture and Farmers Welfare and programme portals.",
                    "Press Information Bureau, Government of India.",
                    "Reserve Bank of India.",
                ]
            ),
        ]
    )

    doc.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return OUTPUT


if __name__ == "__main__":
    build_report()
