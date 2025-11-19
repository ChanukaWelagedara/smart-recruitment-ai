# # # inspect_vector_db.py

# # from database.langchain_vector_db import LangChainVectorDB  # Make sure this path matches your file name

# # def list_vector_db_documents(limit: int = None):
# #     db = LangChainVectorDB()
# #     docs = db.get_all_documents()

# #     if not docs["ids"]:
# #         print("📭 No documents found in vector DB.")
# #         return

# #     print(f"📦 Listing up to {limit} documents in vector DB...\n")

# #     for i in range(min(limit, len(docs["ids"]))):
# #         doc_id = docs["ids"][i]
# #         metadata = docs["metadatas"][i]
# #         content = docs["documents"][i]

# #         print(f"--- Document #{i + 1} ---")
# #         print(f"ID         : {doc_id}")
# #         print(f"Doc Type   : {metadata.get('doc_type', 'N/A')}")
# #         print(f"Email      : {metadata.get('email', 'N/A')}")
# #         print(f"Source     : {metadata.get('source', 'N/A')}")
# #         print(f"File Hash  : {metadata.get('file_hash', 'N/A')}")
# #         print(f"Preview    : {content[:200]}...\n")

# #     print("Done listing documents.")

# # if __name__ == "__main__":
# #     list_vector_db_documents(limit=20)

# # inspect_vector_db.py

# from database.langchain_vector_db import LangChainVectorDB  # Make sure this path matches your file

# def list_vector_db_documents(limit: int = None):
#     db = LangChainVectorDB()
#     docs = db.get_all_documents()

#     total_docs = len(docs["ids"])
#     if total_docs == 0:
#         print("📭 No documents found in vector DB.")
#         return

#     print(f"📦 Total documents in DB: {total_docs}")
#     if limit:
#         print(f"📌 Showing up to {limit} documents...\n")
#     else:
#         print("📌 Showing all documents...\n")

#     for i, doc_id in enumerate(docs["ids"]):
#         if limit and i >= limit:
#             break

#         metadata = docs["metadatas"][i] or {}
#         content = docs["documents"][i] or ""

#         print(f"--- Document #{i + 1} ---")
#         print(f"ID         : {doc_id}")
#         print(f"Doc Type   : {metadata.get('doc_type', 'N/A')}")
#         print(f"Email      : {metadata.get('email', 'N/A')}")
#         print(f"Source     : {metadata.get('source', 'N/A')}")
#         print(f"File Hash  : {metadata.get('file_hash', 'N/A')}")
#         print(f"Preview    : {content[:200].replace(chr(10), ' ')}...\n")  # Single-line preview

#     print("✅ Done listing documents.")

# if __name__ == "__main__":
#     # Set limit=None to show all documents, or a number to limit
#     list_vector_db_documents(limit=None)


# ...existing code...
from database.langchain_vector_db import LangChainVectorDB  # Make sure this path matches your file

def list_vector_db_documents(limit: int = None):
    db = LangChainVectorDB()

    # Print what DB the inspector is connected to
    print("🔎 Vector DB config:")
    for k in ["persist_directory", "collection_name", "namespace", "index_path", "persist_path", "db_path"]:
        print(f" - {k}: {getattr(db, k, None)}")
    # If your wrapper exposes an embeddings/model name, show it too
    for k in ["embedding_model", "embedding_provider"]:
        if hasattr(db, k):
            print(f" - {k}: {getattr(db, k)}")

    docs = db.get_all_documents()

    total_docs = len(docs["ids"])
    if total_docs == 0:
        print("📭 No documents found in vector DB.")
        return

    print(f"📦 Total documents in DB: {total_docs}")
    if limit:
        print(f"📌 Showing up to {limit} documents...\n")
    else:
        print("📌 Showing all documents...\n")

    for i, doc_id in enumerate(docs["ids"]):
        if limit and i >= limit:
            break

        metadata = docs["metadatas"][i] or {}
        content = docs["documents"][i] or ""

        print(f"--- Document #{i + 1} ---")
        print(f"ID         : {doc_id}")
        print(f"Doc Type   : {metadata.get('doc_type', 'N/A')}")
        print(f"Email      : {metadata.get('email', 'N/A')}")
        print(f"Source     : {metadata.get('source', 'N/A')}")
        print(f"File Hash  : {metadata.get('file_hash', 'N/A')}")
        print(f"Preview    : {content[:200].replace(chr(10), ' ')}...\n")  # Single-line preview

    print("✅ Done listing documents.")

if __name__ == "__main__":
    # Set limit=None to show all documents, or a number to limit
    list_vector_db_documents(limit=None)
# ...existing code...