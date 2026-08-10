# Project report

## 1. Problem

Official farmer-scheme information is spread across ministries, programme portals, PDFs, FAQs, and circulars. Search engines can locate pages, but a user still has to identify the relevant passage and determine whether the information came from an official source.

The project creates a compact evidence-first assistant for five scheme areas. The goal is navigation and traceability, not automatic eligibility advice.

## 2. Scope

The corpus covers PM-KISAN income support, PMFBY crop insurance, Soil Health Card information, e-NAM agricultural markets, and Kisan Credit Card guidance. The source registry contains seven official items because three narrow Soil Health Card FAQ pages are indexed separately.

## 3. Data pipeline

The ingestion script downloads each source, records its checksum, extracts PDF or HTML text, and creates page-aware overlapping chunks. The current build indexes 406 chunks. The full documents and index are reproducible local artifacts rather than committed repository files.

## 4. Retrieval approach

Word n-grams capture scheme names and exact policy phrases. Character n-grams improve robustness to spelling variants, abbreviations, and mixed-language queries. A weighted score combines both representations. A small query-expansion dictionary adds transparent domain translations rather than pretending to provide general multilingual language understanding.

## 5. Answer approach

The assistant retrieves four chunks, ranks their sentences for the question, removes common webpage boilerplate, and returns no more than two evidence statements. Each statement is linked to the inherited source metadata. This is closer to a grounded research assistant than an open-ended chatbot.

## 6. Evaluation

On 18 declared questions, the expected official source ranks first in every case. Hit@3 and MRR are also 1.000, expected-term coverage@3 is 0.972, and every answer contains citations. The test includes Hindi and Hinglish examples but remains too small to support a claim of broad multilingual coverage.

## 7. Engineering lessons

Source ingestion was harder than the retrieval model. A dynamic e-NAM page did not include its visible FAQ content in the downloaded HTML, and a broad HTML cleanup rule removed the RBI page because the site wrapped its content in a form. Inspecting raw acquisition artifacts and per-source chunk counts was necessary to detect both issues.

## 8. Limitations

PDF table extraction can produce dense text. The assistant has no learned semantic embedding model, confidence calibration, contradiction detection, or generative explanation layer. The source set is intentionally small, and rules can become outdated.

## 9. Next version

A stronger version would add independent evaluation questions, semantic embeddings, an abstention threshold, document-version comparison, more Indian languages, structured eligibility fields, and a constrained language model that is allowed to answer only when every statement is entailed by retrieved passages.

## 10. Skills demonstrated

The project shows document acquisition, PDF and HTML parsing, checksum provenance, chunking, NLP vectorisation, hybrid ranking, cross-script query handling, extractive answer composition, citation design, retrieval evaluation, error analysis, testing, packaging, and safety documentation.
