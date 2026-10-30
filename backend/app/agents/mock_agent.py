import time
from typing import List, Dict, Any
from .base import BaseAgent
from ..shared.schemas import AgentRequest, AgentResponse, Claim, SourceCitation
from ..shared.constants import SourceTier

class MockAgent(BaseAgent):
    """
    A stub agent for testing the orchestration pipeline.
    """
    
    def __init__(self, agent_id: str = "mock_agent", model_name: str = "mock-model"):
        super().__init__(agent_id, model_name)

    async def run(self, request: AgentRequest) -> AgentResponse:
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(1)
        
        source = SourceCitation(
            id="src_1",
            url="https://example.com/report",
            title="Mock Industry Report",
            tier=SourceTier.TIER_2,
            snippet="This is a simulated piece of evidence."
        )
        
        claim = Claim(
            id="clm_1",
            statement=f"Mock analysis based on query: {request.query}",
            confidence_score=0.85,
            sources=[source],
            agent_id=self.agent_id
        )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return AgentResponse(
            agent_id=self.agent_id,
            status="success",
            claims=[claim],
            raw_output="Mock agent execution completed successfully.",
            execution_time_ms=execution_time
        )

    async def challenge_review(self, request: AgentRequest, challenges: List[Dict[str, Any]]) -> AgentResponse:
        # Mock just returns the same response for now
        return await self.run(request)
