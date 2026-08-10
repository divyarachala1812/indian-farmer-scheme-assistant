from schemeguide.assistant import _normalise_evidence
from schemeguide.ingest import chunk_text
from schemeguide.retrieval import expand_query, split_sentences


def test_chunking_preserves_content_without_runaway_chunks() -> None:
    text = "Sentence about a farmer scheme. " * 120
    chunks = chunk_text(text, size=300, overlap=50)
    assert len(chunks) > 5
    assert all(1 <= len(chunk) <= 302 for chunk in chunks)


def test_hindi_and_hinglish_queries_expand_to_domain_terms() -> None:
    assert "insurance" in expand_query("फसल बीमा premium कितना")
    assert "e-NAM" in expand_query("mandi me online bechne ke liye")


def test_sentence_split_rejects_tiny_fragments() -> None:
    sentences = split_sentences(
        "Short. This is a sufficiently long official sentence about a farmer scheme."
    )
    assert sentences == ["This is a sufficiently long official sentence about a farmer scheme."]


def test_policy_table_row_is_returned_as_readable_evidence() -> None:
    row = (
        "The rate of premium payable by the farmer will be as per Table 1: "
        "Kharif All food grain and Oilseeds crops (Cereals, Millets, Pulses and "
        "Oilseeds crops) 2.0% of SI or Actuarial rate, whichever is less Rabi crops."
    )
    result = _normalise_evidence(row, "What is the Kharif premium?")
    assert result is not None
    assert "2.0% of the sum insured" in result
    assert len(result) < 180


def test_document_header_is_not_used_as_answer_evidence() -> None:
    assert _normalise_evidence("RU-16-01-0215-140423/EXPLAINER National Market", "eNAM") is None
