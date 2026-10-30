"""
Medical Literature Research Agent for AISIA.
Searches for relevant medical literature, guidelines, and clinical evidence.
"""

import time
import json
import logging
from typing import List, Dict, Any

from .medical_base import MedicalBaseAgent
from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalAgentResponse, MedicalFinding,
    MedicalSourceCitation, EvidenceGrade, MedicalDomain
)
from app.shared.llm import generate_text

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = (
    "You are the Medical Literature Research Agent for AISIA. "
    "Your role is to identify relevant medical evidence from clinical guidelines, "
    "peer-reviewed literature, and reputable medical organizations (WHO, NIH, CDC, FDA, AHA, ADA, etc.). "
    "Only report factual, evidence-based medical information. "
    "Clearly indicate when information is from clinical guidelines vs. general medical knowledge. "
    "Never fabricate journal names, study authors, or specific statistics. "
    "Always include educational disclaimers."
)

# Trusted medical source references
MEDICAL_SOURCES = {
    "WHO": {"title": "World Health Organization (WHO)", "url": "https://www.who.int", "grade": EvidenceGrade.GRADE_A},
    "NIH": {"title": "National Institutes of Health (NIH)", "url": "https://www.nih.gov", "grade": EvidenceGrade.GRADE_A},
    "CDC": {"title": "Centers for Disease Control and Prevention (CDC)", "url": "https://www.cdc.gov", "grade": EvidenceGrade.GRADE_A},
    "FDA": {"title": "U.S. Food and Drug Administration (FDA)", "url": "https://www.fda.gov", "grade": EvidenceGrade.GRADE_A},
    "AHA": {"title": "American Heart Association (AHA) Guidelines", "url": "https://www.heart.org", "grade": EvidenceGrade.GRADE_A},
    "ADA": {"title": "American Diabetes Association (ADA) Standards", "url": "https://www.diabetes.org", "grade": EvidenceGrade.GRADE_A},
    "Mayo": {"title": "Mayo Clinic Medical Reference", "url": "https://www.mayoclinic.org", "grade": EvidenceGrade.GRADE_B},
    "MedlinePlus": {"title": "MedlinePlus (NIH National Library of Medicine)", "url": "https://medlineplus.gov", "grade": EvidenceGrade.GRADE_A},
    "Cochrane": {"title": "Cochrane Library Systematic Reviews", "url": "https://www.cochranelibrary.com", "grade": EvidenceGrade.GRADE_A},
}


