from __future__ import annotations

import json

from schemeguide.assistant import SchemeAssistant
from schemeguide.config import EVALUATION_FILE, REPORTS_DIR
from schemeguide.retrieval import HybridRetriever


def evaluate(retriever: HybridRetriever) -> dict[str, object]:
    questions = json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))
    assistant = SchemeAssistant(retriever)
    results = []
    reciprocal_ranks = []
    hit_at_1 = 0
    hit_at_3 = 0
    term_coverages = []

    for item in questions:
        hits = retriever.search(item["query"], top_k=5)
        source_ids = [str(hit.chunk["source_id"]) for hit in hits]
        try:
            rank = source_ids.index(item["expected_source"]) + 1
            reciprocal_rank = 1 / rank
        except ValueError:
            rank = None
            reciprocal_rank = 0.0
        hit_at_1 += int(rank == 1)
        hit_at_3 += int(rank is not None and rank <= 3)
        reciprocal_ranks.append(reciprocal_rank)

        retrieved_text = " ".join(str(hit.chunk["text"]).lower() for hit in hits[:3])
        terms = [term.lower() for term in item["expected_terms"]]
        coverage = sum(term in retrieved_text for term in terms) / len(terms)
        term_coverages.append(coverage)
        answer = assistant.answer(item["query"])
        results.append(
            {
                "id": item["id"],
                "query": item["query"],
                "expected_source": item["expected_source"],
                "retrieved_sources": source_ids,
                "expected_source_rank": rank,
                "term_coverage_at_3": coverage,
                "citation_count": len(answer.citations),
            }
        )

    count = len(questions)
    summary: dict[str, object] = {
        "question_count": count,
        "hit_at_1": hit_at_1 / count,
        "hit_at_3": hit_at_3 / count,
        "mean_reciprocal_rank": sum(reciprocal_ranks) / count,
        "mean_expected_term_coverage_at_3": sum(term_coverages) / count,
        "all_answers_have_citations": all(result["citation_count"] > 0 for result in results),
        "results": results,
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "retrieval_evaluation.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary
