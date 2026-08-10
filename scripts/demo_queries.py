import json
from pathlib import Path

from schemeguide.assistant import SchemeAssistant
from schemeguide.config import REPORTS_DIR
from schemeguide.retrieval import HybridRetriever

QUERIES = [
    "What premium does a farmer pay for Kharif crops under PMFBY?",
    "How often does a farmer receive a Soil Health Card?",
    "mandi me online bechne ke liye eNAM kya hai?",
    "What is the purpose of a Kisan Credit Card?",
]


if __name__ == "__main__":
    assistant = SchemeAssistant(HybridRetriever.load())
    outputs = []
    for query in QUERIES:
        result = assistant.answer(query)
        outputs.append(
            {
                "query": query,
                "answer": result.text,
                "citations": result.citations,
            }
        )
    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "sample_answers.json").write_text(
        json.dumps(outputs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {len(outputs)} citation-grounded examples")
