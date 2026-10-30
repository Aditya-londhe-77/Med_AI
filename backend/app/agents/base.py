from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..shared.schemas import AgentRequest, AgentResponse

class BaseAgent(ABC):
    """
    Abstract base class for all AEGIS agents.
    """
    
    def __init__(self, agent_id: str, model_name: str):
        self.agent_id = agent_id
        self.model_name = model_name

    @abstractmethod
    async def run(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent's core logic for a given request.
        Must be implemented by subclasses.
        """
        pass
        
    @abstractmethod
    async def challenge_review(self, request: AgentRequest, challenges: List[Dict[str, Any]]) -> AgentResponse:
        """
        Handle challenges from the Devil's Advocate agent.
        """
        pass
        
    async def retrieve_context(self, query: str, collection_name: str = "general_docs") -> str:
        """
        Retrieves context using the Hybrid GraphRAG pipeline (ChromaDB + Neo4j).
        """
        from ..retrieval.hybrid import get_fused_context
        return await get_fused_context(query, collection_name)

