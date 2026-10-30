from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument

def get_text_splitter(chunk_size: int = 500, chunk_overlap: int = 50) -> RecursiveCharacterTextSplitter:
    """
    Returns a RecursiveCharacterTextSplitter configured for AEGIS processing.
    Default configuration matches the IMPLEMENTATION_PLAN.md:
    chunk_size = 500 tokens/characters, chunk_overlap = 50.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

def chunk_text(text: str, metadata: dict = None) -> List[LangchainDocument]:
    """
    Convenience function to chunk raw text into LangchainDocuments.
    """
    splitter = get_text_splitter()
    if metadata is None:
        metadata = {}
    return splitter.create_documents([text], metadatas=[metadata])
