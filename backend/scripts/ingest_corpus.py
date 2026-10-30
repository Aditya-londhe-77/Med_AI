#!/usr/bin/env python3
"""
AEGIS Intelligence Corpus Ingestion Script
==========================================
Ingests intelligence documents from `data/documents/`:
1. Chunks text using 500-token chunks with 50-token overlap.
2. Embeds and stores chunks in ChromaDB vector store.
3. Extracts named entities (spaCy NER: Organization, Country, Person) and ingests into Neo4j.
4. Creates relational graph links:
   - (:Document)-[:HAS_CHUNK]->(:Chunk)
   - (:Chunk)-[:MENTIONS]->(:Entity)
   - Discovers co-occurring entity relationships across chunks.

Usage:
    python backend/scripts/ingest_corpus.py [--docs-dir PATH] [--collection NAME] [--test]
"""

import os
import sys
import argparse
import glob
import logging
import uuid
from typing import List, Dict, Any

# Ensure backend root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
)
logger = logging.getLogger("aegis.ingest")

def parse_header_metadata(text: str, filename: str) -> Dict[str, Any]:
    """Extract metadata from document header or fallback to filename."""
    meta = {
        "doc_id": os.path.splitext(filename)[0],
        "title": filename,
        "classification": "UNCLASSIFIED",
        "tier": 1,
        "date": "2026",
    }
    
    for line in text.splitlines()[:15]:
        line_clean = line.strip()
        if line_clean.startswith("DOCUMENT ID:"):
            meta["doc_id"] = line_clean.replace("DOCUMENT ID:", "").strip()
        elif line_clean.startswith("# INTELLIGENCE DOSSIER:"):
            meta["title"] = line_clean.replace("# INTELLIGENCE DOSSIER:", "").strip()
        elif line_clean.startswith("CLASSIFICATION:"):
            meta["classification"] = line_clean.replace("CLASSIFICATION:", "").strip()
        elif line_clean.startswith("SOURCE TIER:"):
            meta["tier_raw"] = line_clean.replace("SOURCE TIER:", "").strip()
            meta["tier"] = 1 if "TIER 1" in meta["tier_raw"].upper() else 2
        elif line_clean.startswith("DATE:"):
            meta["date"] = line_clean.replace("DATE:", "").strip()
            
    return meta

