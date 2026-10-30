"""
AISIA Medical Backend Tests
Tests for medical domain restriction, safety screening, and orchestration workflow.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.medical.domain_guard import MedicalDomainGuard, medical_domain_guard
from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalFinding, MedicalSourceCitation,
    EvidenceGrade, MedicalDomain
)
from app.agents.safety_guard_agent import MedicalSafetyGuardAgent


# ── Domain Guard Tests ───────────────────────────────────────────────────────

class TestMedicalDomainGuard:

    def test_accepts_diabetes_query(self):
        result = medical_domain_guard.validate("What are the symptoms of Type 2 diabetes?")
        assert result.is_medical is True, f"Expected medical, got: {result.rejection_reason}"
        assert result.confidence > 0.5

    def test_accepts_medication_query(self):
        result = medical_domain_guard.validate("How does metformin work for diabetes?")
        assert result.is_medical is True

    def test_accepts_anatomy_query(self):
        result = medical_domain_guard.validate("What is the function of the pancreas?")
        assert result.is_medical is True

    def test_accepts_cardiology_query(self):
        result = medical_domain_guard.validate("What are the treatment options for hypertension?")
        assert result.is_medical is True

    def test_accepts_symptom_query(self):
        result = medical_domain_guard.validate("What causes fever and nausea?")
        assert result.is_medical is True

    def test_accepts_pharmacology_query(self):
        result = medical_domain_guard.validate("What are the side effects of antibiotics?")
        assert result.is_medical is True

    def test_rejects_finance_query(self):
        result = medical_domain_guard.validate("What is the current stock price of Apple?")
        assert result.is_medical is False
        assert result.rejection_reason is not None

    def test_rejects_military_query(self):
        result = medical_domain_guard.validate("Analyze the NATO military strategy for Eastern Europe")
        assert result.is_medical is False
        assert result.rejection_reason is not None

    def test_rejects_programming_query(self):
        result = medical_domain_guard.validate("Write a Python function to sort a list")
        assert result.is_medical is False

    def test_rejects_geopolitical_query(self):
        result = medical_domain_guard.validate("What is the geopolitical impact of the Taiwan Strait conflict?")
        assert result.is_medical is False

    def test_rejects_sports_query(self):
        result = medical_domain_guard.validate("Who won the FIFA World Cup this year?")
        assert result.is_medical is False

    def test_rejects_empty_query(self):
        result = medical_domain_guard.validate("")
        assert result.is_medical is False

    def test_rejects_very_short_query(self):
        result = medical_domain_guard.validate("hi")
        assert result.is_medical is False


# ── Emergency Screening Tests ────────────────────────────────────────────────

class TestEmergencyScreening:

    def test_detects_chest_pain(self):
        result = medical_domain_guard.validate(
            "I have severe chest pain and my left arm hurts"
        )
        # Emergency queries are still medical — just flagged
        assert result.is_emergency is True
        assert result.emergency_message is not None
        assert "emergency" in result.emergency_message.lower() or "urgent" in result.emergency_message.lower()

    def test_detects_stroke_symptoms(self):
        result = medical_domain_guard.validate(
            "Sudden facial droop and speech difficulty — possible stroke?"
        )
        assert result.is_emergency is True

    def test_detects_overdose(self):
        result = medical_domain_guard.validate(
            "Patient took drug overdose — what to do?"
        )
        assert result.is_emergency is True

    def test_normal_medical_query_not_emergency(self):
        result = medical_domain_guard.validate(
            "What are the long-term effects of statin medications?"
        )
        assert result.is_emergency is False


# ── Medical Domain Detection Tests ──────────────────────────────────────────

class TestDomainDetection:

    def test_detects_cardiology_domain(self):
        result = medical_domain_guard.validate("What causes arrhythmia and how is it treated?")
        assert result.is_medical is True
        assert "Cardiology" in result.detected_domains

    def test_detects_pharmacology_domain(self):
        result = medical_domain_guard.validate("What are the drug interactions of warfarin?")
        assert result.is_medical is True

    def test_detects_neurology_domain(self):
        result = medical_domain_guard.validate("What is the difference between Parkinson's and Alzheimer's?")
        assert result.is_medical is True
        assert "Neurology" in result.detected_domains


# ── Safety Guard Agent Tests ─────────────────────────────────────────────────

class TestSafetyGuardAgent:

    def test_adds_disclaimer_to_report(self):
        import asyncio
        guard = MedicalSafetyGuardAgent()
        report = {
            "title": "Test Report",
            "executive_summary": "This is a test medical summary.",
            "sections": [],
            "key_findings": []
        }
        validated = asyncio.run(guard.validate_report("diabetes treatment", report))
        assert "safety_disclaimer" in validated
        assert validated.get("safety_validated") is True

    def test_adds_emergency_notice_for_emergency_query(self):
        import asyncio
        guard = MedicalSafetyGuardAgent()
        report = {
            "title": "Chest Pain Report",
            "executive_summary": "Information about chest pain.",
            "sections": [],
        }
        validated = asyncio.run(guard.validate_report("I have severe chest pain", report))
        assert "emergency_warning" in validated

    def test_adds_safety_section(self):
        import asyncio
        guard = MedicalSafetyGuardAgent()
        report = {
            "title": "Test Report",
            "executive_summary": "Summary.",
            "sections": [
                {"title": "Overview", "content": "Content", "section_type": "overview"}
            ],
        }
        validated = asyncio.run(guard.validate_report("what causes fever", report))
        section_types = [s.get("section_type") for s in validated.get("sections", [])]
        assert "safety" in section_types

    def test_sanitizes_direct_diagnosis(self):
        import asyncio
        guard = MedicalSafetyGuardAgent()
        report = {
            "title": "Test",
            "executive_summary": "Summary.",
            "sections": [
                {
                    "title": "Analysis",
                    "content": "You have Type 2 diabetes based on your symptoms.",
                    "section_type": "overview"
                }
            ],
        }
        validated = asyncio.run(guard.validate_report("do i have diabetes", report))
        # The direct diagnosis phrase should be replaced
        content = validated["sections"][0]["content"]
        assert "you have" not in content.lower() or "may be associated with" in content.lower()


# ── Medical Schema Tests ─────────────────────────────────────────────────────

class TestMedicalSchemas:

    def test_medical_finding_creation(self):
        source = MedicalSourceCitation(
            id="s1",
            title="WHO Guideline",
            source_type="WHO Clinical Guideline",
            grade=EvidenceGrade.GRADE_A,
            snippet="Type 2 diabetes management guidelines",
            is_ai_generated=False
        )
        finding = MedicalFinding(
            id="f1",
            statement="Type 2 diabetes is managed with lifestyle changes and medication.",
            confidence_score=0.90,
            sources=[source],
            domain=MedicalDomain.ENDOCRINOLOGY,
            agent_id="literature_agent",
            finding_type="informational"
        )
        assert finding.confidence_score == 0.90
        assert finding.domain == MedicalDomain.ENDOCRINOLOGY
        assert finding.sources[0].grade == EvidenceGrade.GRADE_A
        assert finding.disclaimer is not None

    def test_medical_query_request(self):
        req = MedicalQueryRequest(
            query="What causes hypertension?",
            session_id="test_session_001",
            max_validation_rounds=1
        )
        assert req.query == "What causes hypertension?"
        assert req.session_id == "test_session_001"

    def test_confidence_score_bounds(self):
        """Confidence score must be between 0.0 and 1.0"""
        with pytest.raises(Exception):
            MedicalFinding(
                id="f_invalid",
                statement="Test",
                confidence_score=1.5,  # > 1.0 — should fail
                sources=[],
                domain=MedicalDomain.GENERAL_MEDICINE,
                agent_id="test_agent",
                finding_type="informational"
            )


# ── Workflow Tests ─────────────────────────────────────────────────────────

class TestMedicalWorkflow:

    def test_workflow_creation(self):
        """Test that the medical workflow graph can be created without errors."""
        from app.orchestrator.medical_workflow import create_medical_workflow
        workflow = create_medical_workflow()
        assert workflow is not None

    def test_workflow_executes_medical_query(self):
        """Test end-to-end workflow execution with a medical query."""
        import asyncio
        from app.orchestrator.medical_workflow import create_medical_workflow

        async def _run():
            workflow = create_medical_workflow()
            request = MedicalQueryRequest(
                query="What are the symptoms and treatment of Type 2 diabetes?",
                session_id="test_workflow_medical"
            )
            state = {
                "request": request,
                "all_findings": [],
                "agent_responses": {},
                "contradictions": [],
                "evidence_gaps": [],
                "validation_round": 0,
                "final_report": {},
                "confidence_metrics": {},
                "agent_events": [],
                "emergency_detected": False,
            }
            return await workflow.ainvoke(state)

        result = asyncio.run(_run())
        assert "final_report" in result
        report = result["final_report"]
        assert "title" in report
        assert "executive_summary" in report
        assert "safety_disclaimer" in report
        assert len(result.get("all_findings", [])) > 0


# ── Specialized Agent Tests ──────────────────────────────────────────────────

class TestSpecializedAgents:

    def test_clinical_agent_run(self):
        import asyncio
        from app.agents.clinical_agent import ClinicalAnalysisAgent
        agent = ClinicalAnalysisAgent()
        req = MedicalQueryRequest(
            query="Clinical presentation and pathophysiology of heart failure",
            session_id="test_clin_01"
        )
        resp = asyncio.run(agent.run(req))
        assert resp.status == "success"
        assert len(resp.findings) > 0
        assert resp.findings[0].domain in [MedicalDomain.CARDIOLOGY, MedicalDomain.GENERAL_MEDICINE]

    def test_medication_agent_run(self):
        import asyncio
        from app.agents.medication_agent import MedicationReferenceAgent
        agent = MedicationReferenceAgent()
        req = MedicalQueryRequest(
            query="Mechanism of action and contraindications of metformin",
            session_id="test_med_01"
        )
        resp = asyncio.run(agent.run(req))
        assert resp.status == "success"
        assert len(resp.findings) > 0
        assert resp.findings[0].domain == MedicalDomain.PHARMACOLOGY

    def test_evidence_validation_agent_review(self):
        import asyncio
        from app.agents.evidence_agent import MedicalEvidenceValidationAgent
        agent = MedicalEvidenceValidationAgent()
        req = MedicalQueryRequest(query="Diabetes therapy", session_id="test_ev_01")
        sample_src = MedicalSourceCitation(
            id="src_test",
            title="AI Fallback Content",
            grade=EvidenceGrade.GRADE_C,
            is_ai_generated=True
        )
        findings = [
            MedicalFinding(
                id="f_test_01",
                statement="Metformin suppresses hepatic gluconeogenesis.",
                confidence_score=0.88,
                sources=[sample_src],
                domain=MedicalDomain.PHARMACOLOGY,
                agent_id="medication_agent",
                finding_type="medication_reference"
            )
        ]
        review = asyncio.run(agent.review_findings(req, findings))
        assert "challenges" in review
        assert "contradictions" in review
        assert "evidence_gaps" in review

