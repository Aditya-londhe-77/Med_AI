# AEGIS — Phase 0: Architecture Review

> **Review Date:** 2026-06-26
> **Reviewer Role:** Senior Software Architect · Lead AI Engineer · Engineering Manager · Technical Reviewer
> **Source Documents:** AEGIS Technical Architecture Document (v.Updated), AEGIS Team Roles & Responsibilities Agreement
> **Status:** ✅ RESOLVED — All questions answered. Proceeding to Phase 1–5.

---

## 1. Executive Summary

### What AEGIS Is
AEGIS (**A**I-driven **E**arly Warning **I**ntelligence **S**ystem) is a multi-agent AI platform that transforms strategic intelligence analysis from a single-LLM pipeline into a coordinated team of specialized AI agents. It is designed as a B.Tech final-year project by a two-person team (Shlok Noval and Aditya).

### Core Mission
To produce **transparent, evidence-grounded strategic intelligence briefs** by orchestrating specialized AI agents that:
1. Independently gather domain-specific intelligence (reconnaissance, financial, geopolitical)
2. Retrieve and reason over heterogeneous sources using both vector-based RAG and graph-based RAG (GraphRAG)
3. Self-challenge conclusions through an adversarial "Devil's Advocate" loop
4. Quantify confidence with a multi-dimensional scoring engine
5. Present results with full source traceability and explainability

### End-to-End Workflow
```
User Query
  → LangGraph Orchestrator (decomposes query into subtasks)
    → Parallel Agent Dispatch:
       ├── Recon Agent (OSINT: web search, SEC filings, RAG/GraphRAG)
       ├── Financial Agent (market data, financial RAG/GraphRAG)
       └── Geopolitical Agent (policy docs, news, geopolitical GraphRAG)
    → Agent outputs collected
    → Devil's Advocate Agent (adversarial review, contradiction detection)
       ├── If challenge valid → targeted re-run of specific agent (max 2 rounds)
       └── Converges when no valid challenges remain OR max rounds hit
    → Synthesis Agent (compiles vetted evidence into strategic brief)
    → Confidence Engine (scores: confidence_before/after, trust, consensus)
  → WebSocket Streaming → React Dashboard (real-time display)
```

---

## 2. Architecture Understanding

