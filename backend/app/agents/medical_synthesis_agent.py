"""
Medical Report Synthesis Agent for AISIA.
Synthesizes all validated medical findings into a structured, user-friendly answer.
Output schema: direct_answer, what_this_means, next_steps, when_to_seek_help,
               sources, safety_note, evidence_details.
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional

from .medical_base import MedicalBaseAgent
from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalAgentResponse, MedicalFinding, MedicalDomain
)
from app.shared.llm import generate_text

logger = logging.getLogger(__name__)

# ── System instruction ───────────────────────────────────────────────────────
SYSTEM_INSTRUCTION = (
    "You are AISIA, a clear and helpful medical information assistant. "
    "Your job is to answer the user's medical question directly and honestly, "
    "using only the validated medical findings provided to you. "
    "Write in plain, everyday language — no jargon, no internal processing details. "
    "Never fabricate citations, statistics, or clinical claims. "
    "If evidence is insufficient, say so honestly instead of inventing information. "
    "Distinguish general guideline information from personalised medical advice."
)


class MedicalSynthesisAgent(MedicalBaseAgent):
    """
    Medical Report Synthesis Agent.
    Compiles all validated medical findings into a structured, user-facing answer.

    Output keys
    -----------
    direct_answer       : str  — 1-3 sentence answer to the question.
    what_this_means     : str  — Plain-language explanation.
    next_steps          : list — Actionable bullet points.
    when_to_seek_help   : str  — Safety trigger paragraph (present if relevant).
    sources             : list — [{title, url, org, date}] verified citations only.
    safety_note         : str  — One brief disclaimer sentence.
    evidence_details    : dict — Full findings, contradictions, gaps (for power users).
    """

    def __init__(self):
        super().__init__(
            agent_id="synthesis_agent",
            agent_name="Medical Report Synthesis Agent",
            model_name="gemini-1.5-pro"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def compile_medical_report(
        self,
        request: MedicalQueryRequest,
        all_findings: List[MedicalFinding],
        contradictions: List[str] = None,
        evidence_gaps: List[str] = None,
    ) -> Dict[str, Any]:
        """Compile all medical findings into a structured, user-friendly answer."""
        query = request.query
        contradictions = contradictions or []
        evidence_gaps = evidence_gaps or []

        # Extract real (non-AI-generated) sources
        real_sources = self._collect_real_sources(all_findings)
        has_real_evidence = len(real_sources) > 0 and len(all_findings) > 0

        # Build findings summary for LLM
        findings_summary = [
            {
                "statement": f.statement,
                "agent": f.agent_id,
                "confidence": round(f.confidence_score, 2),
                "domain": f.domain.value if hasattr(f.domain, "value") else str(f.domain),
                "sources": [
                    {"title": s.title, "url": s.url or "", "org": getattr(s, "organization", ""), "date": getattr(s, "publication_date", "")}
                    for s in f.sources if not s.is_ai_generated
                ],
                "validated": f.validated,
            }
            for f in all_findings
        ]

        llm_prompt = self._build_prompt(query, findings_summary, contradictions, evidence_gaps, has_real_evidence)
        llm_output = await generate_text(llm_prompt, model_name=self.model_name, system_instruction=SYSTEM_INSTRUCTION)

        if llm_output:
            parsed = self._parse_llm_json(llm_output)
            if parsed:
                return self._enrich_response(parsed, all_findings, real_sources, contradictions, evidence_gaps)

        # Heuristic fallback
        return self._heuristic_synthesis(query, all_findings, real_sources, contradictions, evidence_gaps)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _collect_real_sources(self, findings: List[MedicalFinding]) -> List[Dict[str, str]]:
        """Collect unique, non-AI-generated source citations across all findings."""
        seen_titles: set = set()
        sources: List[Dict[str, str]] = []
        for f in findings:
            for s in f.sources:
                if s.is_ai_generated:
                    continue
                if s.title and s.title not in seen_titles:
                    seen_titles.add(s.title)
                    sources.append({
                        "title": s.title,
                        "url": s.url or "",
                        "org": getattr(s, "organization", ""),
                        "date": getattr(s, "publication_date", ""),
                    })
        return sources

    def _build_prompt(
        self,
        query: str,
        findings_summary: list,
        contradictions: list,
        evidence_gaps: list,
        has_real_evidence: bool,
    ) -> str:
        insufficient = not has_real_evidence or not findings_summary
        fallback_instruction = (
            'Because no reliable external sources were retrieved, set direct_answer to: '
            '"I could not find a reliable guideline source to support a specific recommendation right now. '
            'I can explain the general considerations, but cannot verify the exact recommendation. '
            'Please consult a qualified healthcare professional for personalised advice." '
            'Leave sources as an empty list.'
        ) if insufficient else ""

        return f"""Answer the user's medical question in a clear, user-friendly way using ONLY the evidence provided.

User Question: "{query}"

Validated Medical Findings:
{json.dumps(findings_summary, indent=2)}

