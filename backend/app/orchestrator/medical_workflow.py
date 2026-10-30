"""
Medical Multi-Agent LangGraph Orchestration Workflow for AISIA.
Coordinates the full 7-agent medical pipeline with conditional dispatch,
iterative peer-review validation loops, and safety guardrails.
"""

import asyncio
import logging
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.medical.medical_schemas import (
    MedicalQueryRequest, MedicalAgentResponse, MedicalFinding, MedicalDomain
)
from app.agents.intake_agent import MedicalIntakeAgent
from app.agents.literature_agent import MedicalLiteratureAgent
from app.agents.clinical_agent import ClinicalAnalysisAgent
from app.agents.medication_agent import MedicationReferenceAgent
from app.agents.evidence_agent import MedicalEvidenceValidationAgent
from app.agents.medical_synthesis_agent import MedicalSynthesisAgent
from app.agents.safety_guard_agent import MedicalSafetyGuardAgent

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.utcnow().strftime("%H:%M:%S")


class MedicalOrchestratorState(TypedDict):
    request: MedicalQueryRequest
    all_findings: List[MedicalFinding]
    agent_responses: Dict[str, MedicalAgentResponse]
    challenges: List[Dict[str, Any]]
    contradictions: List[str]
    evidence_gaps: List[str]
    validation_round: int
    final_report: Dict[str, Any]
    confidence_metrics: Dict[str, Any]
    agent_events: List[Dict[str, Any]]
    emergency_detected: bool


# ── Full Medical Agent Registry ──────────────────────────────────────────────
MEDICAL_AGENT_REGISTRY = {
    "intake_agent":     (MedicalIntakeAgent,     "Medical Intake & Classification Agent", "gemini-1.5-flash"),
    "literature_agent": (MedicalLiteratureAgent, "Medical Literature Research Agent",     "gemini-1.5-flash"),
    "clinical_agent":   (ClinicalAnalysisAgent,   "Clinical Information Analysis Agent",   "gemini-1.5-flash"),
    "medication_agent": (MedicationReferenceAgent, "Medication Reference Agent",           "gemini-1.5-flash"),
    "evidence_agent":   (MedicalEvidenceValidationAgent, "Medical Evidence Validation Agent", "gemini-1.5-pro"),
    "synthesis_agent":  (MedicalSynthesisAgent,  "Medical Report Synthesis Agent",        "gemini-1.5-pro"),
    "safety_guard_agent": (MedicalSafetyGuardAgent, "Medical Safety Guard Agent",          "gemini-1.5-flash"),
}


async def medical_intake(state: MedicalOrchestratorState):
    """Stage 1: Classify the medical query and extract entities."""
    req = state["request"]
    agent_events: List[Dict[str, Any]] = list(state.get("agent_events", []))

    agent_events.append({
        "type": "agent_started",
        "time": _now(),
        "agent_id": "intake_agent",
        "agent_name": "Medical Intake & Classification Agent",
        "model": "gemini-1.5-flash",
        "message": "🏥 Medical Intake Agent: Classifying medical query, assessing domain, and routing agents..."
    })

    intake = MedicalIntakeAgent()
    response = await intake.run(req)

    for finding in response.findings:
        agent_events.append({
            "type": "agent_finding",
            "time": _now(),
            "agent_id": "intake_agent",
            "agent_name": "Medical Intake & Classification Agent",
            "model": "gemini-1.5-flash",
            "finding_id": finding.id,
            "statement": finding.statement,
            "confidence": round(finding.confidence_score * 100),
            "domain": finding.domain.value if hasattr(finding.domain, 'value') else str(finding.domain),
            "message": f"📋 Classification: {finding.statement[:120]}..."
        })

    agent_responses = dict(state.get("agent_responses", {}))
    agent_responses["intake_agent"] = response

    return {
        "agent_responses": agent_responses,
        "all_findings": list(state.get("all_findings", [])) + response.findings,
        "agent_events": agent_events,
    }


