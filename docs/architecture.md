# Architecture

## Design goal

The assistant should help a user find a supported passage quickly while making the source visible. It should not invent an eligibility decision or hide uncertainty behind conversational wording.

## 1. Acquisition

`data/sources/source_manifest.json` is the source registry. Each entry records a stable ID, title, publisher, URL, and document type. The ingestion job downloads each file, computes a SHA-256 digest, and writes a local acquisition manifest.

Raw files and extracted chunks are deliberately ignored by Git. This keeps the repository small and avoids redistributing complete government documents. A reviewer can rebuild the same knowledge base from the versioned source registry.

## 2. Extraction and chunking

PDF pages are extracted with their page number. HTML pages are stripped of scripts and presentation elements before text extraction. Text is normalised and divided into overlapping chunks of approximately 1,100 characters. Each chunk retains:

- chunk ID;
- source ID;
- title and publisher;
- official URL;
- PDF page number when available;
- extracted text.

Overlap reduces the risk of losing a sentence that crosses a chunk boundary.

## 3. Hybrid retrieval

The retriever fits two independent representations:

- word TF-IDF with unigrams and bigrams for precise terms such as “premium payable” or “Direct Benefit Transfer”;
- character TF-IDF with three- to five-character n-grams for spelling variation, abbreviations, Hindi script, and Hinglish.

Cosine similarities are combined as 68% word score and 32% character score. The document title is included during indexing so scheme names remain strong retrieval signals.

## 4. Query expansion

A small transparent dictionary adds domain synonyms for common Hindi and Hinglish terms such as `बीमा`, `मिट्टी`, `मंडी`, `bima`, and `bechne`. Expansions are visible in source code and can be challenged or extended. This is not claimed as full multilingual understanding.

## 5. Answer composition

The top chunks are split into usable sentences after boilerplate removal. A second TF-IDF ranking chooses the most query-relevant sentences. Long table passages are clipped to a relevant window, and every selected sentence inherits the citation metadata of its source chunk.

The response contains at most two evidence statements, numbered citations, and a mandatory freshness warning. The assistant has no path that creates an uncited factual answer.

## 6. Evaluation

The evaluation job runs a fixed question set and records:

- Hit@1 and Hit@3 for the expected official source;
- mean reciprocal rank;
- expected-term coverage in the top three chunks;
- whether every composed answer has a citation.

The complete per-question results are stored in `reports/retrieval_evaluation.json`.
