from schemeguide.ingest import build_corpus
from schemeguide.retrieval import HybridRetriever

if __name__ == "__main__":
    chunks = build_corpus()
    retriever = HybridRetriever(chunks)
    retriever.save()
    print(f"Indexed {len(chunks):,} chunks from official sources")
