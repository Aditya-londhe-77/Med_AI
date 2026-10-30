"""
Medical Base Agent for AISIA.
All medical agents inherit from this class.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalAgentResponse, MedicalFinding,
    MedicalSourceCitation, EvidenceGrade, MedicalDomain
)

logger = logging.getLogger(__name__)

MEDICAL_DISCLAIMER = (
    "This information is for educational purposes only and does not constitute medical advice. "
    "Consult a qualified healthcare professional for diagnosis and treatment."
)

FALLBACK_SOURCE_NOTICE = "AI-generated educational content — no primary source located for this specific claim."


class MedicalBaseAgent(ABC):
    """
    Abstract base class for all AISIA medical agents.
    Provides shared utilities: RAG retrieval, fallback source creation, disclaimer injection.
    """

    def __init__(self, agent_id: str, agent_name: str, model_name: str = "gemini-1.5-flash"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_name = model_name

    @abstractmethod
    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        """Execute the agent's core medical research logic."""
        pass

    @abstractmethod
    async def validate_findings(
        self,
        request: MedicalQueryRequest,
        challenges: List[Dict[str, Any]]
    ) -> MedicalAgentResponse:
        """Handle validation challenges from the Evidence Validation Agent."""
        pass

    async def retrieve_medical_context(
        self,
        query: str,
        collection_name: str = "medical_literature"
    ) -> str:
        """
        Retrieve medical context from hybrid ChromaDB + Neo4j RAG pipeline.
        Falls back gracefully if vector store or graph is unavailable.
        """
        try:
            from app.retrieval.hybrid import get_fused_context
            context = await get_fused_context(query, collection_name)
            if context and len(context.strip()) > 20:
                return context
        except Exception as e:
            logger.debug(f"RAG retrieval unavailable ({e}). Using empty context.")
        return ""

    def create_fallback_source(self, claim_id: str, domain: str = "Medical") -> MedicalSourceCitation:
        """
        Create a transparent fallback source when no real source is available.
        Clearly marks the source as AI-generated educational content.
        """
        return MedicalSourceCitation(
            id=f"src_fallback_{claim_id}",
            url=None,
            title=FALLBACK_SOURCE_NOTICE,
            source_type="AI Educational Content",
            grade=EvidenceGrade.GRADE_C,
            snippet=f"AI-generated educational context for {domain} query.",
            is_ai_generated=True
        )

    def create_medical_finding(
        self,
        finding_id: str,
        statement: str,
        confidence: float,
        sources: List[MedicalSourceCitation],
        domain: MedicalDomain = MedicalDomain.GENERAL_MEDICINE,
        finding_type: str = "informational"
    ) -> MedicalFinding:
        """Create a validated MedicalFinding object with standard disclaimer."""
        return MedicalFinding(
            id=finding_id,
            statement=statement,
            confidence_score=min(1.0, max(0.0, confidence)),
            sources=sources,
            domain=domain,
            agent_id=self.agent_id,
            finding_type=finding_type,
            disclaimer=MEDICAL_DISCLAIMER
        )

    def error_response(self, error_msg: str) -> MedicalAgentResponse:
        """Return a graceful error response from the agent."""
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="error",
            findings=[],
            raw_output=f"Agent error: {error_msg}",
            execution_time_ms=0
        )
