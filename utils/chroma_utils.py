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
    """
    Add a CV chunk (vector) to the Chroma database.
    :param id: Unique identifier for the chunk (e.g., CV filename or UUID)
    :param embedding: List or numpy array representing the vector
    :param metadata: Optional dictionary with extra info (e.g., candidate name)
    """
    collection.add(
        ids=[id],
        embeddings=[embedding],
        metadatas=[metadata] if metadata else None
    )

# Example usage:
# add_cv_chunk("cv_001", [0.1, 0.2, 0.3, ...], {"name": "John Doe"})

# --- To Retrieve Chunks (vectors) ---
def get_cv_chunk(id):
    """
    Retrieve a CV chunk (vector) from the Chroma database by ID.
    :param id: The unique identifier used when adding the chunk
    :return: The embedding and metadata
    """
    result = collection.get(ids=[id])
    if result['embeddings']:
        return result['embeddings'][0], result['metadatas'][0]
    else:
        return None, None
def list_all_cv_ids(limit=100):
    """
    List all IDs currently stored in the Chroma collection.
    :param limit: Maximum number of IDs to return.
    :return: List of IDs
    """
    result = collection.peek(limit=limit)
    return result['ids']
# Example usage:
# embedding, metadata = get_cv_chunk("cv_001")
# print(embedding, metadata)