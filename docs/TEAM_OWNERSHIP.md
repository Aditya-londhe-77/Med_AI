# AEGIS — Team Ownership Map

> **Created:** 2026-06-26
> **Source:** AEGIS Team Roles & Responsibilities Agreement + Architecture Review
> **Rule:** No ownership overlaps. Every component has exactly one primary owner.

---

## Shlok Noval — Lead AI Architect & Intelligence Systems Engineer

### Primary Ownership: Intelligence Core

| Component | Directory | Description |
|-----------|-----------|-------------|
| **LangGraph Orchestrator** | `backend/app/orchestrator/` | State graph design, agent dispatch, conditional routing, state management |
| **Recon Agent** | `backend/app/agents/recon.py` | OSINT gathering, DuckDuckGo search, SEC Edgar, prompt engineering |
| **Financial Agent** | `backend/app/agents/financial.py` | Market analysis, yfinance integration, financial RAG prompts |
| **Geopolitical Agent** | `backend/app/agents/geopolitical.py` | Policy analysis, GDELT/RSS, geopolitical RAG prompts |
| **Synthesis Agent** | `backend/app/agents/synthesis.py` | Final briefing compilation, narrative structuring |
| **Devil's Advocate Agent** | `backend/app/agents/devil_advocate.py` | Adversarial review, challenge generation, re-run logic |
| **Base Agent** | `backend/app/agents/base.py` | Abstract base class, shared agent interface |
| **ChromaDB / Vector RAG** | `backend/app/retrieval/` | Embeddings (Vertex AI), chunking, vector store, similarity search |
| **Neo4j / GraphRAG** | `backend/app/graph_rag/` | Neo4j client, entity extraction, Cypher queries, graph schema |
| **Confidence Engine** | `backend/app/confidence/` | Scoring formulas, per-claim tracking, global metrics |
| **Source Trust / Validation** | `backend/app/validation/` | Trust scoring, source tiers, credibility framework |
| **Document Ingestion** | `backend/app/retrieval/ingestion.py` | PDF/text processing, corpus loading, embedding pipeline |
| **AI Architecture Docs** | `docs/` (AI sections) | Agent design docs, RAG/GraphRAG documentation |

### Deliverable Directories
```
backend/app/agents/
backend/app/orchestrator/
backend/app/retrieval/
backend/app/graph_rag/
backend/app/confidence/
backend/app/validation/
```

