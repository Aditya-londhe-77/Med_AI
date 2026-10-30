# AI_Based_Strategic_Intelligence_Assistant — Decisions Log

## DEC-001: Retain LangGraph Orchestration Framework
**Date:** 2026-10-12  
**Decision:** Retain LangGraph StateGraph workflow infrastructure and adapt it for medical multi-agent orchestration.  
**Rationale:** LangGraph's conditional edge routing, async dispatch, and state management are domain-agnostic and provide the exact framework needed for conditional medical agent routing.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-002: Retain FastAPI + WebSocket Infrastructure
**Date:** 2026-10-12  
**Decision:** Retain FastAPI REST + WebSocket architecture with medical endpoints.  
**Rationale:** FastAPI's async support, Pydantic validation, and existing WebSocket connection manager are robust and well-suited for streaming agent telemetry.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-003: Retain ChromaDB and Neo4j, Update Collections
**Date:** 2026-10-12  
**Decision:** Keep ChromaDB and Neo4j infrastructure. Replace old intelligence dossiers with clinical medical reference texts.  
**Rationale:** Vector similarity search and graph traversal provide hybrid RAG grounding for biomedical literature.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-004: Remove Financial and Geopolitical Agents
**Date:** 2026-10-12  
**Decision:** Remove `financial.py` and `geopolitical.py` agents entirely.  
**Rationale:** Financial stock ticker quotes and geopolitical crisis feeds have no medical utility.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-005: Transform Devil's Advocate to Medical Evidence Validation Agent
**Date:** 2026-10-12  
**Decision:** Adapt the adversarial challenge pattern into a clinical peer-reviewer that audits evidence grades (GRADE A/B/C) and identifies contradictions.  
**Rationale:** Maps directly to peer review and evidence validation in evidence-based medicine.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-006: Oxford CEBM & GRADE Evidence Calibration
**Date:** 2026-10-12  
**Decision:** Adopt GRADE framework (Grade A: RCTs/Guidelines, Grade B: Observational/Cohort, Grade C: Educational Synthesis) for all citations.  
**Rationale:** Ensures users can immediately distinguish clinical trial consensus from general educational background.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-007: Medical Domain Hard Gatekeeper at API Gateway
**Date:** 2026-10-12  
**Decision:** Enforce domain validation via `MedicalDomainGuard` in `/api/medical/query` before dispatching to LangGraph. Return HTTP 422 for non-medical topics.  
**Rationale:** Fails fast to prevent wasted compute and enforces product specialization.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-008: Pink and Purple Medical Design System
**Date:** 2026-10-12  
**Decision:** Design clean white and lavender surfaces with primary purple (`#7652D6`), deep purple (`#4B2B91`), and pink accent (`#E879B9`).  
**Rationale:** Replaces dark tactical war-room layouts with an inviting, professional healthcare SaaS visual language.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-009: Session Key Update to aisia_session
**Date:** 2026-10-12  
**Decision:** Update localStorage session clearance key from `aegis_session` to `aisia_session` with backward compatibility check.  
**Rationale:** Maintains continuity while adopting AISIA branding.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-010: No Physical Repository Rename
**Date:** 2026-10-12  
**Decision:** Physical directory remains as-is; internal package metadata, titles, and UI reflect AISIA.  
**Rationale:** Avoids breaking path dependencies, virtual environment binaries, or git remotes.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-011: Emergency Safety Fast-Path
**Date:** 2026-10-12  
**Decision:** Emergency symptom detection returns an instant urgent-care advisory card before running research agents.  
**Rationale:** Users with acute emergency symptoms must receive immediate guidance without waiting for multi-agent synthesis.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-012: Transparent Source Provenance (No Invented Sources)
**Date:** 2026-10-12  
**Decision:** Agents must never invent fake author names or nonexistent journal titles. When primary indexed sources are unavailable, claims must be marked with `is_ai_generated: true` and labeled "AI Educational Synthesis".  
**Rationale:** Scientific and clinical integrity prevents users from trusting fabricated citations.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-013: 7-Agent Specialization & Allocation
**Date:** 2026-10-12  
**Decision:** Define 7 distinct healthcare agents with single-responsibility design:
1. `intake_agent`: Domain classification & entity extraction
2. `literature_agent`: Literature search & clinical guideline grounding
3. `clinical_agent`: Symptom constellations & pathophysiology
4. `medication_agent`: Pharmacodynamics & drug interactions
5. `evidence_agent`: Peer-review validation & contradiction detection
6. `synthesis_agent`: Structured clinical report compilation
7. `safety_guard_agent`: Clinical safety gatekeeper & disclaimers
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-014: VerbatimModuleSyntax & Strict TypeScript Compliance
**Date:** 2026-10-12  
**Decision:** Adhere strictly to TypeScript `verbatimModuleSyntax` using `import type` and eliminate all unused variables across all frontend pages and components.  
**Rationale:** Guarantees clean, zero-warning production builds in Vite.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-015: Ingesting Authoritative Clinical Corpus
**Date:** 2026-10-12  
**Decision:** Ingest ADA Diabetes, AHA/ACC Hypertension, GINA Asthma, and WHO Essential Medicines guidelines into `data/documents/` and delete obsolete geopolitical dossiers.  
**Rationale:** Ensures local RAG and retrieval tools index authentic clinical source material.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-016: Dual-Mode Gemini Model Routing
**Date:** 2026-10-12  
**Decision:** Route Intake, Literature, Clinical, Medication, and Safety agents to `gemini-1.5-flash` for high throughput (~1-3s), while routing Evidence Validation and Report Synthesis to `gemini-1.5-pro` for deep reasoning.  
**Rationale:** Optimizes response latency while maintaining deep reasoning where it matters most.  
**Status:** IMPLEMENTED & VERIFIED

---

## DEC-017: Backward-Compatible API Aliases
**Date:** 2026-10-12  
**Decision:** Maintain dual endpoint decorators on FastAPI routes: both `/api/medical/query` and `/api/query`, `/api/knowledge/graph` and `/api/graph/subgraph`.  
**Rationale:** Guarantees zero regression for any existing legacy scripts or test harnesses.  
**Status:** IMPLEMENTED & VERIFIED
