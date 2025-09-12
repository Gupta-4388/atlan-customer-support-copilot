"""
rag.py
- RAG helper: answer_query using ChromaDB + OpenAI
"""

import os
from typing import Dict
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
from ingest import run_ingestion

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment.")

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

# -------------------------------
# Initialize OpenAI client
# -------------------------------
client_openai = OpenAI(api_key=OPENAI_KEY)

# -------------------------------
# Initialize ChromaDB
# -------------------------------
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
embedding_func = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="atlan_docs",
    embedding_function=embedding_func
)

# -------------------------------
# Run ingestion if collection empty
# -------------------------------
if collection.count() == 0:
    print("📥 No docs found in Chroma. Running ingestion...")
    run_ingestion()

# -------------------------------
# Query function
# -------------------------------
def answer_query(query: str, n_results: int = 3) -> Dict[str, any]:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas"]
        )

        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not docs:
            return {"answer": "No relevant documents found in knowledge base.", "sources": []}

        context = "\n\n".join(
            f"Source: {m.get('url', 'N/A')}\n{d}" for d, m in zip(docs, metadatas)
        )

        completion = client_openai.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful support assistant. Use the context to answer."},
                {"role": "user", "content": f"Answer the question using the following context:\n\n{context}\n\nQuestion: {query}"}
            ]
        )

        answer = completion.choices[0].message.content
        sources = [m.get("url", "N/A") for m in metadatas]

        return {"answer": answer, "sources": sources}

    except Exception as e:
        return {"answer": f"Error during query: {e}", "sources": []}
