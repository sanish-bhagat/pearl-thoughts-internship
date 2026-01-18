"""Vector store management for RAG."""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.settings import settings


class VectorStore:
    """Manages vector embeddings and semantic search."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the vector store.
        
        Args:
            db_path: Path to store the vector database (defaults to settings.VECTOR_DB_PATH)
        """
        self.db_path = db_path or settings.get_vector_db_path()
        self.store_type = settings.VECTOR_STORE_TYPE
        self.embedding_model = settings.EMBEDDING_MODEL
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        
        self._store = None
        self._embeddings = None
        self._initialized = False
    
    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        if self._embeddings is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            self._embeddings = SentenceTransformer(self.embedding_model)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
    
    def _initialize_store(self):
        """Initialize the vector store (FAISS or Chroma)."""
        if self._store is not None:
            return
        
        self._initialize_embeddings()
        
        if self.store_type.lower() == "faiss":
            try:
                import faiss
                from langchain.vectorstores import FAISS
                from langchain.embeddings import HuggingFaceEmbeddings
                
                # Use LangChain's FAISS with HuggingFace embeddings
                embedding_function = HuggingFaceEmbeddings(
                    model_name=self.embedding_model
                )
                
                # Try to load existing store
                store_path = self.db_path / "faiss_store"
                if store_path.exists():
                    self._store = FAISS.load_local(
                        str(store_path), embeddings=embedding_function
                    )
                else:
                    # Create new store
                    self._store = None  # Will be created when documents are added
                    self._embedding_function = embedding_function
                    
            except ImportError:
                raise ImportError(
                    "FAISS not installed. Install with: pip install faiss-cpu langchain"
                )
        
        elif self.store_type.lower() == "chroma":
            try:
                import chromadb
                from langchain.vectorstores import Chroma
                from langchain.embeddings import HuggingFaceEmbeddings
                
                embedding_function = HuggingFaceEmbeddings(
                    model_name=self.embedding_model
                )
                
                persist_directory = str(self.db_path / "chroma_db")
                self._store = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=embedding_function,
                )
                self._embedding_function = embedding_function
                
            except ImportError:
                raise ImportError(
                    "Chroma not installed. Install with: pip install chromadb langchain"
                )
        else:
            raise ValueError(f"Unsupported store type: {self.store_type}")
    
    def is_initialized(self) -> bool:
        """Check if the vector store is initialized."""
        return self._initialized and self._store is not None
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of dicts with 'content' and 'metadata' keys
        """
        if not documents:
            return
        
        self._initialize_store()
        
        # Extract texts and metadatas
        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        if self.store_type.lower() == "faiss":
            from langchain.vectorstores import FAISS
            
            if self._store is None:
                # Create new store
                self._store = FAISS.from_texts(
                    texts=texts,
                    embedding=self._embedding_function,
                    metadatas=metadatas,
                )
            else:
                # Add to existing store
                self._store.add_texts(texts=texts, metadatas=metadatas)
            
            # Save
            store_path = self.db_path / "faiss_store"
            store_path.mkdir(parents=True, exist_ok=True)
            self._store.save_local(str(store_path))
        
        elif self.store_type.lower() == "chroma":
            # Chroma handles persistence automatically
            self._store.add_texts(texts=texts, metadatas=metadatas)
        
        self._initialized = True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the vector store for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with 'content', 'metadata', and 'score' keys
        """
        if not self.is_initialized():
            return []
        
        try:
            results = self._store.similarity_search_with_score(
                query, k=top_k
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def clear(self):
        """Clear the vector store."""
        if self.store_type.lower() == "faiss":
            store_path = self.db_path / "faiss_store"
            if store_path.exists():
                import shutil
                shutil.rmtree(store_path)
        
        elif self.store_type.lower() == "chroma":
            persist_directory = self.db_path / "chroma_db"
            if persist_directory.exists():
                import shutil
                shutil.rmtree(persist_directory)
        
        self._store = None
        self._initialized = False
