# inspect_vector_db.py

from database.langchain_vector_db import LangChainVectorDB  # Make sure this path matches your file name

def list_vector_db_documents(limit: int = None):
    db = LangChainVectorDB()
    docs = db.get_all_documents()

    if not docs["ids"]:
        print("📭 No documents found in vector DB.")
        return

    print(f"📦 Listing up to {limit} documents in vector DB...\n")

    for i in range(min(limit, len(docs["ids"]))):
        doc_id = docs["ids"][i]
        metadata = docs["metadatas"][i]
        content = docs["documents"][i]

        print(f"--- Document #{i + 1} ---")
        print(f"ID         : {doc_id}")
        print(f"Doc Type   : {metadata.get('doc_type', 'N/A')}")
        print(f"Email      : {metadata.get('email', 'N/A')}")
        print(f"Source     : {metadata.get('source', 'N/A')}")
        print(f"File Hash  : {metadata.get('file_hash', 'N/A')}")
        print(f"Preview    : {content[:200]}...\n")

    print("Done listing documents.")

if __name__ == "__main__":
    list_vector_db_documents(limit=20)
