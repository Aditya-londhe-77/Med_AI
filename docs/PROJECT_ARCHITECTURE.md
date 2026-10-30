# AI_Based_Strategic_Intelligence_Assistant — Project Architecture

## Overview
AISIA is a medical AI orchestration platform that uses a multi-agent LangGraph architecture to provide evidence-grounded medical information. It accepts medical queries from healthcare professionals and students, routes them through specialized AI agents, validates evidence, and returns structured medical reports with citations.

**Stack:** FastAPI · LangGraph · Google Gemini · ChromaDB · Neo4j · Supabase · React 19 · TypeScript · Vite · Tailwind CSS

---

## Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER'S BROWSER                              │
│   React 19 + TypeScript + Vite + Tailwind CSS (Pink/Purple)     │
│   ┌──────────────┐ ┌────────────────────┐ ┌─────────────────┐  │
│   │ Medical      │ │ Live Agent         │ │ Medical Report  │  │
│   │ Dashboard    │ │ Orchestration      │ │ Viewer          │  │
│   └──────┬───────┘ └────────▲───────────┘ └────────▲────────┘  │
│          │ REST              │ WebSocket             │ REST      │
└──────────┼───────────────────┼───────────────────────┼──────────┘
           │                   │                       │
┌──────────▼───────────────────┼───────────────────────┼──────────┐
│              FASTAPI BACKEND (Python 3.10+)                     │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Medical Domain Guard (pre-validation)                    │  │
│  │  ┌────────────────────────────────────────────────────┐   │  │
│  │  │ LangGraph Medical Multi-Agent Orchestrator         │   │  │
│  │  │  ┌──────────┐  ┌────────────┐  ┌───────────────┐  │   │  │
│  │  │  │ Intake & │  │ Literature │  │  Clinical     │  │   │  │
│  │  │  │ Classify │  │ Research   │  │  Analysis     │  │   │  │
│  │  │  └──────────┘  └────────────┘  └───────────────┘  │   │  │
│  │  │  ┌──────────┐  ┌────────────┐                      │   │  │
│  │  │  │Medication│  │ Evidence   │    ← Parallel        │   │  │
│  │  │  │Reference │  │ Validation │      Dispatch        │   │  │
│  │  │  └──────────┘  └────────────┘                      │   │  │
│  │  │       └──────────────┬──────────────────────────┘  │   │  │
│  │  │          ┌───────────▼──────────┐                   │   │  │
│  │  │          │ Medical Report       │                   │   │  │
│  │  │          │ Synthesis Agent      │                   │   │  │
│  │  │          └───────────┬──────────┘                   │   │  │
│  │  │          ┌───────────▼──────────┐                   │   │  │
│  │  │          │ Safety & Disclaimer  │                   │   │  │
│  │  │          │ Guard Agent          │                   │   │  │
│  │  │          └──────────────────────┘                   │   │  │
│  │  └────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ ChromaDB │  │  Neo4j   │  │ Supabase  │  │ DuckDuckGo   │  │
│  │(Medical  │  │(Medical  │  │(Medical   │  │ Medical News │  │
│  │ Corpus)  │  │ KG)      │  │ Queries)  │  │ Search       │  │
│  └──────────┘  └──────────┘  └───────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Responsibilities

### 1. Medical Intake and Domain Classification Agent
- **ID:** `intake_agent`
- **Model:** gemini-1.5-flash
- **Role:** Classifies the medical query into a domain (e.g., cardiology, pharmacology, anatomy) and validates it is medical in nature.
- **Inputs:** Raw user query
- **Outputs:** Domain classification, query intent, reformulated medical question

### 2. Medical Literature Research Agent
- **ID:** `literature_agent`
- **Model:** gemini-1.5-flash
- **Role:** Searches for relevant medical literature, PubMed-style abstracts, clinical guidelines, and regulatory documents using DuckDuckGo + ChromaDB.
- **Tools:** DuckDuckGo (medical search), ChromaDB vector store, GraphRAG
- **Outputs:** Evidence claims with citations

### 3. Clinical Information Analysis Agent
- **ID:** `clinical_agent`
- **Model:** gemini-1.5-flash
- **Role:** Analyzes clinical data patterns, interprets symptoms, and organizes information about conditions.
- **Outputs:** Clinical claims with analysis notes

### 4. Medication Reference Agent
- **ID:** `medication_agent`
- **Model:** gemini-1.5-flash
- **Role:** Looks up drug information, interactions, dosage guidelines (educational), and contraindications.
- **Outputs:** Medication reference claims with source citations

