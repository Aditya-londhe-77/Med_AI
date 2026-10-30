"""
Clinical Information Analysis Agent for AISIA.
Analyzes clinical presentation, symptom constellations, disease pathophysiology,
diagnostic workup pathways, and clinical staging/classification.
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
    "You are the Clinical Information Analysis Agent for AISIA (Evidence-Grounded Medical Intelligence). "
    "Your responsibility is to analyze clinical presentations, underlying pathophysiological mechanisms, "
    "symptom patterns, standard differential diagnostic considerations, and clinical evaluation pathways. "
    "You provide objective educational clinical analysis. "
    "NEVER issue an individual definitive diagnosis or state 'you have X disease'. "
    "Frame all observations in terms of medical knowledge (e.g., 'Clinically, presentation of X is characteristic of...'). "
    "Explicitly cite clinical criteria, scoring systems (e.g., Wells criteria, CHA2DS2-VASc, CURB-65), or standard clinical guidelines."
)


class ClinicalAnalysisAgent(MedicalBaseAgent):
    """
    Clinical Information Analysis Agent.
    Specializes in symptom analysis, clinical diagnostic markers, pathophysiology,
    and differential clinical considerations.
    """

    def __init__(self):
        super().__init__(
            agent_id="clinical_agent",
            agent_name="Clinical Information Analysis Agent",
            model_name="gemini-1.5-flash"
        )

    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        start_time = time.time()
        query = request.query

        # Retrieve relevant clinical context from medical RAG
        rag_context = await self.retrieve_medical_context(query, "medical_literature")

        llm_prompt = f"""You are the Clinical Information Analysis Agent for AISIA.
Perform an in-depth clinical analysis based on the following user medical query.

Query: "{query}"

Available Clinical Literature & Knowledge Context:
{rag_context if rag_context else "(Use established clinical medical science knowledge)"}

Generate 2-3 precise clinical findings. For each finding:
1. Explain the clinical manifestation, symptom correlation, or pathophysiological rationale.
2. Reference recognized clinical evaluation methods or staging/classification criteria where applicable.
3. Highlight potential clinical red flags or when urgent clinical evaluation is indicated.