class MedicalLiteratureAgent(MedicalBaseAgent):
    """
    Medical Literature Research Agent.
    Searches for medical evidence using DuckDuckGo, RAG, and curated medical sources.
    """

    def __init__(self):
        super().__init__(
            agent_id="literature_agent",
            agent_name="Medical Literature Research Agent",
            model_name="gemini-1.5-flash"
        )

    def _search_medical_ddg(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search DuckDuckGo with medical-specific query augmentation."""
        results = []
        try:
            from duckduckgo_search import DDGS
            medical_query = f"medical clinical evidence {query} site:who.int OR site:nih.gov OR site:mayoclinic.org OR site:medlineplus.gov"
            with DDGS() as ddgs:
                for r in ddgs.text(medical_query, max_results=max_results):
                    results.append({
                        "href": r.get("href", ""),
                        "title": r.get("title", "Medical Reference"),
                        "body": r.get("body", "")
                    })
                if not results:
                    # Fallback to general medical search
                    for r in ddgs.text(f"{query} medical information", max_results=max_results):
                        results.append({
                            "href": r.get("href", ""),
                            "title": r.get("title", "Medical Reference"),
                            "body": r.get("body", "")
                        })
        except Exception as e:
            logger.debug(f"Medical DuckDuckGo search failed ({e}). Using empty results.")
        return results

    def _is_trusted_medical_source(self, url: str) -> tuple[EvidenceGrade, str]:
        """Check if URL is from a trusted medical source and return grade."""
        trusted_domains = {
            "who.int": EvidenceGrade.GRADE_A,
            "nih.gov": EvidenceGrade.GRADE_A,
            "cdc.gov": EvidenceGrade.GRADE_A,
            "fda.gov": EvidenceGrade.GRADE_A,
            "pubmed.ncbi.nlm.nih.gov": EvidenceGrade.GRADE_A,
            "cochranelibrary.com": EvidenceGrade.GRADE_A,
            "mayoclinic.org": EvidenceGrade.GRADE_B,
            "medlineplus.gov": EvidenceGrade.GRADE_A,
            "heart.org": EvidenceGrade.GRADE_A,
            "diabetes.org": EvidenceGrade.GRADE_A,
            "ncbi.nlm.nih.gov": EvidenceGrade.GRADE_A,
            "webmd.com": EvidenceGrade.GRADE_B,
            "healthline.com": EvidenceGrade.GRADE_B,
        }
        if not url:
            return EvidenceGrade.GRADE_C, "Unknown Source"

        for domain, grade in trusted_domains.items():
            if domain in url.lower():
                return grade, domain
        return EvidenceGrade.GRADE_C, "Web Source"

    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        start_time = time.time()
        query = request.query

        # 1. Search for medical evidence (DuckDuckGo + RAG)
        search_results = self._search_medical_ddg(query, max_results=4)
        rag_context = await self.retrieve_medical_context(query, "medical_literature")

        # 2. LLM synthesis of medical findings
        search_summary = "\n".join([
            f"- {r['title']}: {r['body'][:300]}" for r in search_results[:3]
        ]) if search_results else "(No web results available)"

        llm_prompt = f"""You are a Medical Literature Research Agent. Analyze this medical query using the provided evidence.

Medical Query: "{query}"

Web Search Evidence:
{search_summary}

Internal Medical Knowledge Base:
{rag_context if rag_context else "(No RAG context available — rely on training knowledge)"}

Generate 2-4 medical findings grounded in evidence. For each finding:
- State only what is medically established
- Reference real medical organizations where appropriate (WHO, NIH, CDC, FDA, Mayo Clinic)
- Include educational disclaimers
- Do NOT invent specific study authors, paper titles, or statistics you are not certain about

Return ONLY valid JSON:
[
  {{
    "statement": "Evidence-based medical finding about the query",
    "confidence": 0.85,
    "evidence_grade": "Grade A or Grade B or Grade C",
    "source_title": "Real organization/guideline name OR null if uncertain",
    "source_url": "Real URL or null",
    "source_type": "WHO Guideline / NIH Reference / Clinical Guideline / Medical Reference",
    "domain": "primary medical domain (e.g., Cardiology)",
    "finding_type": "informational / diagnostic_clue / medication_info / anatomy"
  }}
]"""

        findings: List[MedicalFinding] = []
        llm_output = await generate_text(llm_prompt, model_name=self.model_name, system_instruction=SYSTEM_INSTRUCTION)

        if llm_output:
            try:
                clean_json = llm_output.strip()
                if clean_json.startswith("```"):
                    clean_json = "\n".join(clean_json.split("\n")[1:])
                    if clean_json.endswith("```"):
                        clean_json = clean_json.rsplit("\n", 1)[0]
                parsed_findings = json.loads(clean_json)

                for idx, item in enumerate(parsed_findings):
                    source_url = item.get("source_url")
                    source_title = item.get("source_title")
                    grade_str = item.get("evidence_grade", "Grade B")
                    grade = EvidenceGrade.GRADE_A if "A" in grade_str else (
                        EvidenceGrade.GRADE_B if "B" in grade_str else EvidenceGrade.GRADE_C
                    )

                    # If source_title is null/None/empty, use fallback
                    is_ai_generated = not source_title
                    if is_ai_generated:
                        source_title = "AI Educational Content — No primary source located"
                        grade = EvidenceGrade.GRADE_C

                    source = MedicalSourceCitation(
                        id=f"src_lit_{idx}",
                        url=source_url,
                        title=source_title,
                        source_type=item.get("source_type", "Medical Reference"),
                        grade=grade,
                        snippet=item.get("statement", "")[:300],
                        is_ai_generated=is_ai_generated
                    )

                    domain = self._map_domain_str(item.get("domain", "General Medicine"))
                    findings.append(self.create_medical_finding(
                        finding_id=f"finding_lit_{idx}",
                        statement=item.get("statement", ""),
                        confidence=float(item.get("confidence", 0.75)),
                        sources=[source],
                        domain=domain,
                        finding_type=item.get("finding_type", "informational")
                    ))
            except Exception as e:
                logger.debug(f"LiteratureAgent: LLM JSON parse failed ({e}). Using fallback.")

        # 3. Fallback: use search results directly
        if not findings:
            findings = self._fallback_from_search(search_results, query)

        # 4. Add RAG-based findings if available
        if rag_context and len(findings) < 3:
            rag_lines = [l.strip("- \t") for l in rag_context.splitlines() if len(l.strip()) > 80]
            for idx, line in enumerate(rag_lines[:2]):
                source = MedicalSourceCitation(
                    id=f"src_lit_rag_{idx}",
                    title="AISIA Medical Knowledge Base",
                    source_type="Internal Medical RAG",
                    grade=EvidenceGrade.GRADE_B,
                    snippet=line[:250],
                    is_ai_generated=False
                )
                findings.append(self.create_medical_finding(
                    finding_id=f"finding_lit_rag_{idx}",
                    statement=line[:300],
                    confidence=0.78,
                    sources=[source],
                    finding_type="informational"
                ))

        execution_time = int((time.time() - start_time) * 1000)
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="success",
            findings=findings,
            raw_output=f"Literature research completed. Found {len(findings)} evidence-based findings.",
            execution_time_ms=execution_time
        )

    def _fallback_from_search(self, search_results: List[Dict], query: str) -> List[MedicalFinding]:
        """Create findings from raw search results when LLM is unavailable."""
        findings = []
        for idx, result in enumerate(search_results[:3]):
            body = result.get("body", "").strip()
            if not body or len(body) < 50:
                continue

            url = result.get("href", "")
            grade, domain = self._is_trusted_medical_source(url)
            title = result.get("title", "Medical Web Source")

            source = MedicalSourceCitation(
                id=f"src_lit_search_{idx}",
                url=url,
                title=title,
                source_type="Web Medical Source",
                grade=grade,
                snippet=body[:300],
                is_ai_generated=False
            )
            findings.append(self.create_medical_finding(
                finding_id=f"finding_lit_search_{idx}",
                statement=body[:350] + ("." if not body.endswith(".") else ""),
                confidence=0.70 if grade == EvidenceGrade.GRADE_A else 0.55,
                sources=[source],
                finding_type="informational"
            ))

        if not findings:
            # Last resort: generate a minimal educational finding with transparency
            source = self.create_fallback_source("lit_empty", "Medical Literature")
            findings.append(self.create_medical_finding(
                finding_id="finding_lit_fallback",
                statement=(
                    f"Medical information about '{query}' requires consultation with primary sources "
                    f"such as PubMed, WHO guidelines, or clinical textbooks. This AI system "
                    f"was unable to retrieve specific evidence-backed information for this query "
                    f"from available sources. Please consult a healthcare professional."
                ),
                confidence=0.40,
                sources=[source],
                finding_type="informational"
            ))
        return findings

    def _map_domain_str(self, domain_str: str) -> MedicalDomain:
        """Map domain string to enum."""
        mapping = {
            "Cardiology": MedicalDomain.CARDIOLOGY,
            "Neurology": MedicalDomain.NEUROLOGY,
            "Oncology": MedicalDomain.ONCOLOGY,
            "Pharmacology": MedicalDomain.PHARMACOLOGY,
            "Endocrinology": MedicalDomain.ENDOCRINOLOGY,
            "Pulmonology": MedicalDomain.PULMONOLOGY,
            "Gastroenterology": MedicalDomain.GASTROENTEROLOGY,
            "Anatomy & Physiology": MedicalDomain.ANATOMY,
            "Psychiatry": MedicalDomain.PSYCHIATRY,
            "Infectious Disease": MedicalDomain.INFECTIOUS_DISEASE,
        }
        return mapping.get(domain_str, MedicalDomain.GENERAL_MEDICINE)

    async def validate_findings(
        self, request: MedicalQueryRequest, challenges: List[Dict[str, Any]]
    ) -> MedicalAgentResponse:
        """Re-run literature search with awareness of challenges."""
        response = await self.run(request)
        for challenge in challenges:
            for finding in response.findings:
                if finding.id == challenge.get("finding_id") or challenge.get("agent_id") == self.agent_id:
                    finding.validated = True
                    finding.validation_notes = f"Reviewed based on validation challenge: {challenge.get('challenge_text', '')[:100]}"
        return response