### 5. Medical Evidence Validation Agent
- **ID:** `evidence_agent`
- **Model:** gemini-1.5-pro
- **Role:** Reviews and validates claims from other agents, identifies contradictions, gaps in evidence, and inconsistencies.
- **Outputs:** Validated/challenged claims, contradiction list

### 6. Medical Report Synthesis Agent
- **ID:** `synthesis_agent`
- **Model:** gemini-1.5-pro
- **Role:** Synthesizes validated claims into a structured medical report with sections, citations, and caveats.
- **Outputs:** Final medical report JSON

### 7. Medical Safety and Domain Guard Agent
- **ID:** `safety_guard_agent`
- **Model:** gemini-1.5-flash
- **Role:** Final safety pass — adds disclaimers, detects any missed non-medical content, ensures emergency warnings are present if needed.
- **Outputs:** Safety-wrapped final response

---

## LangGraph Execution Flow

```
User Query
    │
    ▼
[Medical Domain Guard] ← Hard reject if not medical
    │
    ▼
[Emergency Safety Screening] ← If life-threatening: immediate warning + continue
    │
    ▼
[intake_agent] ← Classify and route
    │
    ▼
[Parallel Dispatch] ──────────────────────────────┐
    │                                             │
    ▼                                             ▼
[literature_agent]                    [clinical_agent / medication_agent]
    │                                             │
    └──────────────────┬──────────────────────────┘
                       ▼
             [evidence_agent] ← Validate + flag contradictions
                       │
                       ▼ (conditional: if contradictions → targeted re-run)
             [synthesis_agent] ← Compile medical report
                       │
                       ▼
             [safety_guard_agent] ← Add disclaimers, final check
                       │
                       ▼
             Structured Medical Response
```

---

## API Routes and Schemas

### REST Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check — returns AISIA version and service status |
| GET | /api/config | System config — models, parameters, integration status |
| POST | /api/medical/query | Submit a medical query → returns query_id |
| GET | /api/medical/query/{query_id} | Get query result (polling) |
| GET | /api/history | Paginated medical query history |
| GET | /api/knowledge/graph | Medical knowledge graph nodes + relationships |
| GET | /api/agents | List registered medical agents and their status |

### WebSocket
| Path | Description |
|------|-------------|
| /ws/{query_id} | Real-time agent progress events |

### WebSocket Event Types
- `system` — System messages (initialization, completion)
- `agent_started` — Agent begins processing
- `agent_finding` — Agent produces a medical finding
- `evidence_validated` — Evidence passed validation
- `evidence_challenged` — Contradiction found
- `synthesis_complete` — Report ready
- `safety_check` — Safety guard completed
- `error` — Processing error

---

## Database Structure

### ChromaDB Collections
| Collection | Contents |
|------------|----------|
| `medical_literature` | PubMed abstracts, clinical guidelines (ingested) |
| `drug_reference` | Medication information from open drug databases |
| `anatomy_physiology` | Anatomy and physiology reference texts |
| `icd_conditions` | ICD-10 condition descriptions |

### Neo4j Medical Knowledge Graph
| Node Types | Description |
|------------|-------------|
| `Condition` | Medical conditions (e.g., Type 2 Diabetes) |
| `Drug` | Medications and drugs |
| `Symptom` | Clinical symptoms |
| `Anatomy` | Body structures |
| `Guideline` | Clinical guidelines |
| `Organization` | WHO, NIH, FDA, CDC |

| Relationship Types | Description |
|-------------------|-------------|
| `TREATS` | Drug treats Condition |
| `CAUSES` | Condition causes Symptom |
| `CONTRAINDICATES` | Drug contraindicated with Condition/Drug |
| `ASSOCIATED_WITH` | Symptom associated with Condition |
| `PUBLISHED_BY` | Guideline published by Organization |

### Supabase (PostgreSQL)
| Table | Contents |
|-------|----------|
| `medical_queries` | Query text, session_id, user_id, status, created_at |
| `medical_reports` | Query_id, report JSON, confidence_score |
| `users` | Auth managed by Supabase Auth |

---

## RAG Pipeline

1. **User query** → embed using Gemini embedding model
2. **ChromaDB semantic search** → top-k medical document chunks
3. **Neo4j graph traversal** → 2-hop related medical entities
4. **Hybrid fusion** → merge vector + graph results, de-duplicate
5. **Context injection** → pass to agent LLM prompt

---

## WebSocket Events