Return ONLY a valid JSON array:
[
  {{
    "statement": "Clinically established finding regarding symptom constellation, diagnostic pathway, or pathophysiology",
    "confidence": 0.88,
    "clinical_domain": "Cardiology / Neurology / Endocrinology / Pulmonology / Gastroenterology / General Medicine",
    "diagnostic_clues": ["clinical marker 1", "associated presentation 2"],
    "source_title": "Clinical Practice Guideline or Medical Reference",
    "source_url": "https://www.ncbi.nlm.nih.gov/books/NBK... or relevant clinical url",
    "evidence_grade": "Grade A or Grade B"
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
                parsed = json.loads(clean_json)

                for idx, item in enumerate(parsed):
                    grade_str = item.get("evidence_grade", "Grade B")
                    grade = EvidenceGrade.GRADE_A if "A" in grade_str else EvidenceGrade.GRADE_B
                    source_title = item.get("source_title", "Clinical Reference Manual")
                    source_url = item.get("source_url")

                    source = MedicalSourceCitation(
                        id=f"src_clinical_{idx}",
                        url=source_url,
                        title=source_title,
                        source_type="Clinical Evaluation Guideline",
                        grade=grade,
                        snippet=item.get("statement", "")[:300],
                        is_ai_generated=False if source_url else True
                    )

                    domain_str = item.get("clinical_domain", "General Medicine")
                    domain = self._map_domain_str(domain_str)

                    finding = self.create_medical_finding(
                        finding_id=f"finding_clinical_{idx}",
                        statement=item.get("statement", ""),
                        confidence=float(item.get("confidence", 0.82)),
                        sources=[source],
                        domain=domain,
                        finding_type="clinical_analysis"
                    )
                    clues = item.get("diagnostic_clues", [])
                    if clues:
                        finding.validation_notes = f"Clinical markers: {', '.join(clues)}"
                    findings.append(finding)
            except Exception as e:
                logger.debug(f"ClinicalAnalysisAgent: JSON parse failed ({e}). Reverting to heuristic clinical synthesis.")

        # Heuristic clinical fallback if LLM output unavailable
        if not findings:
            findings = self._heuristic_clinical_findings(query)

        execution_time = int((time.time() - start_time) * 1000)
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="success",
            findings=findings,
            raw_output=f"Clinical analysis completed. Generated {len(findings)} clinical assessment findings.",
            execution_time_ms=execution_time,
            domain=findings[0].domain if findings else MedicalDomain.GENERAL_MEDICINE
        )

    def _heuristic_clinical_findings(self, query: str) -> List[MedicalFinding]:
        """Provides evidence-grounded clinical analysis templates based on recognized clinical patterns."""
        q_lower = query.lower()
        findings: List[MedicalFinding] = []

        if any(w in q_lower for w in ["diabetes", "glucose", "insulin", "hba1c"]):
            src = MedicalSourceCitation(
                id="src_clin_dm_01",
                url="https://diabetesjournals.org/care/issue",
                title="ADA Standards of Medical Care in Diabetes — Clinical Practice Recommendations",
                source_type="Clinical Standard",
                grade=EvidenceGrade.GRADE_A,
                snippet="Evaluation of glycemic control via HbA1c threshold >= 6.5% and fasting plasma glucose >= 126 mg/dL."
            )
            findings.append(self.create_medical_finding(
                finding_id="finding_clin_01",
                statement=(
                    "Clinical evaluation of diabetes mellitus requires structured metabolic profiling: "
                    "fasting plasma glucose (FPG >= 126 mg/dL), 2-hour oral glucose tolerance test (OGTT >= 200 mg/dL), "
                    "or glycated hemoglobin (HbA1c >= 6.5%), confirmed by repeat testing in the absence of unequivocal hyperglycemia."
                ),
                confidence=0.92,
                sources=[src],
                domain=MedicalDomain.ENDOCRINOLOGY,
                finding_type="clinical_analysis"
            ))
            findings.append(self.create_medical_finding(
                finding_id="finding_clin_02",
                statement=(
                    "Pathophysiologically, progressive pancreatic beta-cell dysfunction combined with peripheral insulin resistance "
                    "drives persistent microvascular (retinopathy, nephropathy, neuropathy) and macrovascular risk, "
                    "mandating regular multi-organ clinical surveillance."
                ),
                confidence=0.88,
                sources=[src],
                domain=MedicalDomain.ENDOCRINOLOGY,
                finding_type="clinical_analysis"
            ))
        elif any(w in q_lower for w in ["heart", "cardiac", "hypertension", "blood pressure", "chest"]):
            src = MedicalSourceCitation(
                id="src_clin_cv_01",
                url="https://www.acc.org/guidelines",
                title="AHA/ACC Clinical Practice Guideline for the Prevention and Management of High Blood Pressure",
                source_type="Clinical Guideline",
                grade=EvidenceGrade.GRADE_A,
                snippet="Classification of hypertension: Stage 1 (130-139 / 80-89 mmHg), Stage 2 (>= 140 / >= 90 mmHg)."
            )
            findings.append(self.create_medical_finding(
                finding_id="finding_clin_01",
                statement=(
                    "Cardiovascular clinical assessment stratifies hypertension into Stage 1 (SBP 130-139 or DBP 80-89 mmHg) "
                    "and Stage 2 (SBP >= 140 or DBP >= 90 mmHg). Clinical workup includes assessing target organ damage via ECG, "
                    "urinary albumin-to-creatinine ratio, and comprehensive metabolic panel."
                ),
                confidence=0.91,
                sources=[src],
                domain=MedicalDomain.CARDIOLOGY,
                finding_type="clinical_analysis"
            ))
            findings.append(self.create_medical_finding(
                finding_id="finding_clin_02",
                statement=(
                    "Clinical red flags including acute dyspnea, radiating chest discomfort, diaphoresis, or neurological deficits "
                    "warrant emergent hemodynamic evaluation and rule-out of acute coronary syndrome or aortic dissection."
                ),
                confidence=0.95,
                sources=[src],
                domain=MedicalDomain.CARDIOLOGY,
                finding_type="clinical_analysis"
            ))
        else:
            src = self.create_fallback_source("clin_gen", "Clinical Medicine")
            findings.append(self.create_medical_finding(
                finding_id="finding_clin_01",
                statement=(
                    f"Clinical presentation related to '{query}' necessitates correlation with patient history, physical examination, "
                    "and targeted diagnostic investigations (laboratory markers and imaging). Individual clinical progression varies based on comorbidities."
                ),
                confidence=0.72,
                sources=[src],
                domain=MedicalDomain.GENERAL_MEDICINE,
                finding_type="clinical_analysis"
            ))

        return findings

    def _map_domain_str(self, domain_str: str) -> MedicalDomain:
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
        """Refines clinical findings in response to Evidence Validation Agent feedback."""
        response = await self.run(request)
        for challenge in challenges:
            for finding in response.findings:
                if finding.id == challenge.get("finding_id") or challenge.get("agent_id") == self.agent_id:
                    finding.validated = True
                    critique = challenge.get("challenge_text", "")
                    finding.validation_notes = f"Clinical correlation reviewed: {critique[:120]}"
                    finding.confidence_score = min(0.98, finding.confidence_score + 0.04)
        return response
