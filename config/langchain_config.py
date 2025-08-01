import os
from groq import Groq
# Use modern HuggingFace embeddings to avoid deprecation warnings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

# Try to import ChatGroq, fallback to direct Groq if not available
try:
    from langchain_groq import ChatGroq
    LANGCHAIN_GROQ_AVAILABLE = True
except ImportError:
    LANGCHAIN_GROQ_AVAILABLE = False
    print("Warning: langchain_groq not available, using direct Groq client")

load_dotenv()

class LangChainConfig:
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    
    # Available Groq models (updated for current models)
    GROQ_MODELS = {
        "llama-3.3-70b": "llama-3.3-70b-versatile",
        "llama-3.1-8b": "llama-3.1-8b-instant",
        "llama-3.2-90b": "llama-3.2-90b-text-preview", 
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gemma-7b": "gemma-7b-it"
    }
    
    MODEL_NAME = GROQ_MODELS["llama-3.3-70b"]  # Use current model
    TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    
    # Vector Store Configuration
    CHROMA_DB_PATH = "./cv_chroma_db"
    COLLECTION_NAME = "cv_job_summaries"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # File Paths
    CV_FOLDER = "data/cv_pdfs"
    JOB_FOLDER = "data/job_ads"
    UPLOAD_FOLDER = "./temp_uploads"
    
    @classmethod
    def get_llm(cls, model_name=None, temperature=None):
        """Get Groq LLM via LangChain (with fallback to direct client)"""
        if LANGCHAIN_GROQ_AVAILABLE:
            return ChatGroq(
                groq_api_key=cls.GROQ_API_KEY,
                model_name=model_name or cls.MODEL_NAME,
                temperature=temperature or cls.TEMPERATURE,
                max_tokens=cls.MAX_TOKENS
            )
        else:
            # Fallback to direct Groq client
            return Groq(api_key=cls.GROQ_API_KEY)
    
    @classmethod
    def get_embeddings(cls):
        return HuggingFaceEmbeddings(model_name=cls.EMBEDDING_MODEL)
    
    @classmethod
    def get_vectorstore(cls):
        return Chroma(
            persist_directory=cls.CHROMA_DB_PATH,
            embedding_function=cls.get_embeddings(),
            collection_name=cls.COLLECTION_NAME
        )