Contradictions:
{json.dumps(contradictions, indent=2) if contradictions else "None"}

Evidence Gaps:
{json.dumps(evidence_gaps, indent=2) if evidence_gaps else "None"}

{fallback_instruction}

Return ONLY valid JSON — no markdown fences, no extra text:
{{
  "direct_answer": "1-3 sentences directly answering the question in plain language",
  "what_this_means": "A clear paragraph explaining what this means for the reader",
  "next_steps": [
    "Practical step 1",
    "Practical step 2",
    "Practical step 3"
  ],
  "when_to_seek_help": "Paragraph describing warning signs that require immediate or urgent care (omit if not relevant)",
  "safety_note": "One brief sentence: this is general information, not personal medical advice."
}}"""

    def _parse_llm_json(self, raw: str) -> Optional[Dict[str, Any]]:
        """Strip markdown fences and parse JSON."""
        try:
            clean = raw.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean.rsplit("\n", 1)[0]
            return json.loads(clean)
        except Exception as e:
            logger.debug(f"SynthesisAgent: JSON parse failed — {e}")
            return None

    def _enrich_response(
        self,
        parsed: Dict[str, Any],
        all_findings: List[MedicalFinding],
        real_sources: List[Dict[str, str]],
        contradictions: list,
        evidence_gaps: list,
    ) -> Dict[str, Any]:
        """Add sources and evidence_details to the LLM-generated answer."""
        # Ensure required keys exist
        parsed.setdefault("direct_answer", "")
        parsed.setdefault("what_this_means", "")
        parsed.setdefault("next_steps", [])
        parsed.setdefault("when_to_seek_help", "")
        parsed.setdefault("safety_note", "This information is for general educational purposes and does not replace professional medical advice.")

        parsed["sources"] = real_sources
        parsed["evidence_details"] = {
            "total_findings": len(all_findings),
            "high_confidence_findings": sum(1 for f in all_findings if f.confidence_score >= 0.80),
            "contradictions": contradictions,
            "evidence_gaps": evidence_gaps,
            "findings": [
                {
                    "statement": f.statement,
                    "agent": f.agent_id,
                    "confidence": round(f.confidence_score * 100),
                    "domain": f.domain.value if hasattr(f.domain, "value") else str(f.domain),
                    "validated": f.validated,
                }
                for f in all_findings
            ],
        }
        return parsed

    def _heuristic_synthesis(
        self,
        query: str,
        findings: List[MedicalFinding],
        real_sources: List[Dict[str, str]],
        contradictions: list,
        evidence_gaps: list,
    ) -> Dict[str, Any]:
        """Heuristic fallback when LLM is unavailable."""
        if not findings:
            direct_answer = (
                "I could not find a reliable guideline source to support a specific recommendation right now. "
                "I can explain the general considerations, but cannot verify the exact recommendation. "
                "Please consult a qualified healthcare professional for personalised advice."
            )
            next_steps = ["Consult a qualified healthcare professional for personalised guidance."]
        else:
            top = sorted(findings, key=lambda f: f.confidence_score, reverse=True)
            direct_answer = top[0].statement if top else "Please consult a healthcare professional for information about this topic."
            next_steps = [
                f.statement[:180] + ("..." if len(f.statement) > 180 else "")
                for f in top[1:4]
            ]
            if not next_steps:
                next_steps = ["Consult a qualified healthcare professional for personalised guidance."]

        return {
            "direct_answer": direct_answer,
            "what_this_means": (
                "Based on available medical information, the above answer summarises the key considerations. "
                "Individual circumstances vary, so the specifics may differ for your situation."
            ),
            "next_steps": next_steps,
            "when_to_seek_help": (
                "Seek immediate medical attention if you experience severe or rapidly worsening symptoms, "
                "difficulty breathing, chest pain, or any other signs of a medical emergency."
            ),
            "sources": real_sources,
            "safety_note": "This information is for general educational purposes and does not replace professional medical advice.",
            "evidence_details": {
                "total_findings": len(findings),
                "high_confidence_findings": sum(1 for f in findings if f.confidence_score >= 0.80),
                "contradictions": contradictions,
                "evidence_gaps": evidence_gaps,
                "findings": [
                    {
                        "statement": f.statement,
                        "agent": f.agent_id,
                        "confidence": round(f.confidence_score * 100),
                        "domain": f.domain.value if hasattr(f.domain, "value") else str(f.domain),
                        "validated": f.validated,
                    }
                    for f in findings
                ],
            },
        }

    # ── LangGraph run() interface ─────────────────────────────────────────────

    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        """Run synthesis on its own (not used in normal workflow)."""
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="not_applicable",
            findings=[],
            raw_output="Synthesis agent requires findings from other agents. Use compile_medical_report().",
            execution_time_ms=0,
        )

    async def validate_findings(
        self, request: MedicalQueryRequest, challenges: List[Dict[str, Any]]
    ) -> MedicalAgentResponse:
        return await self.run(request)
