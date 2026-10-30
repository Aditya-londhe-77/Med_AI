import os
import chromadb
from typing import List, Dict, Any, Optional

class VectorStore:
    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initializes ChromaDB in persistent mode.
        If running in Docker, 'chroma_db' is mounted as a volume.
        """
        # Ensure path is absolute or relative to project root
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        self.collections = {}

    def get_or_create_collection(self, collection_name: str):
        if collection_name not in self.collections:
            try:
                self.collections[collection_name] = self.client.get_collection(name=collection_name)
            except Exception:
                self.collections[collection_name] = self.client.get_or_create_collection(name=collection_name)
        return self.collections[collection_name]

    def add_documents(
        self, 
        collection_name: str, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str], 
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Add documents to a collection. Assumes embeddings are already computed and passed.
        """
        collection = self.get_or_create_collection(collection_name)
        if embeddings:
            collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
        else:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def search(
        self, 
        collection_name: str, 
        query_embeddings: Optional[List[List[float]]] = None, 
        query_texts: Optional[List[str]] = None, 
        n_results: int = 8,
        where: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Perform a vector search. Returns a dict containing 'ids', 'distances', 'metadatas', 'documents'.
        """
        collection = self.get_or_create_collection(collection_name)
        
        query_kwargs = {"n_results": n_results}
        if query_embeddings:
            query_kwargs["query_embeddings"] = query_embeddings
        elif query_texts:
            query_kwargs["query_texts"] = query_texts
        else:
            raise ValueError("Must provide either query_embeddings or query_texts")
            
        if where:
            query_kwargs["where"] = where
            
        return collection.query(**query_kwargs)

# Global instance to be used across the app
vector_store = VectorStore()