async def medical_research_dispatch(state: MedicalOrchestratorState):
    """
    Stage 2: Conditional parallel dispatch of research agents
    (Literature + Clinical + Medication) based on query context.
    """
    req = state["request"]
    agent_events: List[Dict[str, Any]] = list(state.get("agent_events", []))
    validation_round = state.get("validation_round", 0)
    q_lower = req.query.lower()

    # Determine which agents to conditionally invoke
    active_tasks = []
    task_agents = []
    selected = req.selected_agents

    # 1. Literature Agent
    use_literature = (selected is None and True) or (selected is not None and "literature_agent" in selected)
    if use_literature:
        lit_agent = MedicalLiteratureAgent()
        active_tasks.append(lit_agent.run(req))
        task_agents.append(("literature_agent", "Medical Literature Research Agent", "gemini-1.5-flash"))

    # 2. Clinical Analysis Agent
    has_clinical_intent = req.include_clinical_analysis or any(
        w in q_lower for w in ["symptom", "pain", "syndrome", "disease", "diagnos", "patholog", "stage", "risk", "condition", "fever", "heart", "brain"]
    )
    use_clinical = (selected is not None and "clinical_agent" in selected) or (selected is None and has_clinical_intent)
    if use_clinical:
        clin_agent = ClinicalAnalysisAgent()
        active_tasks.append(clin_agent.run(req))
        task_agents.append(("clinical_agent", "Clinical Information Analysis Agent", "gemini-1.5-flash"))

    # 3. Medication Reference Agent
    has_med_intent = req.include_medication_info or any(
        w in q_lower for w in ["drug", "medication", "pill", "tablet", "dose", "antibiotic", "statin", "insulin", "inhibitor", "pharma", "therapy", "metformin", "lisinopril", "aspirin"]
    )
    use_medication = (selected is not None and "medication_agent" in selected) or (selected is None and has_med_intent)
    if use_medication:
        med_agent = MedicationReferenceAgent()
        active_tasks.append(med_agent.run(req))
        task_agents.append(("medication_agent", "Medication Reference Agent", "gemini-1.5-flash"))

    # Broadcast agent start events
    for agent_id, display_name, model_name in task_agents:
        agent_events.append({
            "type": "agent_started",
            "time": _now(),
            "agent_id": agent_id,
            "agent_name": display_name,
            "model": model_name,
            "message": f"🔬 {display_name}: Deployed — gathering evidence-grounded findings..."
        })

    # Execute all active research agents concurrently
    responses = await asyncio.gather(*active_tasks, return_exceptions=True)

    all_findings = list(state.get("all_findings", []))
    agent_responses = dict(state.get("agent_responses", {}))

    for response in responses:
        if isinstance(response, Exception):
            logger.error(f"Medical research agent error: {response}")
            continue

        agent_responses[response.agent_id] = response
        all_findings.extend(response.findings)

        for finding in response.findings:
            agent_events.append({
                "type": "agent_finding",
                "time": _now(),
                "agent_id": response.agent_id,
                "agent_name": response.agent_name,
                "model": "gemini-1.5-flash",
                "finding_id": finding.id,
                "statement": finding.statement,
                "confidence": round(finding.confidence_score * 100),
                "sources": [s.title for s in finding.sources],
                "message": (
                    f"📚 [{response.agent_name}] Finding ({round(finding.confidence_score*100)}% conf): "
                    f"{finding.statement[:140]}{'...' if len(finding.statement) > 140 else ''}"
                )
            })

    return {
        "all_findings": all_findings,
        "agent_responses": agent_responses,
        "validation_round": validation_round + 1,
        "agent_events": agent_events,
    }


