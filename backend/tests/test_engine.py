import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.shared.schemas import AgentRequest, Claim, SourceCitation
from app.shared.constants import SourceTier
from app.confidence.engine import ConfidenceEngine
from app.orchestrator.workflow import create_workflow

def test_confidence_engine_scoring():
    engine = ConfidenceEngine()
    source = SourceCitation(
        id="s1",
        title="BIS Directive",
        tier=SourceTier.TIER_1,
        snippet="Mandatory export licensing",
        trust_score=0.95
    )
    claim = Claim(
        id="c1",
        statement="ASML DUV export controls limit Chinese sub-7nm yields",
        confidence_score=0.85,
        sources=[source],
        agent_id="recon_agent"
    )
    
    score = engine.score_claim(claim, challenge_survived=True)
    assert 0.1 <= score <= 1.0
    assert score > 0.85 # Bonus for surviving challenge

def test_global_confidence_metrics():
    engine = ConfidenceEngine()
    source = SourceCitation(
        id="s1",
        title="BIS Directive",
        tier=SourceTier.TIER_1,
        snippet="Mandatory export licensing",
        trust_score=0.95
    )
    claims = [
        Claim(
            id="c1",
            statement="Statement 1",
            confidence_score=0.90,
            sources=[source],
            agent_id="recon_agent"
        ),
        Claim(
            id="c2",
            statement="Statement 2",
            confidence_score=0.80,
            sources=[source],
            agent_id="financial_agent"
        )
    ]
    
    metrics = engine.global_confidence(claims)
    assert "global_score" in metrics
    assert "evidence_richness" in metrics
    assert "consensus_score" in metrics
    assert "challenge_survival_rate" in metrics
    assert metrics["global_score"] > 0

def test_workflow_execution():
    import asyncio
    async def _run():
        app = create_workflow()
        request = AgentRequest(query="Impact of semiconductor export controls", session_id="test_pytest")
        state = {
            "request": request,
            "all_claims": [],
            "agent_responses": {},
            "challenges": [],
            "round_count": 0,
            "final_briefing": {},
            "confidence_metrics": {}
        }
        return await app.ainvoke(state)
        
    result = asyncio.run(_run())
    briefing = result.get("final_briefing", {})
    assert "title" in briefing
    assert "scenarios" in briefing
    assert len(briefing["scenarios"]) >= 3
    assert len(briefing["claims"]) > 0
