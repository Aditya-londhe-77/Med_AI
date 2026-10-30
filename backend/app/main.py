"""
AISIA — AI_Based_Strategic_Intelligence_Assistant
Medical AI Orchestration Platform — FastAPI Backend
"Evidence-Grounded Medical Intelligence"
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Query
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid
import logging
from typing import List, Dict, Any, Optional

load_dotenv()

from app.medical.domain_guard import medical_domain_guard
from app.medical.medical_schemas import MedicalQueryRequest
from app.orchestrator.medical_workflow import create_medical_workflow
from app.shared.websocket_manager import manager
from app.shared.llm import is_configured
from app.database.supabase_client import (
    log_query,
    log_query_complete,
    log_briefing,
    get_query_history,
    get_briefing_by_query_id
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize medical workflow
medical_orchestrator = create_medical_workflow()

app = FastAPI(
    title="AISIA Medical AI API",
    description=(
        "AI_Based_Strategic_Intelligence_Assistant — Medical AI Orchestration Platform. "
        "Evidence-Grounded Medical Intelligence. "
        "This API handles medical education, healthcare information, and clinical research queries ONLY."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for recent sessions
SESSION_CACHE: Dict[str, Dict[str, Any]] = {}


@app.get("/health")
async def health_check():
    """AISIA health check endpoint."""
    return {
        "status": "ok",
        "service": "aisia-medical-backend",
        "product": "AI_Based_Strategic_Intelligence_Assistant",
        "tagline": "Evidence-Grounded Medical Intelligence",
        "version": "1.0.0",
        "domain": "Medical AI Orchestration",
        "agents_ready": True,
        "llm_configured": is_configured()
    }


@app.get("/api/config")
async def get_system_config():
    """Returns AISIA system configuration and agent registry."""
    llm_active = is_configured()
    return {
        "platform": "AISIA — AI_Based_Strategic_Intelligence_Assistant",
        "domain": "Medical AI Orchestration",
        "agents": {
            "intake_agent": {
                "name": "Medical Intake & Classification Agent",
                "model": "gemini-1.5-flash",
                "status": "active"
            },
            "literature_agent": {
                "name": "Medical Literature Research Agent",
                "model": "gemini-1.5-flash",
                "status": "active"
            },
            "evidence_agent": {
                "name": "Medical Evidence Validation Agent",
                "model": "gemini-1.5-pro",
                "status": "active"
            },
            "synthesis_agent": {
                "name": "Medical Report Synthesis Agent",
                "model": "gemini-1.5-pro",
                "status": "active"
            },
            "safety_guard_agent": {
                "name": "Medical Safety Guard Agent",
                "model": "gemini-1.5-flash",
                "status": "active"
            }
        },
        "parameters": {
            "max_validation_rounds": 1,
            "evidence_grade_threshold": "Grade B",
            "graph_traversal_hops": 2,
            "timeout_seconds": 90
        },
        "integrations": {
            "neo4j": "medical_knowledge_graph",
            "chromadb": "medical_literature_corpus",
            "supabase": "medical_query_history",
            "llm": "active" if llm_active else "heuristic_fallback"
        },
        "domain_restriction": "MEDICAL_ONLY",
        "llm_configured": llm_active
    }


@app.get("/api/agents")
async def get_agents():
    """Returns list of registered AISIA medical agents."""
    return {
        "agents": [
            {
                "id": "intake_agent",
                "name": "Medical Intake & Classification Agent",
                "role": "Query classification and medical entity extraction",
                "model": "gemini-1.5-flash",
                "tools": ["Medical Domain Classifier", "Entity Extractor"],
                "status": "active"
            },
            {
                "id": "literature_agent",
                "name": "Medical Literature Research Agent",
                "role": "Evidence search from medical sources and guidelines",
                "model": "gemini-1.5-flash",
                "tools": ["DuckDuckGo Medical Search", "ChromaDB RAG", "Medical Source Filter"],
                "status": "active"
            },
            {
                "id": "evidence_agent",
                "name": "Medical Evidence Validation Agent",
                "role": "Evidence quality assessment and contradiction detection",
                "model": "gemini-1.5-pro",
                "tools": ["Evidence Grader", "Contradiction Detector"],
                "status": "active"
            },
            {
                "id": "synthesis_agent",
                "name": "Medical Report Synthesis Agent",
                "role": "Structured medical report compilation with citations",
                "model": "gemini-1.5-pro",
                "tools": ["Report Compiler", "Citation Formatter"],
                "status": "active"
            },
            {
                "id": "safety_guard_agent",
                "name": "Medical Safety Guard Agent",
                "role": "Final safety validation and disclaimer injection",
                "model": "gemini-1.5-flash",
                "tools": ["Safety Checker", "Disclaimer Injector", "Emergency Detector"],
                "status": "active"
            }
        ]
    }


@app.get("/api/history")
async def get_history(limit: int = 20, offset: int = 0):
    """Returns paginated medical query history."""
    records = await get_query_history(limit=limit, offset=offset)
    if not records and SESSION_CACHE:
        records = [
            {
                "id": qid,
                "query_text": data.get("query_text", ""),
                "status": data.get("status", "completed"),
                "created_at": data.get("created_at", ""),
                "domain": data.get("domain", "General Medicine")
            }
            for qid, data in list(SESSION_CACHE.items())[offset:offset + limit]
        ]
    return {"history": records, "limit": limit, "offset": offset}


@app.get("/api/medical/query/{query_id}")
@app.get("/api/query/{query_id}")
async def get_medical_query_result(query_id: str):
    """Returns the medical research report for a given session ID."""
    if query_id in SESSION_CACHE:
        cached = SESSION_CACHE[query_id]
        if cached.get("status") == "processing":
            return {"query_id": query_id, "status": "processing"}
        return cached

    db_briefing = await get_briefing_by_query_id(query_id)
    if db_briefing:
        raw_data = db_briefing.get("raw_data", {})
        return {
            "query_id": query_id,
            "status": "completed",
            "query_text": raw_data.get("title", "Medical Query"),
            "report": raw_data,
            "briefing": raw_data,  # backward compatibility
            "confidence": {"overall_score": db_briefing.get("confidence_score", 0)},
            "findings": raw_data.get("findings", []),
            "domain": raw_data.get("domain", "General Medicine"),
            "analysis_mode": raw_data.get("analysis_mode", "heuristic_fallback"),
            "llm_configured": raw_data.get("llm_configured", False),
        }

    raise HTTPException(
        status_code=404,
        detail=f"Medical research session '{query_id}' not found. It may still be processing."
    )


class MedicalQueryPayload(BaseModel):
    query: Optional[str] = None
    max_validation_rounds: Optional[int] = 1
    include_medication_info: Optional[bool] = True
    include_clinical_analysis: Optional[bool] = True
    selected_agents: Optional[List[str]] = None
    agents: Optional[List[str]] = None


# ── WebSocket event → message type mapping ───────────────────────────────────
_MEDICAL_EVENT_MAP = {
    "agent_started": "agent",
    "agent_finding": "finding",
    "evidence_validated": "evidence",
    "evidence_challenged": "challenge",
    "synthesis_complete": "system",
    "safety_check": "system",
}


async def run_medical_orchestrator(session_id: str, query_text: str, initial_state: dict):
    """
    Runs the AISIA medical multi-agent LangGraph orchestrator in the background.
    Streams real-time agent events to connected WebSocket clients.
    """
    await asyncio.sleep(0.6)

    llm_mode = "🤖 Gemini AI" if is_configured() else "⚠️ Heuristic Fallback (no API key)"
    analysis_mode = "gemini" if is_configured() else "heuristic_fallback"

    await manager.broadcast(session_id, {
        "type": "system",
        "message": f"🏥 Initializing AISIA Medical AI Orchestration... Mode: {llm_mode}",
        "progress": 5,
        "analysis_mode": analysis_mode,
        "llm_configured": is_configured(),
    })

    all_findings = []
    final_report = {}
    confidence_metrics = {}
    agent_events = []

    try:
        progress = 10
        async for output in medical_orchestrator.astream(initial_state):
            for node_name, state_update in output.items():
                new_events = state_update.get("agent_events", [])
                prev_event_count = len(initial_state.get("agent_events", []))

                for ev in new_events[prev_event_count:]:
                    ws_type = _MEDICAL_EVENT_MAP.get(ev.get("type", ""), "system")
                    payload: Dict[str, Any] = {
                        "type": ws_type,
                        "event": ev.get("type"),
                        "message": ev.get("message", ""),
                        "progress": progress,
                        "agent_id": ev.get("agent_id", ""),
                        "agent_name": ev.get("agent_name", ""),
                        "model": ev.get("model", ""),
                    }
                    if ev.get("type") == "agent_finding":
                        payload["finding_id"] = ev.get("finding_id")
                        payload["statement"] = ev.get("statement")
                        payload["confidence"] = ev.get("confidence")
                        payload["domain"] = ev.get("domain")
                        payload["sources"] = ev.get("sources", [])
                    elif ev.get("type") == "evidence_validated":
                        payload["total_findings"] = ev.get("total_findings")
                        payload["contradictions"] = ev.get("contradictions")
                        payload["evidence_gaps"] = ev.get("evidence_gaps")

                    await manager.broadcast(session_id, payload)

                initial_state["agent_events"] = new_events
                agent_events = list(new_events)

                if "final_report" in state_update and state_update["final_report"]:
                    final_report = state_update["final_report"]
                if "confidence_metrics" in state_update and state_update["confidence_metrics"]:
                    confidence_metrics = state_update["confidence_metrics"]
                if "all_findings" in state_update:
                    all_findings = state_update["all_findings"]

                progress = min(progress + 18, 95)

        if not final_report:
            raise RuntimeError("Medical synthesis agent returned no report.")

        final_report["agent_events"] = agent_events
        final_report["analysis_mode"] = analysis_mode
        final_report["llm_configured"] = is_configured()
        final_report["findings"] = [
            {
                "id": f.id,
                "statement": f.statement,
                "confidence_score": f.confidence_score,
                "domain": f.domain.value if hasattr(f.domain, "value") else str(f.domain),
                "agent_id": f.agent_id,
                "sources": [{"title": s.title, "grade": s.grade.value, "url": s.url, "is_ai_generated": s.is_ai_generated} for s in f.sources],
                "validated": f.validated,
                "disclaimer": f.disclaimer
            }
            for f in all_findings
        ]

        SESSION_CACHE[session_id] = {
            "query_id": session_id,
            "status": "completed",
            "query_text": query_text,
            "report": final_report,
            "briefing": final_report,  # backward compatibility
            "confidence": confidence_metrics,
            "findings": final_report.get("findings", []),
            "claims": final_report.get("findings", []),  # backward compatibility
            "agent_events": agent_events,
            "analysis_mode": analysis_mode,
            "llm_configured": is_configured(),
            "emergency_detected": final_report.get("emergency_detected", False),
            "emergency_warning": final_report.get("emergency_warning", SESSION_CACHE.get(session_id, {}).get("emergency_warning")),
            "domain": final_report.get("domain", SESSION_CACHE.get(session_id, {}).get("medical_domains", [""])[0] if SESSION_CACHE.get(session_id, {}).get("medical_domains") else ""),
        }

        overall_conf_pct = (
            round(confidence_metrics.get("overall_score", 0.85) * 100)
            if isinstance(confidence_metrics, dict)
            else 85
        )

        await manager.broadcast(session_id, {
            "type": "system",
            "event": "completed",
            "message": "✅ Medical research complete. Evidence-grounded report ready.",
            "progress": 100,
            "status": "completed",
            "report": final_report,
            "confidence": overall_conf_pct,
            "confidence_metrics": confidence_metrics
        })

        await log_query_complete(session_id, "completed")
        await log_briefing(session_id, final_report, confidence_metrics)

    except Exception as e:
        logger.error(f"AISIA orchestrator error: {e}", exc_info=True)
        await manager.broadcast(session_id, {
            "type": "system",
            "event": "error",
            "message": f"❌ Medical orchestration error: {str(e)}",
            "status": "failed"
        })
        SESSION_CACHE[session_id] = {
            **SESSION_CACHE.get(session_id, {}),
            "status": "failed",
            "error": str(e)
        }
        await log_query_complete(session_id, "failed")


@app.post("/api/medical/query")
@app.post("/api/query")
async def submit_medical_query(
    payload: MedicalQueryPayload,
    background_tasks: BackgroundTasks,
    query: Optional[str] = Query(None)
):
    """
    Submit a medical query to AISIA.
    Enforces medical-only domain restriction before dispatching to LangGraph.
    """
    query_text = query or payload.query
    if not query_text or not query_text.strip():
        raise HTTPException(status_code=400, detail="Medical query text is required.")

    # ── Medical domain validation (HARD GATE) ────────────────────────────────
    validation = medical_domain_guard.validate(query_text)
    if not validation.is_medical:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "MEDICAL_DOMAIN_RESTRICTION",
                "message": validation.rejection_reason,
                "platform": "AISIA is exclusively a Medical AI platform.",
                "suggestion": "Please ask a medical, healthcare, or biomedical science question."
            }
        )

    # ── Emergency fast-path ──────────────────────────────────────────────────
    emergency_warning = None
    if validation.is_emergency:
        emergency_warning = validation.emergency_message
        logger.warning(f"AISIA: Emergency symptom query detected for session processing.")

    session_id = str(uuid.uuid4())

    chosen_agents = payload.selected_agents or payload.agents

    request = MedicalQueryRequest(
        query=query_text,
        session_id=session_id,
        max_validation_rounds=payload.max_validation_rounds or 1,
        include_medication_info=payload.include_medication_info if payload.include_medication_info is not None else True,
        include_clinical_analysis=payload.include_clinical_analysis if payload.include_clinical_analysis is not None else True,
        selected_agents=chosen_agents,
    )

    initial_state = {
        "request": request,
        "all_findings": [],
        "agent_responses": {},
        "contradictions": [],
        "evidence_gaps": [],
        "validation_round": 0,
        "final_report": {},
        "confidence_metrics": {},
        "agent_events": [],
        "emergency_detected": validation.is_emergency,
    }

    SESSION_CACHE[session_id] = {
        "query_id": session_id,
        "status": "processing",
        "query_text": query_text,
        "report": {},
        "briefing": {},
        "confidence": {},
        "findings": [],
        "claims": [],
        "agent_events": [],
        "analysis_mode": "gemini" if is_configured() else "heuristic_fallback",
        "llm_configured": is_configured(),
        "emergency_warning": emergency_warning,
        "medical_domains": validation.detected_domains,
    }

    await log_query(session_id, query_text)
    background_tasks.add_task(run_medical_orchestrator, session_id, query_text, initial_state)

    response_data = {
        "message": "Medical research started",
        "query_id": session_id,
        "llm_configured": is_configured(),
        "medical_domains": validation.detected_domains,
        "platform": "AISIA — Evidence-Grounded Medical Intelligence"
    }

    if emergency_warning:
        response_data["emergency_warning"] = emergency_warning
        response_data["emergency_detected"] = True

    return response_data


@app.get("/api/knowledge/graph")
@app.get("/api/graph/subgraph")
async def get_medical_knowledge_graph(query: Optional[str] = None, hops: int = 2):
    """
    Returns medical knowledge graph nodes and relationships.
    Attempts live Neo4j query, falls back to sample medical graph.
    """
    try:
        from app.shared.neo4j_client import neo4j_client
        cypher = """
        MATCH (n)-[r]->(m)
        RETURN n.name as source_name, labels(n)[0] as source_type,
               type(r) as relationship,
               m.name as target_name, labels(m)[0] as target_type
        LIMIT 60
        """
        results = neo4j_client.query(cypher)
        if results:
            nodes_dict = {}
            links = []
            for row in results:
                src_name = row["source_name"] or "Entity"
                tgt_name = row["target_name"] or "Entity"
                src_type = row["source_type"] or "Condition"
                tgt_type = row["target_type"] or "Drug"
                rel = row["relationship"] or "RELATED_TO"
                if src_name not in nodes_dict:
                    nodes_dict[src_name] = {"id": src_name, "name": src_name, "type": src_type}
                if tgt_name not in nodes_dict:
                    nodes_dict[tgt_name] = {"id": tgt_name, "name": tgt_name, "type": tgt_type}
                links.append({"source": src_name, "target": tgt_name, "label": rel})
            return {"nodes": list(nodes_dict.values()), "links": links, "source": "neo4j_live"}
    except Exception as e:
        logger.debug(f"Neo4j medical graph unavailable ({e}). Serving sample medical graph.")

    # Sample medical knowledge graph (educational — not clinical data)
    sample_nodes = [
        {"id": "Type2Diabetes", "name": "Type 2 Diabetes Mellitus", "type": "Condition"},
        {"id": "Hypertension", "name": "Hypertension", "type": "Condition"},
        {"id": "Metformin", "name": "Metformin", "type": "Drug"},
        {"id": "Insulin", "name": "Insulin", "type": "Drug"},
        {"id": "Pancreas", "name": "Pancreas", "type": "Anatomy"},
        {"id": "Glucose", "name": "Blood Glucose", "type": "Biomarker"},
        {"id": "HbA1c", "name": "HbA1c", "type": "Biomarker"},
        {"id": "WHO", "name": "World Health Organization", "type": "Organization"},
        {"id": "ADA", "name": "American Diabetes Association", "type": "Organization"},
        {"id": "Obesity", "name": "Obesity", "type": "Condition"},
        {"id": "Cardiovascular", "name": "Cardiovascular Disease", "type": "Condition"},
        {"id": "AHA", "name": "American Heart Association", "type": "Organization"},
        {"id": "Lisinopril", "name": "Lisinopril (ACE Inhibitor)", "type": "Drug"},
        {"id": "Aspirin", "name": "Aspirin", "type": "Drug"},
        {"id": "Coronary", "name": "Coronary Artery Disease", "type": "Condition"},
        {"id": "NIH", "name": "National Institutes of Health", "type": "Organization"},
    ]

    sample_links = [
        {"source": "Type2Diabetes", "target": "Metformin", "label": "TREATED_BY"},
        {"source": "Type2Diabetes", "target": "Insulin", "label": "TREATED_BY"},
        {"source": "Pancreas", "target": "Insulin", "label": "PRODUCES"},
        {"source": "Type2Diabetes", "target": "Glucose", "label": "ELEVATES"},
        {"source": "Type2Diabetes", "target": "HbA1c", "label": "MONITORED_BY"},
        {"source": "ADA", "target": "Type2Diabetes", "label": "PUBLISHES_GUIDELINES_FOR"},
        {"source": "WHO", "target": "Type2Diabetes", "label": "TRACKS_PREVALENCE"},
        {"source": "Obesity", "target": "Type2Diabetes", "label": "RISK_FACTOR_FOR"},
        {"source": "Type2Diabetes", "target": "Cardiovascular", "label": "INCREASES_RISK_OF"},
        {"source": "Hypertension", "target": "Lisinopril", "label": "TREATED_BY"},
        {"source": "Cardiovascular", "target": "Aspirin", "label": "MANAGED_WITH"},
        {"source": "AHA", "target": "Cardiovascular", "label": "PUBLISHES_GUIDELINES_FOR"},
        {"source": "Hypertension", "target": "Cardiovascular", "label": "RISK_FACTOR_FOR"},
        {"source": "Coronary", "target": "Cardiovascular", "label": "TYPE_OF"},
        {"source": "NIH", "target": "Type2Diabetes", "label": "FUNDS_RESEARCH_ON"},
    ]

    return {
        "nodes": sample_nodes,
        "links": sample_links,
        "source": "aisia_sample_medical_graph",
        "note": "Sample educational medical knowledge graph. Connect Neo4j for live graph data."
    }


@app.websocket("/ws/{query_id}")
async def websocket_endpoint(websocket: WebSocket, query_id: str):
    """WebSocket endpoint for real-time AISIA medical agent updates."""
    await manager.connect(websocket, query_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, query_id)
    except Exception:
        manager.disconnect(websocket, query_id)