async def evidence_validation(state: MedicalOrchestratorState):
    """Stage 3: Peer-review validation by Medical Evidence Validation Agent."""
    agent_events: List[Dict[str, Any]] = list(state.get("agent_events", []))
    all_findings = list(state.get("all_findings", []))
    validation_round = state.get("validation_round", 1)

    req = state["request"]
    selected = req.selected_agents
    if selected is not None and "evidence_agent" not in selected:
        agent_events.append({
            "type": "evidence_validated",
            "time": _now(),
            "agent_id": "evidence_agent",
            "agent_name": "Medical Evidence Validation Agent",
            "model": "gemini-1.5-pro",
            "total_findings": len(all_findings),
            "contradictions": 0,
            "evidence_gaps": 0,
            "challenges_count": 0,
            "message": "⚡ Evidence Fact-Checker skipped per user configuration. Directing verified findings to synthesis."
        })
        return {
            "all_findings": all_findings,
            "challenges": [],
            "contradictions": [],
            "evidence_gaps": [],
            "agent_events": agent_events,
        }

    agent_events.append({
        "type": "agent_started",
        "time": _now(),
        "agent_id": "evidence_agent",
        "agent_name": "Medical Evidence Validation Agent",
        "model": "gemini-1.5-pro",
        "message": "🔍 Evidence Validation Agent: Auditing medical claims, detecting contradictions, and verifying evidence grades..."
    })

    validator = MedicalEvidenceValidationAgent()
    val_result = await validator.review_findings(state["request"], all_findings)

    challenges = val_result.get("challenges", [])
    contradictions = val_result.get("contradictions", [])
    evidence_gaps = val_result.get("evidence_gaps", [])
    updated_findings = val_result.get("updated_findings", all_findings)

    for ch in challenges:
        agent_events.append({
            "type": "evidence_challenged",
            "time": _now(),
            "agent_id": "evidence_agent",
            "agent_name": "Medical Evidence Validation Agent",
            "model": "gemini-1.5-pro",
            "target_finding_id": ch.get("finding_id"),
            "target_agent": ch.get("agent_id"),
            "message": f"⚠️ Evidence Challenge to [{ch.get('agent_id')}]: {ch.get('challenge_text')}"
        })

    agent_events.append({
        "type": "evidence_validated",
        "time": _now(),
        "agent_id": "evidence_agent",
        "agent_name": "Medical Evidence Validation Agent",
        "model": "gemini-1.5-pro",
        "total_findings": len(updated_findings),
        "contradictions": len(contradictions),
        "evidence_gaps": len(evidence_gaps),
        "challenges_count": len(challenges),
        "message": (
            f"✅ Evidence validation audit complete: {len(updated_findings)} findings checked, "
            f"{len(contradictions)} contradictions, {len(challenges)} targeted challenges."
        )
    })

    return {
        "all_findings": updated_findings,
        "challenges": challenges,
        "contradictions": contradictions,
        "evidence_gaps": evidence_gaps,
        "agent_events": agent_events,
    }


def should_refine(state: MedicalOrchestratorState) -> str:
    """Conditional edge: decides if a targeted re-run is warranted."""
    challenges = state.get("challenges", [])
    round_count = state.get("validation_round", 1)
    max_rounds = state.get("request").max_validation_rounds if state.get("request") else 1

    if challenges and round_count < max_rounds:
        logger.info(f"Medical LangGraph: Re-running challenged agents in round {round_count + 1}")
        return "challenge_review_dispatch"
    return "medical_synthesis"


async def challenge_review_dispatch(state: MedicalOrchestratorState):
    """Stage 3b: Re-runs challenged agents to nuance and verify their findings."""
    req = state["request"]
    challenges = state.get("challenges", [])
    all_findings = list(state.get("all_findings", []))
    agent_events: List[Dict[str, Any]] = list(state.get("agent_events", []))
    validation_round = state.get("validation_round", 1)

    agent_class_map = {
        "literature_agent": MedicalLiteratureAgent,
        "clinical_agent": ClinicalAnalysisAgent,
        "medication_agent": MedicationReferenceAgent,
    }

    challenged_agents = {c.get("agent_id") for c in challenges if c.get("agent_id") in agent_class_map}

    for agent_id in challenged_agents:
        cls = agent_class_map[agent_id]
        agent_instance = cls()
        agent_challenges = [c for c in challenges if c.get("agent_id") == agent_id]

        agent_events.append({
            "type": "agent_started",
            "time": _now(),
            "agent_id": agent_id,
            "agent_name": agent_instance.agent_name,
            "message": f"🔄 [{agent_instance.agent_name}] Revising findings in response to evidence challenges..."
        })

        revised_resp = await agent_instance.validate_findings(req, agent_challenges)
        for rev_f in revised_resp.findings:
            for idx, existing in enumerate(all_findings):
                if existing.id == rev_f.id:
                    all_findings[idx] = rev_f

    return {
        "all_findings": all_findings,
        "validation_round": validation_round + 1,
        "agent_events": agent_events,
        "challenges": []  # Cleared after review
    }


