# Safety and responsible use

## Allowed use

- discover which official source discusses a scheme question;
- retrieve passages about benefits, programme purpose, premiums, market access, soil cards, and agricultural credit;
- use citations to continue research on an official portal;
- demonstrate applied NLP and retrieval engineering.

## Prohibited interpretation

The output is not:

- a final eligibility decision;
- an application approval or rejection;
- legal, financial, crop-insurance, or health advice;
- a promise that an amount, deadline, rate, or document remains current;
- a substitute for a bank, insurer, agriculture office, or government portal.

## Built-in controls

- Answers are extractive and use indexed official passages.
- Every factual answer carries citations.
- Source titles, publishers, page numbers, and URLs are returned.
- A verification warning is appended to every answer.
- The assistant does not collect Aadhaar numbers, bank details, land records, or personal profiles.
- Downloaded documents are local and excluded from version control.

## Freshness risk

The source registry includes the document version in its title when known. Scheme rules can change without a code change. Rebuilding the index refreshes the downloaded files, but the user must still confirm the publication date and current portal instructions.

## Unsupported questions

If no candidate sentences can be extracted, the assistant returns that it could not find a supported answer. A production version should also use a confidence threshold and abstain when the top retrieval score is low or sources disagree.
