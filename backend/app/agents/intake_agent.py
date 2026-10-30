"""
Medical Intake and Domain Classification Agent for AISIA.
Classifies the medical query into specific domains and structures the research intent.
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
    "You are the Medical Intake and Classification Agent for AISIA (AI-Based Strategic Intelligence Assistant). "
    "Your role is to classify medical queries into specific medical domains, identify the query intent, "
    "and extract key medical entities (conditions, drugs, symptoms, anatomy). "
    "You must only process medical and healthcare-related queries. "
    "Never provide direct medical diagnosis or treatment advice. "
    "Always use evidence-based medical terminology."
)


class MedicalIntakeAgent(MedicalBaseAgent):
    """
    Medical Intake and Domain Classification Agent.
    First agent in the pipeline — classifies the query and extracts key medical entities.
    """

    def __init__(self):
        super().__init__(
            agent_id="intake_agent",
            agent_name="Medical Intake & Classification Agent",
            model_name="gemini-1.5-flash"
        )

    async def run(self, request: MedicalQueryRequest) -> MedicalAgentResponse:
        start_time = time.time()
        query = request.query

        # LLM-based domain classification
        llm_prompt = f"""You are a medical domain classification system.

Analyze this medical query and classify it:
Query: "{query}"

Return ONLY valid JSON with this exact format:
{{
  "primary_domain": "one of: Cardiology, Neurology, Oncology, Pharmacology, Endocrinology, Pulmonology, Gastroenterology, Anatomy & Physiology, Psychiatry, Infectious Disease, Nephrology, Orthopedics, Dermatology, General Medicine, Pediatrics, Emergency Medicine",
  "secondary_domains": ["domain2", "domain3"],
  "query_intent": "one of: symptom_inquiry, condition_overview, medication_information, treatment_options, diagnostic_education, anatomy_explanation, research_literature, prevention_wellness",
  "key_entities": {{
    "conditions": ["condition1", "condition2"],
    "symptoms": ["symptom1"],
    "medications": ["drug1"],
    "anatomy": ["organ/structure"]
  }},
  "research_questions": ["specific medical question 1", "specific medical question 2"],
  "classification_confidence": 0.92
}}"""

        classification_data = None
        llm_output = await generate_text(llm_prompt, model_name=self.model_name, system_instruction=SYSTEM_INSTRUCTION)

        if llm_output:
            try:
                clean_json = llm_output.strip()
                if clean_json.startswith("```"):
                    clean_json = "\n".join(clean_json.split("\n")[1:])
                    if clean_json.endswith("```"):
                        clean_json = clean_json.rsplit("\n", 1)[0]
                classification_data = json.loads(clean_json)
            except Exception as e:
                logger.debug(f"IntakeAgent: Could not parse LLM JSON ({e}). Using keyword-based fallback.")

        # Fallback: keyword-based classification
        if not classification_data:
            classification_data = self._keyword_classify(query)

        # Build a classification finding
        primary_domain_str = classification_data.get("primary_domain", "General Medicine")
        query_intent = classification_data.get("query_intent", "condition_overview")
        research_questions = classification_data.get("research_questions", [query])
        key_entities = classification_data.get("key_entities", {})

        primary_domain = self._map_domain(primary_domain_str)

        classification_statement = (
            f"Query classified as: {primary_domain_str} — Intent: {query_intent.replace('_', ' ').title()}. "
            f"Key entities identified: "
            f"conditions={key_entities.get('conditions', [])}, "
            f"medications={key_entities.get('medications', [])}, "
            f"symptoms={key_entities.get('symptoms', [])}."
        )

        source = MedicalSourceCitation(
            id="src_intake_classification",
            title="AISIA Medical Domain Classification Engine",
            source_type="Internal Classification",
            grade=EvidenceGrade.GRADE_C,
            snippet=f"Medical domain: {primary_domain_str}",
            is_ai_generated=True
        )

        finding = self.create_medical_finding(
            finding_id="finding_intake_01",
            statement=classification_statement,
            confidence=classification_data.get("classification_confidence", 0.80),
            sources=[source],
            domain=primary_domain,
            finding_type="classification"
        )

        # Store classification data in finding for downstream agents
        finding.validation_notes = json.dumps({
            "primary_domain": primary_domain_str,
            "secondary_domains": classification_data.get("secondary_domains", []),
            "query_intent": query_intent,
            "key_entities": key_entities,
            "research_questions": research_questions[:3]
        })

        execution_time = int((time.time() - start_time) * 1000)
        return MedicalAgentResponse(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="success",
            findings=[finding],
            raw_output=f"Classification complete: {primary_domain_str} ({query_intent})",
            execution_time_ms=execution_time,
            domain=primary_domain
        )

    def _keyword_classify(self, query: str) -> dict:
        """Keyword-based fallback classification."""
        query_lower = query.lower()

        domain_map = {
            "Cardiology": ["heart", "cardiac", "cardiovascular", "blood pressure", "arrhythmia", "coronary"],
            "Neurology": ["brain", "neuron", "stroke", "seizure", "alzheimer", "parkinson", "nerve", "headache"],
            "Oncology": ["cancer", "tumor", "chemotherapy", "lymphoma", "leukemia", "malignant"],
            "Pharmacology": ["drug", "medication", "dose", "antibiotic", "side effect", "interaction"],
            "Endocrinology": ["diabetes", "insulin", "thyroid", "hormone", "adrenal"],
            "Pulmonology": ["lung", "asthma", "copd", "breathing", "respiratory", "pneumonia"],
            "Gastroenterology": ["stomach", "liver", "hepatitis", "bowel", "intestine", "colitis"],
            "Anatomy & Physiology": ["anatomy", "physiology", "organ", "tissue", "cell"],
            "Psychiatry": ["depression", "anxiety", "mental health", "schizophrenia"],
            "Infectious Disease": ["infection", "bacteria", "virus", "antibiotic", "sepsis", "covid"],
        }

        for domain, keywords in domain_map.items():
            if any(kw in query_lower for kw in keywords):
                return {
                    "primary_domain": domain,
                    "secondary_domains": [],
                    "query_intent": "condition_overview",
                    "key_entities": {"conditions": [], "symptoms": [], "medications": [], "anatomy": []},
                    "research_questions": [query],
                    "classification_confidence": 0.70
                }

        return {
            "primary_domain": "General Medicine",
            "secondary_domains": [],
            "query_intent": "condition_overview",
            "key_entities": {"conditions": [], "symptoms": [], "medications": [], "anatomy": []},
            "research_questions": [query],
            "classification_confidence": 0.60
        }

    def _map_domain(self, domain_str: str) -> MedicalDomain:
        """Map string domain to MedicalDomain enum."""
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
            "Nephrology": MedicalDomain.NEPHROLOGY,
            "Orthopedics": MedicalDomain.ORTHOPEDICS,
            "Dermatology": MedicalDomain.DERMATOLOGY,
            "Pediatrics": MedicalDomain.PEDIATRICS,
            "Emergency Medicine": MedicalDomain.EMERGENCY,
        }
        return mapping.get(domain_str, MedicalDomain.GENERAL_MEDICINE)

    async def validate_findings(
        self, request: MedicalQueryRequest, challenges: List[Dict[str, Any]]
    ) -> MedicalAgentResponse:
        """Intake agent doesn't need to revise classification findings."""
        return await self.run(request)
