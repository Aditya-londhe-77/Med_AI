import asyncio
import logging
from typing import List
from .vector_store import vector_store
from .graph import retrieve_graph_context

logger = logging.getLogger(__name__)

async def _vector_search(query: str, collection_name: str) -> List[str]:
    """Run ChromaDB vector search in a thread pool executor (sync client)."""
    loop = asyncio.get_event_loop()
    try:
        def _do_search():
            res = vector_store.search(collection_name=collection_name, query_texts=[query], n_results=5)
            if (not res or not res.get("documents") or not res["documents"][0]) and collection_name != "general_docs":
                res = vector_store.search(collection_name="general_docs", query_texts=[query], n_results=5)
            return res

        vector_results = await loop.run_in_executor(None, _do_search)
        if vector_results and "documents" in vector_results and vector_results["documents"][0]:
            blocks = ["--- SEMANTIC CONTEXT (Vector DB) ---"]
            blocks.extend(f"- {doc}" for doc in vector_results["documents"][0])
            return blocks
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
    return []

async def _graph_search(query: str) -> List[str]:
    """Run Neo4j graph search in a thread pool executor (sync client)."""
    loop = asyncio.get_event_loop()
    try:
        graph_results = await loop.run_in_executor(
            None,
            lambda: retrieve_graph_context(query, hops=2),
        )
        if graph_results:
            blocks = ["\n--- RELATIONAL CONTEXT (Knowledge Graph) ---"]
            blocks.extend(f"- {res}" for res in graph_results)
            return blocks
    except Exception as e:
        logger.error(f"Graph search failed: {e}")
    return []

async def get_fused_context(query: str, collection_name: str) -> str:
    """
    Hybrid Retrieval: runs ChromaDB and Neo4j searches *concurrently* via
    asyncio.gather, then fuses the results into a single context string for
    the LLM prompt.

    Performance: both I/O-bound calls execute in parallel, reducing retrieval
    latency compared to the previous sequential approach.
    """
    vector_blocks, graph_blocks = await asyncio.gather(
        _vector_search(query, collection_name),
        _graph_search(query),
    )

    fused_blocks = vector_blocks + graph_blocks

    if not fused_blocks:
        return "No relevant context found."

    return "\n".join(fused_blocks)