async def medical_synthesis(state: MedicalOrchestratorState):
    """Stage 4: Synthesize all findings into a structured medical report."""
    agent_events: List[Dict[str, Any]] = list(state.get("agent_events", []))
    all_findings = state.get("all_findings", [])
    contradictions = state.get("contradictions", [])
    evidence_gaps = state.get("evidence_gaps", [])

    agent_events.append({
        "type": "agent_started",
        "time": _now(),
        "agent_id": "synthesis_agent",
        "agent_name": "Medical Report Synthesis Agent",
        "model": "gemini-1.5-pro",
        "message": "📝 Medical Report Synthesis Agent: Compiling structured medical intelligence report..."
    })

    synthesis = MedicalSynthesisAgent()
    report = await synthesis.compile_medical_report(
        state["request"],
        all_findings,
        contradictions,
        evidence_gaps
    )

    if all_findings:
        avg_confidence = sum(f.confidence_score for f in all_findings) / len(all_findings)
        grade_a_count = sum(
            1 for f in all_findings
            if any(s.grade.value == "Grade A" for s in f.sources)
        )
    else:
        avg_confidence = 0.0
        grade_a_count = 0

    confidence_metrics = {
        "overall_score": round(avg_confidence, 2),
        "total_findings": len(all_findings),
        "grade_a_sources": grade_a_count,
        "contradictions": len(contradictions),
        "evidence_gaps": len(evidence_gaps),
    }

    agent_events.append({
        "type": "synthesis_complete",
        "time": _now(),
        "agent_id": "synthesis_agent",
        "agent_name": "Medical Report Synthesis Agent",
        "model": "gemini-1.5-pro",
        "total_findings": len(all_findings),
        "global_score": round(avg_confidence * 100),
        "message": (
            f"✅ Report synthesis complete — {len(all_findings)} findings synthesized with "
            f"overall evidence confidence {round(avg_confidence * 100)}%"
        )
    })

    return {
        "final_report": report,
        "confidence_metrics": confidence_metrics,
        "agent_events": agent_events,
    }


async def safety_validation(state: MedicalOrchestratorState):
    """Stage 5: Final safety validation, content sanitization, and disclaimer enforcement."""
    agent_events: List[Dict[str, Any]] = list(state.get("agent_events", []))
    final_report = state.get("final_report", {})

    agent_events.append({
        "type": "agent_started",
        "time": _now(),
        "agent_id": "safety_guard_agent",
        "agent_name": "Medical Safety Guard Agent",
        "model": "gemini-1.5-flash",
        "message": "🛡️ Safety Guard Agent: Applying clinical safety checks and mandatory disclaimers..."
    })

    safety_guard = MedicalSafetyGuardAgent()
    validated_report = await safety_guard.validate_report(
        state["request"].query,
        final_report
    )

    agent_events.append({
        "type": "safety_check",
        "time": _now(),
        "agent_id": "safety_guard_agent",
        "agent_name": "Medical Safety Guard Agent",
        "model": "gemini-1.5-flash",
        "message": "✅ Safety validation complete. Educational disclaimers and emergency screening verified."
    })

    return {
        "final_report": validated_report,
        "agent_events": agent_events,
    }


def create_medical_workflow():
    """Compiles the complete 7-agent medical LangGraph state machine with conditional routing."""
    workflow = StateGraph(MedicalOrchestratorState)

    workflow.add_node("medical_intake", medical_intake)
    workflow.add_node("medical_research_dispatch", medical_research_dispatch)
    workflow.add_node("evidence_validation", evidence_validation)
    workflow.add_node("challenge_review_dispatch", challenge_review_dispatch)
    workflow.add_node("medical_synthesis", medical_synthesis)
    workflow.add_node("safety_validation", safety_validation)

    workflow.set_entry_point("medical_intake")
    workflow.add_edge("medical_intake", "medical_research_dispatch")
    workflow.add_edge("medical_research_dispatch", "evidence_validation")

    # Conditional edge for peer-review debate loop
    workflow.add_conditional_edges(
        "evidence_validation",
        should_refine,
        {
            "challenge_review_dispatch": "challenge_review_dispatch",
            "medical_synthesis": "medical_synthesis"
        }
    )
    workflow.add_edge("challenge_review_dispatch", "medical_synthesis")
    workflow.add_edge("medical_synthesis", "safety_validation")
    workflow.add_edge("safety_validation", END)

    return workflow.compile()
