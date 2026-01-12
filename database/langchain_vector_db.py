import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config.langchain_config import LangChainConfig
from utils.hash_utils import get_file_hash

class LangChainVectorDB:
    def __init__(self):
        self.embeddings = LangChainConfig.get_embeddings()
        self.vectorstore = LangChainConfig.get_vectorstore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def add_pdf_document(self, pdf_path: str, doc_type: str = "cv"):
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            for doc in documents:
                doc.metadata.update({
                    "source": pdf_path,
                    "doc_type": doc_type,
                    "filename": os.path.basename(pdf_path)
                })
            splits = self.text_splitter.split_documents(documents)
            self.vectorstore.add_documents(splits)
            print(f"Added {len(splits)} chunks from {pdf_path}")
            return True
        except Exception as e:
            print(f"Error adding PDF {pdf_path}: {e}")
            return False

    def add_text_document(self, text: str, doc_id: str, doc_type: str = "summary", file_hash: str = None, email: str = None, source: str = None):
        try:
            doc_id_to_use = file_hash if file_hash else doc_id

            if file_hash:
                print(f"Checking for duplicates using file hash: {file_hash}")
                try:
                    existing_docs = self.vectorstore.similarity_search_with_score(
                        query=text,
                        k=1,
                        filter={"file_hash": file_hash}
                    )
                    if existing_docs:
                        print(f"Duplicate document detected. Skipping: {doc_id}")
                        return False
                except Exception as e:
                    print(f"Error during duplicate check: {e}")
                    return False
            else:
                print(f"No file hash provided for {doc_id}. Skipping deduplication check.")

            metadata = {
                "source": source if source else (doc_id if os.path.isfile(doc_id) else "unknown_source"),
                "doc_type": doc_type,
                "document_id": doc_id_to_use
            }
            if file_hash:
                metadata["file_hash"] = file_hash
            if email:
                metadata["email"] = email.lower()

            doc = Document(
                page_content=text,
                metadata=metadata
            )
            self.vectorstore.add_documents([doc])
            print(f"Added text document: {doc_id_to_use}")
            return True
        except Exception as e:
            print(f"Error adding text document {doc_id}: {e}")
            return False

    def add_cv_summary(self, file_path: str, summary: str, email: str = None):
        try:
            file_hash = get_file_hash(file_path)
            print(f"Storing summary with email: {email}")
            print(f"Checking for existing CV summary with hash: {file_hash}")
            try:
                existing = self.vectorstore.similarity_search_with_score(
                    query=summary,
                    k=1,
                    filter={"file_hash": file_hash}
                )
                if existing:
                    print(f"Duplicate CV detected. Skipping: {file_path}")
                    return False
            except Exception as e:
                print(f"Error during duplicate check: {e}")
                return False

            metadata = {
                "source": file_path,
                "doc_type": "cv_summary",
                "file_hash": file_hash
            }
            if email:
                metadata["email"] = email.lower()

            doc = Document(
                page_content=summary,
                metadata=metadata
            )
            self.vectorstore.add_documents([doc])
            print("Summary stored in vector DB")
            return True
        except Exception as e:
            print(f"Error adding CV summary: {e}")
            return False


    def get_all_documents(self):
        try:
            return self.vectorstore.get()
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return {"ids": [], "metadatas": [], "documents": []}

    def get_all_cv_summaries(self):
        try:
            all_docs = self.get_all_documents()
            results = []
            for i in range(len(all_docs["ids"])):
                meta = all_docs["metadatas"][i]
                if meta.get("doc_type") == "cv_summary":
                    results.append({
                        "id": all_docs["ids"][i],
                        "text": all_docs["documents"][i],
                        "metadata": meta
                    })
            return results
        except Exception as e:
            print(f"Error fetching CV summaries: {e}")
            return []

    def print_all_cv_summaries(self):
        try:
            summaries = self.get_all_cv_summaries()
            if not summaries:
                print("No CV summaries found.")
                return
            for idx, doc in enumerate(summaries, 1):
                print(f"\n--- CV Summary #{idx} ---")
                print(f"Document ID: {doc['id']}")
                print(f"Source File: {doc['metadata'].get('source', 'Unknown')}")
                print(f"File Hash: {doc['metadata'].get('file_hash', 'N/A')}")
                print("Summary Text:")
                print(doc['text'])
                print("-" * 40)
        except Exception as e:
            print(f"Error printing summaries: {e}")

    def get_document_count(self):
        return len(self.get_all_documents().get("ids", []))
        
    def get_cv_summary_by_email(self, email):
        try:
            email_lower = email.lower()
            all_summaries = self.get_all_cv_summaries()
            print(f"Looking for email: {email_lower}. Available emails:")
            for summary in all_summaries:
                meta_email = summary["metadata"].get("email", "").lower()
                print(f"- {meta_email}")
                if meta_email == email_lower:
                    return summary["text"]
            return None
        except Exception as e:
            print(f"Error searching CV summary by email {email}: {e}")
            return None
        
if __name__ == "__main__":
    # Create DB instance
    db = LangChainVectorDB()

    #Print all summaries (optional)
    print(f"Database initialized. Document count: {db.get_document_count()}")
    db.print_all_cv_summaries()  

    test_email = "krishanabeywardhana123@gmail.com"
    result = db.get_cv_summary_by_email(test_email)
    if result:
        print(f"\nFound CV Summary for {test_email}:\n{result}")
    else:
        print(f"\nNo CV summary found for {test_email}")
