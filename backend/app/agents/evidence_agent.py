"""
Medical Evidence Validation Agent for AISIA.
Acts as the peer-review and adversarial evidence auditor.
Cross-examines claims from Literature, Clinical, and Medication agents,
identifies contradictions, challenges low-evidence assertions, and checks source provenance.
"""

import time
import json
import logging
from typing import List, Dict, Any

from .medical_base import MedicalBaseAgent
from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalAgentResponse, MedicalFinding,
    EvidenceGrade, MedicalDomain
)
from app.shared.llm import generate_text

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = (
    "You are the Medical Evidence Validation Agent for AISIA (Evidence-Grounded Medical Intelligence). "
    "Your role corresponds to an expert medical peer-reviewer and evidence validator. "
    "You rigorously audit medical statements produced by other agents: "
    "1. Identify potential contradictions between statements (e.g., efficacy vs. safety contradictions). "
    "2. Scrutinize evidence quality (flag statements lacking primary literature or relying on unverified claims). "
    "3. Check for omitted safety warnings, high-risk contraindications, or vulnerable population caveats. "
    "4. Generate targeted, constructive challenges to prompt claim revision. "
    "Maintain strict adherence to evidence-based medicine (GRADE framework)."
)


class MedicalEvidenceValidationAgent(MedicalBaseAgent):
    """
    Medical Evidence Validation Agent.
    Audits and validates findings, flags contradictions and evidence gaps,
    and generates challenges for iterative agent refinement.
    """

    def __init__(self):
        super().__init__(
            agent_id="evidence_agent",
            agent_name="Medical Evidence Validation Agent",
            model_name="gemini-1.5-pro"
        )

    async def review_findings(
        self,
        request: MedicalQueryRequest,
        findings: List[MedicalFinding]
    ) -> Dict[str, Any]:
        """
        Audits a collection of medical findings.
        Returns:
        - challenges: List of targeted challenges for agents
        - contradictions: List of identified contradictory assertions
        - evidence_gaps: List of noted missing evidence or caveats
        - updated_findings: Findings with validation scores updated
        """
        start_time = time.time()
        query = request.query

        findings_data = [
            {
                "id": f.id,
                "agent_id": f.agent_id,
                "statement": f.statement,
                "confidence": f.confidence_score,
                "sources": [s.title for s in f.sources],
                "grades": [s.grade.value for s in f.sources]
            }
            for f in findings
        ]

        llm_prompt = f"""You are the Medical Evidence Validation Agent for AISIA.
Audit the following medical findings for consistency, source rigor, and safety omissions.

Query: "{query}"

Findings to Validate:
{json.dumps(findings_data, indent=2)}

Perform rigorous peer-review and return ONLY a valid JSON object:
{{
  "challenges": [
    {{
      "finding_id": "finding_id_to_challenge",
      "agent_id": "agent_id",
      "challenge_text": "Precise evidentiary critique or question demanding nuance",
      "severity": "HIGH or MODERATE"
    }}
  ],
  "contradictions": [
    "Description of contradiction between findings A and B"
  ],
  "evidence_gaps": [
    "Noted absence of primary RCT evidence, long-term safety data, or guideline consensus"
  ],
  "overall_evidence_quality": "HIGH / MODERATE / LOW"
}}"""

        challenges = []
        contradictions = []
        evidence_gaps = []

        llm_output = await generate_text(llm_prompt, model_name=self.model_name, system_instruction=SYSTEM_INSTRUCTION)
        if llm_output:
            try:
                clean_json = llm_output.strip()
                if clean_json.startswith("```"):
                    clean_json = "\n".join(clean_json.split("\n")[1:])
                    if clean_json.endswith("```"):
                        clean_json = clean_json.rsplit("\n", 1)[0]
                audit = json.loads(clean_json)
                challenges = audit.get("challenges", [])
                contradictions = audit.get("contradictions", [])
                evidence_gaps = audit.get("evidence_gaps", [])
            except Exception as e:
                logger.debug(f"EvidenceValidationAgent: JSON parse failed ({e}). Running rule-based validation.")

        # Rule-based validation fallback and augmentation
        if not challenges:
            for f in findings:
                # Flag findings that rely solely on AI fallback
                has_fallback = any(s.is_ai_generated for s in f.sources)
                if has_fallback and f.confidence_score > 0.80:
                    challenges.append({
                        "finding_id": f.id,
                        "agent_id": f.agent_id,
                        "challenge_text": "Claim relies on educational synthesis rather than primary indexed literature; calibrate confidence.",
                        "severity": "MODERATE"
                    })
                # Check for low confidence
                if f.confidence_score < 0.70:
                    evidence_gaps.append(f"Finding '{f.id}' exhibits low evidentiary confidence ({round(f.confidence_score*100)}%).")

        # Update findings validation status
        challenged_ids = {c.get("finding_id") for c in challenges}
        for f in findings:
            if f.id in challenged_ids:
                f.validated = False
                ch = next(c for c in challenges if c.get("finding_id") == f.id)
                f.validation_notes = f"Evidentiary Challenge: {ch.get('challenge_text')}"
            else:
                f.validated = True

        execution_time = int((time.time() - start_time) * 1000)
        logger.info(f"EvidenceValidationAgent completed in {execution_time}ms: {len(challenges)} challenges, {len(contradictions)} contradictions.")

        return {
            "challenges": challenges,
            "contradictions": contradictions,
            "evidence_gaps": evidence_gaps,
            "updated_findings": findings
        }

    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="ready",
            findings=[],
            raw_output="Evidence Validation Agent acts via review_findings() during workflow validation.",
            execution_time_ms=0
        )

    async def validate_findings(
        self, request: MedicalQueryRequest, challenges: List[Dict[str, Any]]
    ) -> MedicalAgentResponse:
        return await self.run(request)
