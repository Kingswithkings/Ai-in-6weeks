import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

client = chromadb.Client()
collection = client.get_or_create_collection(name="knowledge_base")
_embedding_model: SentenceTransformer | None = None
_sample_data_loaded = False


def _get_embedding_model() -> SentenceTransformer | None:
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        _embedding_model = SentenceTransformer(MODEL_NAME)
    except Exception:
        return None

    return _embedding_model


def add_documents(docs: list[str]) -> None:
    model = _get_embedding_model()
    if model is None:
        return

    existing = collection.count()
    embeddings = model.encode(docs).tolist()

    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=[str(existing + index) for index in range(len(docs))],
    )


def query_documents(query: str, top_k: int = 3) -> list[str]:
    model = _get_embedding_model()
    if model is None:
        return []

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    documents = results.get("documents", [])
    return documents[0] if documents else []


def load_sample_data() -> None:
    global _sample_data_loaded

    if _sample_data_loaded or collection.count() > 0:
        _sample_data_loaded = True
        return

    docs = [
        "AI agents are systems that can perform tasks autonomously.",
        "RAG stands for Retrieval-Augmented Generation.",
        "FastAPI is a modern web framework for building APIs with Python.",
        "Kings AI system is designed to build intelligent automation tools.",
    ]
    add_documents(docs)
    _sample_data_loaded = True