### Review/Viva Ownership
- Multi-Agent Systems architecture and design rationale
- LangGraph orchestration and state management
- RAG and GraphRAG implementation details
- Neo4j schema design and Cypher queries
- Confidence Engine formulas and scoring logic
- Adversarial validation (Devil's Advocate) workflow
- Source credibility framework
- Vertex AI / Gemini integration

---

## Aditya — Lead Platform Engineer & Full-Stack Systems Developer

### Primary Ownership: Product, Platform, and Infrastructure

| Component | Directory | Description |
|-----------|-----------|-------------|
| **React Frontend** | `frontend/` | Vite setup, component architecture, state management, routing |
| **Query UI** | `frontend/src/pages/` | Query input, submission, loading states |
| **Agent Activity Stream** | `frontend/src/components/` | Real-time agent status display |
| **Strategic Briefing UI** | `frontend/src/components/` | Briefing rendering, claim display, confidence badges |
| **Knowledge Graph Viewer** | `frontend/src/components/` | Graph visualization (future P2) |
| **Risk Dashboard** | `frontend/src/components/` | Confidence metrics display |
| **FastAPI Routes** | `backend/app/api/` | All REST endpoints, request validation, response formatting |
| **WebSocket Handler** | `backend/app/api/websocket.py` | WebSocket connection, event broadcasting, reconnection |
| **Supabase Integration** | `backend/app/database/` | Supabase client, database models, migrations |
| **Authentication** | `backend/app/api/routes/auth.py` | Supabase Auth integration, JWT validation, middleware |
| **Authorization** | `backend/app/api/` | RLS policies, permission checks |
| **Docker / Deployment** | `docker-compose.yml`, `Dockerfile`s | Container configuration, service orchestration |
| **GitHub Workflows** | `.github/workflows/` | CI/CD pipeline configuration |
| **Hosting / Infrastructure** | Deployment configs | Environment setup, DNS, cloud config (if applicable) |

### Deliverable Directories
```
frontend/
backend/app/api/
backend/app/database/
docker-compose.yml
.github/workflows/
```

### Review/Viva Ownership
- Frontend architecture (React + Vite)
- API design and REST endpoint architecture
- Supabase PostgreSQL schema design
- WebSocket real-time streaming implementation
- Supabase Auth (JWT, RLS)
- Docker deployment and containerization
- CI/CD pipeline (GitHub Actions)
- Infrastructure and hosting decisions

---

## Shared Ownership — Both Team Members

### Jointly Responsible For

| Responsibility | Cadence | Notes |
|---------------|---------|-------|
| **Shared Schemas** (`backend/app/shared/`) | As needed | Both must approve changes to Pydantic models |
| **Integration Testing** | Weekly | Verify agent ↔ API ↔ frontend pipeline |
| **GitHub Repository** | Continuous | Branch management, PR reviews |
| **Documentation Updates** | Weekly | Keep docs in sync with implementation |
| **Bug Fixing** | As needed | Cross-boundary bugs resolved together |
| **Demo Preparation** | Pre-submission | Joint demo script, rehearsal |
| **PPT Preparation** | Pre-submission | Shared slides, each presents own section |
| **Final Report** | Pre-submission | Each writes own section, cross-review |
| **System Validation** | Pre-submission | End-to-end testing of complete pipeline |

### Shared Directory
```
backend/app/shared/        # Pydantic schemas, constants, shared utilities
docs/                      # All documentation (each owns their sections)
data/                      # Demo corpus and seed data
```

---

## Ownership Boundary Rules

### Rule 1: Single Owner Per File
Every source file has exactly **one** primary owner. If a file needs changes from the non-owner, it goes through a PR.

### Rule 2: Schema Changes Require Both
Changes to `backend/app/shared/schemas.py` (the agent I/O contract) **must be approved by both** Shlok and Aditya since both depend on it.

### Rule 3: Integration Points
These are the interfaces between Shlok's and Aditya's code:

```
Shlok's Code                    Interface                    Aditya's Code
─────────────                   ─────────                    ────────────
Orchestrator.run()    ──►  shared/schemas.py  ◄──    api/routes/query.py
  (returns AgentResponse)   (Pydantic models)       (calls orchestrator)
  
Agents emit events    ──►  WSMessage schema   ◄──    api/websocket.py
  (via callback)            (typed events)          (broadcasts to client)
  
Confidence Engine     ──►  confidence metrics  ◄──   frontend/components/
  (returns scores)          (JSON structure)         (displays scores)
```

### Rule 4: Technical Authority
- **Shlok** has final authority on AI architecture decisions (agent design, RAG strategy, LLM choice, orchestration logic)
- **Aditya** has final authority on platform decisions (API design, auth scheme, deployment, frontend architecture)
- **Major architecture changes** (affecting both sides) require **mutual approval**

### Rule 5: Communication Protocol
1. If you need to change code you don't own → create a PR and tag the owner
2. If a schema change is needed → discuss before implementing
3. If a blocking dependency exists → communicate immediately, don't wait for weekly sync
4. Weekly progress review → status update on completed work, blockers, next steps

---

## Ownership Visual Map

```
┌─────────────────────────────────────────────────────────────────┐
│                           AEGIS                                  │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│  │     SHLOK's Domain       │  │       ADITYA's Domain         │ │
│  │                          │  │                                │ │
│  │  ┌──────────────────┐   │  │  ┌────────────────────────┐   │ │
│  │  │  Orchestrator     │   │  │  │  FastAPI Routes         │   │ │
│  │  │  (LangGraph)      │   │  │  │  (REST + WebSocket)    │   │ │
│  │  └──────────────────┘   │  │  └────────────────────────┘   │ │
│  │  ┌──────────────────┐   │  │  ┌────────────────────────┐   │ │
│  │  │  Agents           │   │  │  │  React Frontend         │   │ │
│  │  │  (5 agents)       │   │  │  │  (Vite + components)   │   │ │
│  │  └──────────────────┘   │  │  └────────────────────────┘   │ │
│  │  ┌──────────────────┐   │  │  ┌────────────────────────┐   │ │
│  │  │  RAG / ChromaDB   │   │  │  │  Supabase (DB + Auth)  │   │ │
│  │  └──────────────────┘   │  │  └────────────────────────┘   │ │
│  │  ┌──────────────────┐   │  │  ┌────────────────────────┐   │ │
│  │  │  GraphRAG / Neo4j │   │  │  │  Docker / Deployment   │   │ │
│  │  └──────────────────┘   │  │  └────────────────────────┘   │ │
│  │  ┌──────────────────┐   │  │  ┌────────────────────────┐   │ │
│  │  │  Confidence Engine│   │  │  │  CI/CD (GitHub Actions) │   │ │
│  │  └──────────────────┘   │  │  └────────────────────────┘   │ │
│  │  ┌──────────────────┐   │  │                                │ │
│  │  │  Source Validation│   │  │                                │ │
│  │  └──────────────────┘   │  │                                │ │
│  └──────────────────────────┘  └──────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                    SHARED (Both)                              ││
│  │  schemas.py │ constants.py │ docs/ │ data/ │ integration     ││
│  └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```
