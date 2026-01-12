import chromadb
from chromadb.config import Settings

# Connect to your Chroma database
import os
db_path = os.path.abspath("cv_chroma_db")
client = chromadb.Client(Settings(persist_directory=db_path))

# Get or create a collection (e.g., for CVs)
collection = client.get_or_create_collection("cv_job_summaries")

# --- To Add a Chunk (vector) ---
def add_cv_chunk(id, embedding, metadata=None):

    collection.add(
        ids=[id],
        embeddings=[embedding],
        metadatas=[metadata] if metadata else None
    )


def get_cv_chunk(id):
  
    result = collection.get(ids=[id])
    if result['embeddings']:
        return result['embeddings'][0], result['metadatas'][0]
    else:
        return None, None
def list_all_cv_ids(limit=100):
  
    result = collection.peek(limit=limit)
    return result['ids']