### 2.1 LangGraph Orchestrator
- **Role:** Central controller that decomposes user queries into subtasks and dispatches them to specialized agents in parallel
- **Framework:** LangGraph (LangChain's state-machine-based orchestrator)
- **Key Behaviors:** Parallel agent dispatch, conditional re-routing for Devil's Advocate challenges, state management across multi-round debate
- **Understanding Confidence:** ✅ HIGH

### 2.2 Recon Agent
- **Role:** Open-source intelligence (OSINT) gathering
- **Data Sources:** Web search (DuckDuckGo — free), SEC Edgar (free)
- **RAG Flow:** Chunks text → embeds with Vertex AI text-embedding-005 → stores in ChromaDB → cosine similarity search → top-k retrieval
- **GraphRAG Flow:** Extracts entities/relations via Gemini or spaCy NER → indexes into Neo4j → Cypher traversal queries
- **Understanding Confidence:** ✅ HIGH

### 2.3 Financial Agent
- **Role:** Market data analysis and financial intelligence
- **Data Sources:** Yahoo Finance (yfinance — free), archived news via vector DB
- **GraphRAG:** Knowledge graph of companies/sectors/events
- **Understanding Confidence:** ✅ HIGH (resolved with free APIs)

### 2.4 Geopolitical Agent
- **Role:** Policy and geopolitical context analysis
- **Data Sources:** Free news RSS feeds, GDELT (free geopolitical events DB), policy document corpora
- **GraphRAG:** Neo4j graph of geopolitical actors, events, sanctions, alliances
- **Understanding Confidence:** ✅ HIGH (resolved with free sources)

### 2.5 Synthesis Agent
- **Role:** Final narrative compilation from all validated agent outputs
- **LLM:** Gemini 1.5 Pro (via Vertex AI — higher reasoning quality)
- **Approach:** Chain-of-Thought prompting, structured JSON inputs from other agents, formal analyst-tone briefing
- **Understanding Confidence:** ✅ HIGH

### 2.6 Devil's Advocate Agent
- **Role:** Adversarial self-validation through structured critique
- **Termination:** Max 2 re-run rounds + 60s timeout per round
- **Process:**
  1. Decompose claims into explicit/implicit assumptions
  2. Search vector DB + graph for counter-evidence
  3. Generate counterarguments with citations
  4. If valid refutation found → trigger targeted re-run of specific agent
  5. Converges when no valid challenges remain OR max rounds hit
- **Understanding Confidence:** ✅ HIGH

### 2.7 Confidence Engine
- **Metrics:** `confidence_before`, `confidence_after`, supporting/contradicting source counts, trust score, consensus score
- **Formula:** `confidence_after = min(1, confidence_before + α × (support_count - contradict_count))`
- **Global:** `global_confidence = avg(claim_confidences) × global_trust_score`
- **Storage:** Supabase PostgreSQL (per-claim tracking)
- **Understanding Confidence:** ✅ HIGH (resolved with Supabase storage)

### 2.8 ChromaDB (Vector Database)
- **Role:** Stores embedded document chunks for similarity-based retrieval
- **Mode:** Embedded (in-process, no separate server)
- **Embedding Model:** Vertex AI text-embedding-005
- **Chunking:** ~500 tokens with overlap
- **Similarity:** Cosine distance
- **Understanding Confidence:** ✅ HIGH

### 2.9 Neo4j GraphRAG
- **Role:** Structured knowledge graph for entity-relationship queries
- **Edition:** Community Edition (free, Docker)
- **Schema:** Nodes (organizations, products, people, countries, documents), edges (HAS_INVESTOR, HAS_COMPETITOR, HAS_CHUNK, etc.)
- **Query Language:** Cypher
- **Entity Extraction:** Gemini (via Vertex AI) or spaCy NER
- **Understanding Confidence:** ✅ HIGH

### 2.10 FastAPI Backend
- **Role:** Monolithic backend — all agents, orchestrator, and APIs in one process
- **Architecture:** Modular monolith with clear package boundaries
- **Understanding Confidence:** ✅ HIGH

### 2.11 React Frontend
- **Framework:** React + Vite (no Next.js — simpler for dashboard)
- **Components:** Query input, agent activity stream, basic confidence display, strategic briefing view
- **Understanding Confidence:** ✅ HIGH

### 2.12 WebSocket Streaming
- **Implementation:** FastAPI native WebSockets (built-in, no Socket.IO dependency)
- **Message Level:** Agent-level status updates (started, completed, challenged) + final briefing
- **Understanding Confidence:** ✅ HIGH

### 2.13 Supabase (NEW — User Requested)
- **Role:** Application database + authentication + realtime
- **Services Used:** PostgreSQL (free: 500MB), Auth (built-in), Realtime subscriptions
- **Replaces:** Separate PostgreSQL + custom auth
- **Understanding Confidence:** ✅ HIGH

---

## 3. Resolved Technology Stack (Zero-Budget)

| Component | Technology | Cost | Rationale |
|-----------|-----------|------|-----------|
| **LLM (Speed)** | Gemini 1.5 Flash via Vertex AI | GCP credits ($1,000) | Fastest Gemini model — optimized for low latency |
| **LLM (Quality)** | Gemini 1.5 Pro via Vertex AI | GCP credits | Better reasoning for Synthesis + Devil's Advocate |
| **Embeddings** | Vertex AI text-embedding-005 | GCP credits | Native GCP integration, high quality |
| **Vector DB** | ChromaDB (embedded) | Free | No server needed, simplest setup |
| **Graph DB** | Neo4j Community (Docker) | Free | Full Cypher support, Docker deployment |
| **App DB** | Supabase PostgreSQL | Free tier (500MB) | User/session/log storage, built-in auth |
| **Auth** | Supabase Auth | Free tier | Email/password + OAuth out of the box |
| **Backend** | FastAPI (Python) | Free | Monolithic, high performance, WebSocket built-in |
| **Frontend** | React + Vite | Free | Fast dev, no SSR overhead |
| **WebSocket** | FastAPI native | Free | No additional dependency |
| **Web Search** | DuckDuckGo (duckduckgo-search) | Free | No API key needed |
| **Financial Data** | yfinance | Free | Yahoo Finance wrapper, no key needed |
| **News** | GDELT + RSS feeds | Free | Geopolitical events + news aggregation |
| **SEC Filings** | SEC Edgar API | Free | No key needed for EDGAR |
| **NER** | spaCy (en_core_web_sm) | Free | Offline entity extraction |
| **Orchestration** | LangGraph | Free | State-machine agent orchestration |
| **Deployment** | Docker Compose | Free | Local development and demo |
| **CI/CD** | GitHub Actions | Free (public repo) | Automated lint/test/build |
| **Monitoring** | Python logging + Supabase logs | Free | Structured logging to Supabase tables |

### Vertex AI Credit Budget Estimate

| Model | Use Case | Est. Cost/Query | Queries/Day | Monthly Est. |
|-------|----------|-----------------|-------------|-------------|
| Gemini 1.5 Flash | Recon, Financial, Geopolitical agents | ~$0.002 | 20 | ~$1.20 |
| Gemini 1.5 Pro | Synthesis, Devil's Advocate | ~$0.01 | 20 | ~$6.00 |
| text-embedding-005 | Document embedding + queries | ~$0.0001 | 100 | ~$0.30 |
| **Total** | | | | **~$7.50/month** |

> With $1,000 in credits expiring April 2027, you have roughly **133 months** of runway at this rate — far more than enough.

---

## 4. Risk Assessment

### 4.1 Scalability Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Vertex AI rate limits | 🟡 MEDIUM | Use Flash for most agents; queue requests; implement retry with backoff |
| Neo4j Community limits | 🟡 MEDIUM | Community Edition lacks clustering but is fine for demo-scale data |
| ChromaDB scale | 🟢 LOW | Embedded mode handles up to ~1M vectors; more than enough for MVP |
| Devil's Advocate loops | ✅ RESOLVED | Max 2 rounds + 60s timeout per round |

### 4.2 Security Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| API Key Exposure | ✅ RESOLVED | Only GCP service account key; stored in env vars / .env file |
| Prompt Injection | 🟡 MEDIUM | Sanitize all external content before LLM input; use structured output parsing |
| Authentication | ✅ RESOLVED | Supabase Auth (built-in JWT, row-level security) |
| Data Privacy | 🟢 LOW | Academic project; no real sensitive data |

### 4.3 Latency Optimization (User Priority: "Very Less Waiting Time")

| Technique | Impact | Details |
|-----------|--------|---------|
| **Gemini Flash** for speed-critical agents | 🟢 HIGH | ~2-5s per agent call vs ~10-15s for Pro |
| **Parallel agent execution** | 🟢 HIGH | All 3 agents run simultaneously via asyncio |
| **Streaming responses** | 🟢 HIGH | WebSocket pushes results as they arrive |
| **ChromaDB embedded** | 🟢 HIGH | In-process = zero network latency for retrieval |
| **Max 2 DA rounds** | 🟢 HIGH | Caps worst-case latency |
| **Pre-computed embeddings** | 🟡 MEDIUM | Corpus embedded at ingestion, not query time |
| **Estimated total latency** | | **15-45 seconds** per query (down from >2 min) |

### 4.4 Cost Risks — ✅ ELIMINATED
All components are free-tier or covered by GCP credits. Zero external spend required.

---

## 5. Resolved Document Inconsistencies

| # | Issue | Resolution |
|---|-------|-----------|
| 1 | Project subtitle conflict | **"AI-driven Early Warning Intelligence System"** — from the technical architecture doc (more descriptive) |
| 2 | React vs React/Next.js | **React + Vite** — no SSR needed for a dashboard app |
| 3 | Optional agents | **Deferred** — Source Credibility logic folded into Devil's Advocate; Evidence Verification folded into Recon |
| 4 | Phase ordering conflict | **New integrated order** created (see ROADMAP.md) — combines best of both documents |
| 5 | PostgreSQL optional vs core | **Supabase** replaces standalone PostgreSQL — provides DB + Auth + Realtime in one free service |

---

## 6. Clarification Questions — All Resolved

| Q# | Question | Resolution |
|----|----------|-----------|
| Q1 | Monolithic vs Microservices | **Monolithic** (user confirmed) |
| Q2 | DA max rounds | **2 rounds max** (recommendation accepted) |
| Q3 | Optional agents in scope | **Deferred** (recommendation accepted) |
| Q4 | Primary LLM | **Gemini 1.5 Flash + Pro** via Vertex AI ($1,000 GCP credits) |
| Q5 | Target latency | **"Very less waiting time"** → target 15-45s via Flash + parallel + streaming |
| Q6 | PostgreSQL role | **Supabase** (user suggestion) — app state, auth, logs |
| Q7 | Neo4j edition | **Community Edition** (Docker, free) |
| Q8 | ChromaDB mode | **Embedded** (in-process) |
| Q9 | Demo corpus | Small curated corpus (recommendation accepted) |
| Q10 | Frontend framework | **React + Vite** (recommendation accepted) |
| Q11 | MVP UI scope | **(b) Query input + agent activity stream** → path to (c) |
| Q12 | Design system | **Shadcn/ui + Tailwind** (free, modern, premium look) |
| Q13 | External APIs | Free only: DuckDuckGo, SEC Edgar, yfinance, GDELT, RSS feeds |
| Q14 | WebSocket granularity | **(b) Agent-level status updates** |
| Q15 | Phase ordering | **New integrated order** |
| Q16 | Official name | **"AI-driven Early Warning Intelligence System"** |
| Q17 | Hard deadlines | ⚠️ **UNKNOWN** — user to confirm |
| Q18 | Deployment environment | **Local (Docker Compose)** + optional GCP for demo |
| Q19 | Auth method | **Supabase Auth** (JWT, email/password + optional OAuth) |
| Q20 | Multi-user | **Single-user MVP** with multi-user capability via Supabase |
| Q21 | Cloud budget | **$0** except GCP credits ($1,000 Vertex AI) |
| Q22 | Machine specs | ⚠️ **UNKNOWN** — user to confirm (affects Neo4j performance) |
| Q23 | Ambitious features in scope | **Follow MVP scope** (recommendation accepted) |
| Q24 | Scenario Simulation Agent | **Cut from MVP** |
| Q25 | Fine-tuning | **No fine-tuning** — pre-trained models only |

> [!WARNING]
> **Q17 (deadlines) and Q22 (machine specs) remain unanswered.** These are non-blocking for documentation but should be answered before development begins.

---

## 7. Recommended Improvements — All Accepted

All recommendations from the original review have been accepted and are incorporated into the implementation plan. Key decisions:

1. ✅ Monolithic architecture with modular code boundaries
2. ✅ Max 2 rounds for Devil's Advocate + 60s timeout
3. ✅ ChromaDB embedded + Neo4j Community + Supabase
4. ✅ Pydantic models for all agent I/O contracts
5. ✅ FastAPI native WebSockets (no Socket.IO)
6. ✅ React + Vite (no Next.js)
7. ✅ Docker Compose only (no Kubernetes)
8. ✅ LangGraph only (no LlamaIndex duplication)
9. ✅ Gemini Flash for speed, Gemini Pro for quality
10. ✅ CI/CD from day 1 via GitHub Actions

---

## 8. Conclusion

All architectural decisions are now locked in. The technology stack is fully resolved with a **zero-cost** constraint (except GCP Vertex AI credits). The system is optimized for **low latency** using Gemini Flash, parallel execution, streaming, and embedded ChromaDB.

**Proceeding to Phase 1–5 documentation.**
