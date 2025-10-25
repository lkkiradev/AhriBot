import os
from pathlib import Path

class Config:
    class Path:
        APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
        DATABASE_DIR = APP_HOME / "docs-db"
        DOCUMENTS_DIR = APP_HOME / "tmp"
        IMAGES_DIR = APP_HOME / "images"
        PDF_DIR = APP_HOME / "docs"
        CACHE_DIR = APP_HOME / "cache"

    class Database:
        DOCUMENTS_COLLECTION = "documents"

    class Model:
        EMBEDDINGS = "BAAI/bge-base-en-v1.5"
        RERANKER = "ms-marco-MiniLM-L-12-v2"
        LOCAL_LLM = "llama3.1"
        REMOTE_LLM = "llama-3.1-70b-versatile"
        TEMPERATURE = 1.0
        MAX_TOKENS = 8000
        USE_LOCAL = False
        GROQ_API_KEY = "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"

    class Retriever:
        USE_RERANKER = True
        USE_CHAIN_FILTER = False
    
    class Deduplication:
        ENABLE_DEDUPLICATION = True

    DEBUG = False
    CONVERSATION_MESSAGES_LIMIT = 50