Events are JSON objects with these fields:
```json
{
  "type": "agent_finding",
  "event": "agent_finding",
  "message": "Literature Agent: Found clinical guideline on hypertension management",
  "progress": 45,
  "agent_id": "literature_agent",
  "agent_name": "Medical Literature Research Agent",
  "model": "gemini-1.5-flash",
  "claim_id": "clm_lit_001",
  "statement": "...",
  "confidence": 87,
  "sources": ["WHO Guideline 2023", "AHA Position Statement"]
}
```

---

## Frontend Structure

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── MedicalAppShell.tsx     ← Main layout wrapper
│   │   ├── MedicalSidebar.tsx      ← Navigation sidebar
│   │   └── MedicalTopbar.tsx       ← Top header bar
│   ├── medical/
│   │   ├── MedicalQueryComposer.tsx
│   │   ├── MedicalAgentCard.tsx
│   │   ├── AgentWorkflowTimeline.tsx
│   │   ├── EvidenceCitationCard.tsx
│   │   ├── MedicalReportSection.tsx
│   │   ├── MedicalSafetyAlert.tsx
│   │   ├── MedicalKnowledgeSourceCard.tsx
│   │   └── ResearchHistoryTable.tsx
│   └── ui/
│       ├── LoadingState.tsx
│       ├── EmptyState.tsx
│       └── ErrorState.tsx
├── pages/
│   ├── MedicalDashboard.tsx        ← Home page
│   ├── MedicalWorkspace.tsx        ← Query + agent selection
│   ├── AgentOrchestration.tsx      ← Live agent execution
│   ├── MedicalReportViewer.tsx     ← Structured report view
│   ├── AgentCenter.tsx             ← Agent status + config
│   ├── KnowledgeExplorer.tsx       ← Medical knowledge graph
│   ├── ResearchHistory.tsx         ← Past queries
│   ├── SystemSettings.tsx          ← Config
│   ├── Login.tsx                   ← Auth
│   └── Signup.tsx                  ← Auth
├── hooks/
│   └── useMedicalStream.ts         ← WebSocket + polling hook
├── services/
│   ├── api.ts                      ← Typed API client
│   └── supabase.ts                 ← Supabase client
└── App.tsx                         ← Routes
```

---

## Design System — Pink & Purple Medical Theme

```css
--primary: 270 70% 58%       /* #7652D6 — Primary Purple */
--deep-purple: 261 52% 36%   /* #4B2B91 — Deep Purple */
--pink-accent: 319 74% 69%   /* #E879B9 — Pink Accent */
--pale-pink: 330 100% 97%    /* #FFF1F7 — Pale Pink Background */
--lavender: 270 100% 96%     /* #F3EEFF — Lavender Background */
--main-text: 267 24% 19%     /* #29243A — Main Text */
--secondary-text: 264 13% 51% /* #777187 — Secondary Text */
--border: 270 35% 92%        /* #E9E2F2 — Borders */
```

---

## Authentication and Authorization
- **Method:** Supabase Auth (email + password) + local session fallback for offline demo
- **Session key:** `aisia_session` (localStorage)
- **Protected routes:** All routes except /login and /signup
- **Row-Level Security:** Supabase RLS on medical_queries table (users see only their own queries)

---

## Medical Domain Validation

The `MedicalDomainGuard` class in `backend/app/medical/domain_guard.py`:
1. Checks query against a curated list of MEDICAL_KEYWORDS
2. Checks query against a list of REJECTED_DOMAINS (finance, military, geopolitics, etc.)
3. Returns a `DomainValidationResult` with `is_medical`, `confidence`, and `rejection_reason`
4. If `is_medical = False` → HTTP 422 with medical-only restriction message

---

## Safety and Evidence Validation

1. **Emergency screening:** Query checked for life-threatening symptoms before agent dispatch
2. **Disclaimer injection:** All responses include "This is for educational purposes only — not medical advice"
3. **Contradiction reporting:** Evidence agent flags conflicting information
4. **Missing evidence disclosure:** If evidence is insufficient, report states so explicitly
5. **Prompt injection protection:** Retrieved RAG context is sanitized before injection

---

## Environment Variables and Service Dependencies

| Variable | Required | Description |
|----------|----------|-------------|
| GEMINI_API_KEY | Recommended | Google Gemini API key |
| NEO4J_URI | Optional | Neo4j connection URI |
| NEO4J_USER | Optional | Neo4j username |
| NEO4J_PASSWORD | Optional | Neo4j password |
| SUPABASE_URL | Optional | Supabase project URL |
| SUPABASE_SERVICE_KEY | Optional | Supabase service key |
| SUPABASE_ANON_KEY | Optional | Supabase anonymous key |

All integrations fail gracefully. The system operates in heuristic fallback mode without API keys.
