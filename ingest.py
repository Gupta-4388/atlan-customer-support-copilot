"""
ingest.py
- Ingest selected Atlan docs + developer URLs
- Store them in ChromaDB with embeddings
"""

import os
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

# -------------------------------
# Curated knowledge base URLs
# -------------------------------
TOPICS = {
    "Product": [
        "https://docs.atlan.com/get-started/what-is-atlan",
        "https://docs.atlan.com/get-started/how-tos/quick-start-for-admins#glossary",
        "https://docs.atlan.com/product/capabilities/lineage",
        "https://docs.atlan.com/secure-agent#how-it-works"
    ],
    "SSO": [
        "https://docs.atlan.com/platform/concepts/authentication-and-authorization#sso-authentication"
    ],
    "Best Practices": [
        "https://docs.atlan.com/platform/references/compliance-standards-and-assessments"
    ],
    "API/SDK": [
        "https://docs.atlan.com/get-started/references/api-authentication",
        "https://docs.atlan.com/get-started/how-tos/getting-started-with-the-apis",
        "https://developer.atlan.com/reference/",
        "https://developer.atlan.com/snippets/access/tokens/",
        "https://developer.atlan.com/snippets/users-groups/read/",
        "https://developer.atlan.com/snippets/users-groups/sso-group-mapping/"
    ]
}

# -------------------------------
# Initialize Chroma client
# -------------------------------
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
embedding_func = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="atlan_docs",
    embedding_function=embedding_func
)

# -------------------------------
# Helper: fetch text from URL
# -------------------------------
def fetch_text(url: str) -> str:
    resp = requests.get(url, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    for script in soup(["script", "style", "nav", "footer"]):
        script.decompose()
    return " ".join(soup.stripped_strings)

# -------------------------------
# Run ingestion if collection empty
# -------------------------------
def run_ingestion():
    count = collection.count()
    if count > 0:
        print(f"⚡ Skipping ingestion, {count} docs already present.")
        return

    doc_id = 0
    for topic, urls in TOPICS.items():
        for url in urls:
            text = fetch_text(url)
            collection.add(
                documents=[text],
                metadatas=[{"topic": topic, "url": url}],
                ids=[f"doc_{doc_id}"]
            )
            print(f"Ingested {url}")
            doc_id += 1
    print("✅ Ingestion complete (persisted automatically).")

# -------------------------------
# Run ingestion if executed directly
# -------------------------------
if __name__ == "__main__":
    run_ingestion()
