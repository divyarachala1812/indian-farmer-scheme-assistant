# Evaluation

## Test set

The test set contains 18 declared questions:

- three PM-KISAN questions;
- three PMFBY questions;
- three Soil Health Card questions;
- three e-NAM questions;
- three Kisan Credit Card questions;
- two Hindi questions and one Hinglish question that repeat important intents in a different form.

Each question has an expected source ID and two expected evidence terms. The labels are stored in `data/evaluation/questions.json` so the test is inspectable rather than hidden.

## Metrics

| Metric | Definition | Result |
|---|---|---:|
| Hit@1 | Expected source appears first | 1.000 |
| Hit@3 | Expected source appears in first three chunks | 1.000 |
| MRR | Mean reciprocal rank of expected source | 1.000 |
| Term coverage@3 | Expected evidence terms present in top-three text | 0.972 |
| Citation completeness | Every answer includes a source | 100% |

## Interpretation

The system retrieves the correct official source first for every declared evaluation question. Expected-term coverage is slightly lower because PDF extraction and chunk boundaries can separate a phrase even when the correct page is retrieved.

The result is useful evidence for this project's scope, but it is not a general benchmark. The questions are small, source-specific, and curated by the project author. A stronger future evaluation would add paraphrases written by independent reviewers, adversarial questions, outdated-policy traps, unanswerable questions, more Indian languages, and graded answer-support judgements.

## Error analysis performed during development

Early retrieval exposed two useful problems:

1. Dynamic e-NAM webpages returned navigation HTML rather than FAQ content. The source was replaced with a static Government of India explainer PDF.
2. The RBI page wrapped its main content in an HTML form. Removing all form elements deleted the KCC circular, so extraction was narrowed to scripts and presentation-only elements and the RBI content container was selected explicitly.

The final metrics were regenerated only after those source-ingestion problems were corrected.

## Answer quality boundary

Retrieval correctness does not guarantee that every extracted sentence is perfectly written. Tables in PDFs can lose layout, so the assistant may return a dense evidence excerpt. That tradeoff is documented and preferred to paraphrasing a financial or eligibility rule without a generative model and a stronger factuality evaluation.
