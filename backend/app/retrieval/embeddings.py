import os
import logging
from langchain_google_vertexai import VertexAIEmbeddings

logger = logging.getLogger(__name__)

def get_embedding_model() -> VertexAIEmbeddings:
    """
    Returns an instance of VertexAIEmbeddings using text-embedding-005.
    Requires GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT to be set.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT is not set. Attempting to initialize embeddings without it.")
        
    try:
        # VertexAIEmbeddings will automatically use the credentials from GOOGLE_APPLICATION_CREDENTIALS
        return VertexAIEmbeddings(
            model_name="text-embedding-005",
            project=project_id
        )
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI Embeddings: {e}")
        raise
