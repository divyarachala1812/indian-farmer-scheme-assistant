import json

import _project_path  # noqa: F401

from schemeguide.evaluation import evaluate
from schemeguide.retrieval import HybridRetriever

if __name__ == "__main__":
    summary = evaluate(HybridRetriever.load())
    print(json.dumps({key: value for key, value in summary.items() if key != "results"}, indent=2))
