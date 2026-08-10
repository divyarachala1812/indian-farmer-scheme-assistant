from __future__ import annotations

import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from schemeguide.retrieval import HybridRetriever, SearchHit, expand_query, split_sentences


def _normalise_evidence(sentence: str, query: str) -> str | None:
    """Remove source-page furniture and make extracted policy rows readable."""
    if sentence.startswith("RU-") or "/EXPLAINER" in sentence:
        return None

    sentence = re.sub(
        r"^\d+(?:\.\d+)*\s+Objective\s*/\s*Purpose\s+",
        "",
        sentence,
        flags=re.IGNORECASE,
    )
    if "kharif" in query.lower() and "premium payable by the farmer" in sentence.lower():
        match = re.search(
            r"Kharif\s+All food grain and Oilseeds crops.*?"
            r"(\d+(?:\.\d+)?)%\s+of SI or Actuarial rate, whichever is less",
            sentence,
            flags=re.IGNORECASE,
        )
        if match:
            rate = match.group(1)
            return (
                "For Kharif food-grain and oilseed crops, the farmer's maximum premium "
                f"is {rate}% of the sum insured or the actuarial rate, whichever is lower."
            )
    return sentence


@dataclass
class Answer:
    query: str
    text: str
    citations: list[dict[str, object]]
    retrieval: list[SearchHit]


class SchemeAssistant:
    def __init__(self, retriever: HybridRetriever) -> None:
        self.retriever = retriever

    def answer(self, query: str, top_k: int = 4) -> Answer:
        hits = self.retriever.search(query, top_k=top_k)
        candidates: list[tuple[str, SearchHit]] = []
        for hit in hits:
            for sentence in split_sentences(str(hit.chunk["text"])):
                candidates.append((sentence, hit))

        if not candidates:
            return Answer(
                query=query,
                text="I could not find a supported answer in the indexed official sources.",
                citations=[],
                retrieval=hits,
            )

        sentences = [candidate[0] for candidate in candidates]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        matrix = vectorizer.fit_transform([expand_query(query), *sentences])
        scores = cosine_similarity(matrix[0], matrix[1:]).ravel()
        query_lower = query.lower()
        for position, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            if "premium" in query_lower and "premium payable by the farmer" in sentence_lower:
                scores[position] += 0.30
            if "purpose" in query_lower and "objective / purpose" in sentence_lower:
                scores[position] += 0.30
        ranked = scores.argsort()[::-1]

        selected: list[tuple[str, SearchHit]] = []
        selected_text = ""
        max_statements = (
            1 if any(marker in query_lower for marker in ("what is", "kya hai", "क्या है")) else 2
        )
        best_score = float(scores[ranked[0]]) if len(ranked) else 0.0
        for index in ranked:
            if selected and float(scores[int(index)]) < best_score * 0.55:
                continue
            sentence, hit = candidates[int(index)]
            sentence = _normalise_evidence(sentence, query)
            if sentence is None:
                continue
            if len(sentence.split()[0].strip(".,)")) <= 2 and sentence[0].islower():
                continue
            if len(sentence) > 520:
                query_terms = [
                    term.lower()
                    for term in expand_query(query).split()
                    if len(term) >= 4 and term.isascii()
                ]
                lowered = sentence.lower()
                positions = [lowered.find(term) for term in query_terms if lowered.find(term) >= 0]
                centre = min(positions) if positions else 0
                start = max(0, centre - 80)
                end = min(len(sentence), start + 500)
                start = max(0, end - 500)
                sentence = f"{'…' if start else ''}{sentence[start:end].strip()}{'…' if end < len(sentence) else ''}"
            normalised = sentence.lower()
            if any(
                normalised in existing[0].lower() or existing[0].lower() in normalised
                for existing in selected
            ):
                continue
            if len(selected_text) + len(sentence) > 900:
                continue
            selected.append((sentence, hit))
            selected_text += sentence
            if len(selected) == max_statements:
                break

        citation_keys: dict[tuple[str, int | None], int] = {}
        citations: list[dict[str, object]] = []
        answer_lines = ["The indexed official sources state:"]
        for sentence, hit in selected:
            key = (str(hit.chunk["source_id"]), hit.chunk.get("page"))
            if key not in citation_keys:
                citation_number = len(citations) + 1
                citation_keys[key] = citation_number
                citations.append(
                    {
                        "id": citation_number,
                        "source_id": hit.chunk["source_id"],
                        "title": hit.chunk["title"],
                        "publisher": hit.chunk["publisher"],
                        "page": hit.chunk.get("page"),
                        "url": hit.chunk["url"],
                    }
                )
            answer_lines.append(f"- {sentence} [{citation_keys[key]}]")

        answer_lines.append(
            "Verify current eligibility, amounts, deadlines, and application steps on the linked official portal before acting."
        )
        return Answer(
            query=query,
            text="\n".join(answer_lines),
            citations=citations,
            retrieval=hits,
        )
