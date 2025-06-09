from typing import Optional
from langchain_community.vectorstores import FAISS

class InMemoryVectorStore:
    """A simple class to hold the vector store in memory."""
    def __init__(self):
        self.vector_store: Optional[FAISS] = None

db_store = InMemoryVectorStore()