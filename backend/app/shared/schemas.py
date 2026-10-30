from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .constants import SourceTier

class SourceCitation(BaseModel):
    id: str
    url: Optional[str] = None
    title: str
    tier: SourceTier
    snippet: str
    accessed_at: datetime = Field(default_factory=datetime.utcnow)

class Claim(BaseModel):
    id: str
    statement: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    sources: List[SourceCitation]
    challenged: bool = False
    challenge_result: Optional[str] = None
    challenge_note: Optional[str] = None
    revised: bool = False
    agent_id: str

class AgentRequest(BaseModel):
    query: str
    session_id: str
    max_rounds: int = 2

class AgentResponse(BaseModel):
    agent_id: str
    status: str
    claims: List[Claim]
    raw_output: str
    execution_time_ms: int

class WSMessage(BaseModel):
    event_type: str  # e.g., "agent_started", "claim_challenged", "briefing_ready"
    agent_id: Optional[str] = None
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
