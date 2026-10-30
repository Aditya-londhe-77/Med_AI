import uuid
from typing import List, Dict, Any
from .chunking import chunk_text
from .embeddings import get_embedding_model
from .vector_store import vector_store

def ingest_text(
    text: str, 
    collection_name: str, 
    source_metadata: Dict[str, Any]
) -> List[str]:
    """
    Ingests a raw text string into ChromaDB.
    1. Chunks the text
    2. Embeds the chunks using Vertex AI
    3. Stores them in ChromaDB
    
    Returns a list of generated chunk IDs.
    """
    # 1. Chunking
    docs = chunk_text(text, metadata=source_metadata)
    
    if not docs:
        return []
        
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    
    # Generate unique IDs for each chunk (can append index to a base ID)
    base_id = source_metadata.get("doc_id", str(uuid.uuid4()))
    ids = [f"{base_id}_chunk_{i}" for i in range(len(texts))]
    
    # 2. Embeddings
    embedding_model = get_embedding_model()
    # Batch embed the texts
    embeddings = embedding_model.embed_documents(texts)
    
    # 3. Store in Vector DB
    vector_store.add_documents(
        collection_name=collection_name,
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )
    
    # 4. Extract Entities and Push to Knowledge Graph (Neo4j)
    from .graph import extract_entities
    from ..shared.neo4j_client import neo4j_client
    
    for i, text_chunk in enumerate(texts):
        chunk_id = ids[i]
        entities = extract_entities(text_chunk)
        
        # Add chunk node to Neo4j
        cypher_chunk = """
        MERGE (c:Chunk {chunk_id: $chunk_id})
        SET c.text = $text, c.doc_id = $doc_id
        """
        neo4j_client.execute_write(cypher_chunk, {
            "chunk_id": chunk_id,
            "text": text_chunk[:200] + "...", # Store snippet for context
            "doc_id": base_id
        })
        
        # Link chunk to entities
        for ent in entities:
            cypher_ent = f"""
            MERGE (e:{ent['type']} {{name: $name}})
            WITH e
            MATCH (c:Chunk {{chunk_id: $chunk_id}})
            MERGE (c)-[:MENTIONS]->(e)
            """
            neo4j_client.execute_write(cypher_ent, {
                "name": ent['text'],
                "chunk_id": chunk_id
            })
            
    return ids

