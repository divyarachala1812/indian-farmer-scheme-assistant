from __future__ import annotations

import argparse

from schemeguide.assistant import SchemeAssistant
from schemeguide.retrieval import HybridRetriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Search official Indian farmer-scheme material")
    parser.add_argument("query", nargs="+", help="Question to ask")
    args = parser.parse_args()
    assistant = SchemeAssistant(HybridRetriever.load())
    result = assistant.answer(" ".join(args.query))
    print(result.text)
    print("\nSources:")
    for citation in result.citations:
        page = f", page {citation['page']}" if citation["page"] else ""
        print(f"[{citation['id']}] {citation['title']}{page}\n    {citation['url']}")


if __name__ == "__main__":
    main()
