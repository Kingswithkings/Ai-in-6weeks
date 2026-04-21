import chromadb
from sentence_transformers import SentenceTransformer

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Chroma DB
client = chromadb.Client()
collection = client.get_or_create_collection(name="knowledge_base")


def add_documents(docs: list[str]):
    embeddings = embedding_model.encode(docs).tolist()

    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=[str(i) for i in range(len(docs))]
    )


def query_documents(query: str, top_k: int = 3):
    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results["documents"][0]

def load_sample_data():
    docs = [
        "AI agents are systems that can perform tasks autonomously.",
        "RAG stands for Retrieval-Augmented Generation.",
        "FastAPI is a modern web framework for building APIs with Python.",
        "Kings AI system is designed to build intelligent automation tools."
    ]
    add_documents(docs)