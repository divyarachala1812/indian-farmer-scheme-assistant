from __future__ import annotations

import re
from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from schemeguide.config import MODEL_DIR

QUERY_EXPANSIONS = {
    "किसान": "farmer beneficiary",
    "योजना": "scheme programme",
    "फसल": "crop",
    "बीमा": "insurance premium PMFBY",
    "खरीफ": "kharif",
    "प्रीमियम": "premium",
    "मिट्टी": "soil soil health card",
    "जांच": "test sample",
    "कार्ड": "card",
    "साल": "years cycle",
    "मंडी": "mandi market e-NAM",
    "ऋण": "loan credit KCC",
    "कर्ज": "loan credit KCC",
    "किस्त": "instalment payment",
    "bima": "insurance PMFBY",
    "kharif": "kharif crop",
    "mitti": "soil health card",
    "mandi": "market e-NAM",
    "bechne": "selling produce",
    "kcc": "Kisan Credit Card RBI agriculture credit farmers",
    "parameters": "12 parameters nutrients pH EC OC",
    "transferred": "Direct Benefit Transfer DBT bank accounts PFMS",
    "money": "Direct Benefit Transfer DBT bank accounts PFMS",
}


def expand_query(query: str) -> str:
    additions = [value for key, value in QUERY_EXPANSIONS.items() if key.lower() in query.lower()]
    return f"{query} {' '.join(additions)}".strip()


@dataclass
class SearchHit:
    rank: int
    score: float
    chunk: dict[str, object]


class HybridRetriever:
    def __init__(self, chunks: list[dict[str, object]]) -> None:
        self.chunks = chunks
        documents = [f"{chunk['title']}\n{chunk['text']}" for chunk in chunks]
        self.word_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_df=0.97,
        )
        self.char_vectorizer = TfidfVectorizer(
            lowercase=True,
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            sublinear_tf=True,
        )
        self.word_matrix = self.word_vectorizer.fit_transform(documents)
        self.char_matrix = self.char_vectorizer.fit_transform(documents)

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        expanded = expand_query(query)
        word_query = self.word_vectorizer.transform([expanded])
        char_query = self.char_vectorizer.transform([expanded])
        word_scores = cosine_similarity(word_query, self.word_matrix).ravel()
        char_scores = cosine_similarity(char_query, self.char_matrix).ravel()
        scores = 0.68 * word_scores + 0.32 * char_scores
        order = np.argsort(scores)[::-1][:top_k]
        return [
            SearchHit(rank=rank, score=float(scores[index]), chunk=self.chunks[index])
            for rank, index in enumerate(order, start=1)
        ]

    def save(self) -> None:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, MODEL_DIR / "hybrid_retriever.joblib")

    @classmethod
    def load(cls) -> HybridRetriever:
        return joblib.load(MODEL_DIR / "hybrid_retriever.joblib")


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    for phrase in (
        "Guest User | Sign In",
        "Frequently Asked Question",
        "Please wait... it will take a second!",
    ):
        text = text.replace(phrase, " ")
    candidates = re.split(r"(?<=[.!?])\s+", text)
    cleaned = []
    blocked = ("copyright ©",)
    for candidate in candidates:
        candidate = candidate.strip(" -•")
        if any(term in candidate.lower() for term in blocked):
            continue
        if len(candidate.split()) < 8 or len(candidate) < 45:
            continue
        cleaned.append(candidate)
    return cleaned
