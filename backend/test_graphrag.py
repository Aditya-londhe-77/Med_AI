import asyncio
import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.retrieval.ingestion import ingest_text
from app.retrieval.hybrid import get_fused_context

async def test_graphrag():
    print("=== Testing AEGIS Hybrid GraphRAG ===")
    
    # 1. Mock Document Ingestion
    print("\n[1] Ingesting test document...")
    sample_text = (
        "Apple Inc. is headquartered in Cupertino, California. "
        "Tim Cook is the CEO of Apple. "
        "Apple released the new iPhone 15 recently."
    )
    metadata = {"source": "test_doc", "doc_id": "test_123"}
    
    try:
        chunk_ids = ingest_text(sample_text, collection_name="test_docs", source_metadata=metadata)
        print(f"Successfully ingested chunks: {chunk_ids}")
    except Exception as e:
        print(f"Ingestion failed. Ensure Neo4j and ChromaDB are running. Error: {e}")
        return

    # 2. Query the Hybrid System
    print("\n[2] Querying Hybrid Context...")
    query = "Who is the CEO of Apple?"
    print(f"Query: '{query}'")
    
    try:
        fused_context = await get_fused_context(query, collection_name="test_docs")
        print("\n--- Fused Context Result ---")
        print(fused_context)
        print("----------------------------")
    except Exception as e:
        print(f"Query failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_graphrag())