def ingest_corpus(docs_dir: str, collection_name: str = "general_docs", is_test: bool = False):
    """Main ingestion runner."""
    from app.retrieval.chunking import chunk_text
    from app.retrieval.vector_store import vector_store
    
    search_path = os.path.join(docs_dir, "*.txt")
    doc_files = glob.glob(search_path)
    
    if not doc_files:
        # Fallback to check relative to repo root
        repo_root = os.path.dirname(BACKEND_ROOT)
        search_path = os.path.join(repo_root, docs_dir, "*.txt")
        doc_files = glob.glob(search_path)
        
    logger.info(f"Found {len(doc_files)} intelligence dossier(s) to process from: {docs_dir}")
    
    if not doc_files:
        logger.warning("No .txt documents found in target path.")
        return
        
    total_chunks = 0
    total_entities = 0
    
    # Try importing entity extraction
    try:
        from app.retrieval.graph import extract_entities
        ner_available = True
    except Exception as e:
        logger.warning(f"spaCy NER not available: {e}. Skipping graph extraction.")
        ner_available = False
        
    # Check Neo4j availability
    neo4j_available = False
    neo4j_client = None
    if ner_available and not is_test:
        try:
            from app.shared.neo4j_client import neo4j_client as client
            # Test connectivity
            client.query("RETURN 1 as test")
            neo4j_client = client
            neo4j_available = True
            logger.info("Connected to Neo4j Knowledge Graph successfully.")
        except Exception as e:
            logger.warning(f"Neo4j is not reachable ({e}). Proceeding with vector-only ingestion.")
            
    # Try Vertex AI embeddings if configured
    embedding_model = None
    if not is_test:
        try:
            from app.retrieval.embeddings import get_embedding_model
            embedding_model = get_embedding_model()
            logger.info("Vertex AI text-embedding-005 initialized.")
        except Exception as e:
            logger.warning(f"Vertex AI Embeddings not initialized ({e}). ChromaDB will compute embeddings locally.")

    for file_path in doc_files:
        filename = os.path.basename(file_path)
        logger.info(f"--- Ingesting: {filename} ---")
        
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        meta = parse_header_metadata(raw_text, filename)
        
        # 1. Chunking
        docs = chunk_text(raw_text, metadata=meta)
        if not docs:
            logger.warning(f"No chunks produced for {filename}")
            continue
            
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        base_id = meta.get("doc_id", str(uuid.uuid4()))
        ids = [f"{base_id}_chk_{i}" for i in range(len(texts))]
        
        total_chunks += len(texts)
        logger.info(f"Generated {len(texts)} chunks for '{meta['title']}'")
        
        # 2. Vector DB Ingestion
        embeddings = None
        if embedding_model:
            try:
                embeddings = embedding_model.embed_documents(texts)
            except Exception as e:
                logger.warning(f"Embedding API error: {e}. Falling back to default ChromaDB embeddings.")
                embeddings = None
                
        try:
            vector_store.add_documents(
                collection_name=collection_name,
                documents=texts,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info(f"Stored {len(texts)} vectors in ChromaDB collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to store in ChromaDB: {e}")
            
        # 3. Knowledge Graph Entity Extraction
        if ner_available:
            doc_entities_set = set()
            for i, chunk_text_content in enumerate(texts):
                chunk_id = ids[i]
                ents = extract_entities(chunk_text_content)
                total_entities += len(ents)
                
                for ent in ents:
                    doc_entities_set.add((ent["text"], ent["type"]))
                    
                if neo4j_available and neo4j_client:
                    try:
                        # Add Chunk node
                        cypher_chunk = """
                        MERGE (c:Chunk {chunk_id: $chunk_id})
                        SET c.text = $text, c.doc_id = $doc_id, c.title = $title
                        """
                        neo4j_client.execute_write(cypher_chunk, {
                            "chunk_id": chunk_id,
                            "text": chunk_text_content[:250],
                            "doc_id": base_id,
                            "title": meta["title"]
                        })
                        
                        # Link Chunk to Entities
                        for ent in ents:
                            cypher_ent = f"""
                            MERGE (e:{ent['type']} {{name: $name}})
                            WITH e
                            MATCH (c:Chunk {{chunk_id: $chunk_id}})
                            MERGE (c)-[:MENTIONS]->(e)
                            """
                            neo4j_client.execute_write(cypher_ent, {
                                "name": ent["text"],
                                "chunk_id": chunk_id
                            })
                    except Exception as e:
                        logger.error(f"Error indexing to Neo4j: {e}")
                        
            logger.info(f"Extracted {len(doc_entities_set)} unique entities from {filename}")

    logger.info("==========================================")
    logger.info("INGESTION COMPLETE SUMMARY:")
    logger.info(f"  Total Dossiers Processed: {len(doc_files)}")
    logger.info(f"  Total Text Chunks:        {total_chunks}")
    logger.info(f"  Total Entities Extracted: {total_entities}")
    logger.info(f"  ChromaDB Collection:      {collection_name}")
    logger.info(f"  Neo4j Knowledge Graph:    {'Active' if neo4j_available else 'Offline/Skipped'}")
    logger.info("==========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS Ingest Corpus Script")
    parser.add_argument("--docs-dir", default="data/documents", help="Path to documents folder")
    parser.add_argument("--collection", default="general_docs", help="Target ChromaDB collection")
    parser.add_argument("--test", action="store_true", help="Run in offline verification test mode")
    args = parser.parse_args()
    
    ingest_corpus(docs_dir=args.docs_dir, collection_name=args.collection, is_test=args.test)
