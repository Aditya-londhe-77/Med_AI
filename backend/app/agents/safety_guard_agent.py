"""
Medical Safety Guard Agent for AISIA.
Final safety check that sanitises content and adds safety notes / emergency flags.
Works with the new structured answer schema:
  direct_answer, what_this_means, next_steps, when_to_seek_help, sources, safety_note, evidence_details
"""

import logging
import re
from typing import List, Dict, Any

from .medical_base import MedicalBaseAgent, MEDICAL_DISCLAIMER
from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalAgentResponse
)

logger = logging.getLogger(__name__)

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "overdose", "suicide",
    "can't breathe", "cannot breathe", "difficulty breathing",
    "severe bleeding", "unconscious", "not breathing",
    "anaphylactic", "septic shock",
]

EMERGENCY_NOTICE = (
    "If you or someone nearby is experiencing these symptoms RIGHT NOW, "
    "call emergency services (911 / 112 / 108) immediately or go to the nearest emergency room."
)

SAFETY_NOTE = (
    "This information is for general educational purposes and does not replace "
    "personalised advice from a qualified healthcare professional."
)


class MedicalSafetyGuardAgent(MedicalBaseAgent):
    """
    Medical Safety and Domain Guard Agent.
    Final validation pass for all medical responses.
    """

    def __init__(self):
        super().__init__(
            agent_id="safety_guard_agent",
            agent_name="Medical Safety Guard Agent",
            model_name="gemini-1.5-flash",
        )

    def _has_emergency(self, text: str) -> bool:
        tl = text.lower()
        return any(kw in tl for kw in EMERGENCY_KEYWORDS)

    def _sanitize(self, text: str) -> str:
        if not text:
            return text
        text = re.sub(
            r'\b(you have|you are suffering from|you are diagnosed with)\b',
            'this may be associated with',
            text, flags=re.IGNORECASE,
        )
        text = re.sub(
            r'\btake (\d+)\s*(mg|ml|units?|tablets?|capsules?) of\b',
            r'dosage of \1 \2 of',
            text, flags=re.IGNORECASE,
        )
        return text

    async def validate_report(
        self,
        query: str,
        report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply safety validation to the structured answer.
        Works with both the new schema and the legacy 'executive_summary' schema.
        """
        is_emergency = self._has_emergency(query)

        # ── New structured-answer schema ──────────────────────────────────────
        if "direct_answer" in report:
            # Sanitize text fields
            for field in ("direct_answer", "what_this_means", "when_to_seek_help"):
                if report.get(field):
                    report[field] = self._sanitize(report[field])

            for i, step in enumerate(report.get("next_steps", [])):
                report["next_steps"][i] = self._sanitize(step)

            # Override safety_note with canonical text
            report["safety_note"] = SAFETY_NOTE

            # Emergency handling
            if is_emergency:
                report["emergency_detected"] = True
                report["emergency_warning"] = EMERGENCY_NOTICE
                # Prepend emergency notice to when_to_seek_help
                existing = report.get("when_to_seek_help", "")
                if EMERGENCY_NOTICE not in existing:
                    report["when_to_seek_help"] = EMERGENCY_NOTICE + (" " + existing if existing else "")
            else:
                report["emergency_detected"] = False

        else:
            # ── Legacy schema fallback (executive_summary, sections…) ──────────
            exec_summary = report.get("executive_summary", "")
            if is_emergency:
                report["emergency_warning"] = EMERGENCY_NOTICE
                report["emergency_detected"] = True
                if "IMPORTANT" not in exec_summary:
                    report["executive_summary"] = (
                        "⚠️ IMPORTANT: The symptoms described may require immediate medical attention. "
                        + exec_summary
                    )
            else:
                report["emergency_detected"] = False

            # Sanitize sections
            for section in report.get("sections", []):
                if "content" in section:
                    section["content"] = self._sanitize(section["content"])

        report["safety_validated"] = True
        logger.info("SafetyGuardAgent: safety validation complete.")
        return report

    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="ready",
            findings=[],
            raw_output="Safety guard ready. Use validate_report() for report validation.",
            execution_time_ms=0,
        )

    async def validate_findings(
        self, request: MedicalQueryRequest, challenges: List[Dict[str, Any]]
    ) -> MedicalAgentResponse:
        return await self.run(request)
