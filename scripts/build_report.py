from __future__ import annotations

import json
from pathlib import Path

from report_template import build_research_report

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "KrishiGuide_Report.pdf"
FIGURES = ROOT / "reports" / "figures"


def build_report() -> Path:
    metrics = json.loads((ROOT / "reports/retrieval_evaluation.json").read_text())
    sections = [
        {
            "title": "Project overview and problem statement",
            "paragraphs": [
                "KrishiGuide is a citation-grounded information retrieval assistant for major farmer schemes. I built it because important details are distributed across ministry PDFs, programme pages, FAQs, and an RBI circular, while ordinary search results may hide the exact supporting passage.",
                "The system retrieves evidence and returns extractive answers with visible source metadata. It does not determine eligibility, approve an application, recommend credit or insurance, or guarantee that a historical document remains current.",
            ],
        },
        {
            "title": "Official source collection",
            "paragraphs": [
                "The knowledge base contains seven declared source items covering PM-KISAN, PMFBY crop insurance, three Soil Health Card FAQ topics, e-NAM, and Kisan Credit Card. Every item records a stable ID, title, official publisher, URL, and format.",
                "PDF pages retain page numbers. HTML pages are cleaned before extraction. Files are downloaded locally, hashed, and excluded from Git; the versioned source registry allows the collection to be rebuilt.",
            ],
            "table": [
                ["Area", "Official material"],
                ["PM-KISAN", "Revised operational guidelines"],
                ["PMFBY", "Revised operational guidelines"],
                ["Soil Health Card", "Issue cycle, parameters, and sampling FAQs"],
                ["e-NAM", "Government explainer"],
                ["Kisan Credit Card", "RBI master circular"],
            ],
        },
        {
            "title": "Retrieval and answer method",
            "paragraphs": [
                "Extracted text is divided into overlapping page-aware chunks. The retriever combines word TF-IDF for exact scheme language and character TF-IDF for spelling variation, Hindi script, and Hinglish. Scores are combined using a documented 68 percent word and 32 percent character weight.",
                "A transparent query-expansion dictionary covers selected Hindi and Hinglish scheme terms. The top chunks are split into sentences, ranked again for relevance, and used to compose at most two evidence statements. Every factual statement inherits citation metadata and every answer ends with a current-source verification warning.",
            ],
        },
        {
            "title": "Evaluation design",
            "paragraphs": [
                "The declared test set contains 18 inspectable questions: three each for PM-KISAN, PMFBY, Soil Health Card, e-NAM, and Kisan Credit Card, plus two Hindi questions and one Hinglish question that repeat important intents.",
                "Each question specifies an expected source and two expected evidence terms. I measure Hit@1, Hit@3, mean reciprocal rank, expected-term coverage in the top three chunks, and citation completeness. This is a curated project test, not a general benchmark.",
            ],
        },
        {
            "title": "End-to-end retrieval architecture",
            "paragraphs": [
                "The architecture keeps official-source acquisition, page-aware ingestion, indexing, retrieval and answer construction as separate stages. Each source item retains its URL, checksum and page metadata before it enters the searchable index.",
                "Python extractors create 406 chunks. Word and character retrieval identify evidence passages, while the bounded answer step selects short statements and attaches the originating source and page. The answer stage cannot create a citation that was not present in retrieved evidence.",
            ],
            "figure": FIGURES / "06_architecture.png",
            "caption": "Architecture evidence. KrishiGuide source, index, retrieval and citation stages.",
            "explanation": [
                ["Technology flow", "Official PDF and HTML sources pass through Python extraction, hybrid ranking and a bounded citation template."],
                ["Traceability", "Every returned statement is connected to a source item and page-aware chunk."],
                ["Safety boundary", "Eligibility, deadlines and application decisions remain outside the assistant and require current official confirmation."],
            ],
        },
        {
            "title": "Automated retrieval test execution",
            "paragraphs": [
                "I ran the current repository test suite after the report update. Six tests passed. The tests cover citation formatting, source ranking, empty-query handling, answer boundaries and required project assets.",
                "The automated suite is different from the 18-question retrieval evaluation. Unit tests verify software contracts, while Hit@1, term coverage and citation completeness measure the declared information-retrieval scenarios.",
            ],
            "figure": FIGURES / "07_test_execution.png",
            "caption": "Test evidence. Actual KrishiGuide pytest execution for retrieval and answer contracts.",
            "explanation": [
                ["Execution", "Six tests passed in 1.60 seconds and no test failed."],
                ["Negative scenario", "An empty or unsupported query must return a safe bounded response instead of invented scheme detail."],
                ["Combined evidence", "The unit suite and 18-question evaluation address different risks and are reported separately."],
            ],
        },
        {
            "title": "Experiment 1: overall retrieval metrics",
            "figure": FIGURES / "01_retrieval_metrics.png",
            "caption": "Figure 1. Retrieval and citation metrics across the 18-question evaluation.",
            "explanation": [
                [
                    "What I tested",
                    "Whether the correct official source is retrieved early, whether expected evidence terms appear, and whether answers contain citations.",
                ],
                [
                    "What the graph shows",
                    "Hit@1, Hit@3 and MRR are 1.000; expected-term coverage is 0.972; all evaluated answers contain citations.",
                ],
                [
                    "Conclusion",
                    "The system works reliably on the declared test set, but the small curated scope prevents broad accuracy claims.",
                ],
            ],
        },
        {
            "title": "Experiment 2: question-level term coverage",
            "figure": FIGURES / "02_question_coverage.png",
            "caption": "Figure 2. Expected-term coverage for each declared evaluation question.",
            "explanation": [
                [
                    "What I tested",
                    "Whether the top three chunks contain both expected answer concepts for every question.",
                ],
                [
                    "What the graph shows",
                    "Seventeen questions reached full coverage; the KCC eligibility question reached 0.50 even though the correct source ranked first.",
                ],
                [
                    "Conclusion",
                    "Retrieval rank alone is insufficient. The partial case identifies chunk boundaries and extraction wording as an improvement area.",
                ],
            ],
        },
        {
            "title": "Experiment 3: source coverage",
            "figure": FIGURES / "03_source_distribution.png",
            "caption": "Figure 3. Number of evaluation questions associated with each official source item.",
            "explanation": [
                [
                    "What I tested",
                    "Whether evaluation covers the complete declared knowledge base rather than a single strong scheme.",
                ],
                [
                    "What the graph shows",
                    "All seven source items are represented, with three broader question groups for PM-KISAN, PMFBY, e-NAM, and KCC.",
                ],
                [
                    "Conclusion",
                    "The results reflect multiple scheme areas, although more independently written questions are still required.",
                ],
            ],
        },
        {
            "title": "Experiment 4: citation completeness",
            "figure": FIGURES / "04_citation_counts.png",
            "caption": "Figure 4. Citation counts returned by the evaluated answers.",
            "explanation": [
                [
                    "What I tested",
                    "Whether any evaluated factual answer can be produced without source metadata.",
                ],
                [
                    "What the graph shows",
                    "Every answer contains at least one citation, and several answers contain two cited evidence statements.",
                ],
                [
                    "Conclusion",
                    "The citation contract passes for this evaluation; factual output remains traceable to official material.",
                ],
            ],
        },
        {
            "title": "Experiment 5: rank and language stress checks",
            "figure": FIGURES / "05_rank_language_checks.png",
            "caption": "Figure 5. Expected-source rank and language composition of the evaluation set.",
            "explanation": [
                [
                    "What I tested",
                    "Whether the correct source remains first for English, Hindi, and Hinglish queries.",
                ],
                [
                    "What the graph shows",
                    "All 18 questions rank the expected source first, including two Hindi and one Hinglish case.",
                ],
                [
                    "Conclusion",
                    "Character features and transparent expansion help these examples, but three non-English questions are not evidence of general multilingual understanding.",
                ],
            ],
        },
        {
            "title": "Results, error analysis and safety",
            "paragraphs": [
                f"The final evaluation reports Hit@1 {metrics['hit_at_1']:.3f}, Hit@3 {metrics['hit_at_3']:.3f}, MRR {metrics['mean_reciprocal_rank']:.3f}, and expected-term coverage {metrics['mean_expected_term_coverage_at_3']:.3f}. Every evaluated answer contains at least one citation.",
                "During development, dynamic e-NAM pages returned navigation text and the RBI page lost its main content when form elements were removed too broadly. Replacing the e-NAM source with a static government PDF and narrowing RBI cleanup corrected these ingestion failures. These examples show why source extraction must be tested separately from retrieval.",
                "Scheme rules can change. Answers are evidence-navigation aids and must be checked against the latest official portal before any decision.",
            ],
        },
        {
            "title": "Reproducibility, limitations and future work",
            "paragraphs": [
                "The repository versions the source registry, evaluation questions, retrieval configuration, metrics, sample answers, tests, and report. Raw documents, extracted chunks, and the model index are rebuilt locally to avoid redistributing full source documents.",
                "The evaluation is small, source-specific, and written by the project author. A stronger next version would include independently written paraphrases, unanswerable questions, outdated-policy traps, adversarial prompts, more Indian languages, confidence-based abstention, and manual grading of answer support.",
            ],
        },
        {
            "title": "Conclusion",
            "paragraphs": [
                "I built KrishiGuide to make the source visible rather than to produce unsupported advice. The project demonstrates official-source acquisition, page-aware extraction, hybrid retrieval, lightweight multilingual handling, extractive response composition, citations, and measurable evaluation. Its strongest contribution is the combination of useful retrieval with an explicit boundary: the assistant supports research, while eligibility and financial decisions remain with current official channels."
            ],
        },
    ]
    return build_research_report(
        OUTPUT,
        "KrishiGuide Scheme Assistant",
        "Divya Rachala",
        [
            "This report describes a citation-grounded retrieval assistant for official information about PM-KISAN, PMFBY, Soil Health Card, e-NAM, and Kisan Credit Card. I created a rebuildable knowledge base from seven official source items, combined word- and character-level retrieval, added transparent Hindi and Hinglish query expansion, and composed short extractive answers with citations.",
            "On a declared 18-question test set, the expected source ranked first for every question, expected-term coverage in the top three chunks was 0.972, and every evaluated answer included a citation. Five experiments examine aggregate retrieval, question-level coverage, source representation, citation completeness, and language stress cases.",
        ],
        "information retrieval; farmer schemes; official sources; citations; Hindi and Hinglish queries",
        sections,
    )


if __name__ == "__main__":
    print(build_report())
