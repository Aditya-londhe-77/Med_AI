# AEGIS — Project Decisions Log

> **Created:** 2026-06-26
> **Status:** Living Document — Updated throughout development
> **Rule:** Every major decision is recorded here with full rationale.

---

## Decision Template

```
### DEC-XXX: [Decision Title]
- **Date:** YYYY-MM-DD
- **Decision:** What was decided
- **Reason:** Why this was chosen
- **Alternatives Considered:** What else was evaluated
- **Trade-offs:** What we gain and lose
- **Final Selection:** Confirmed choice
```

---

## Architecture Decisions

### DEC-001: Monolithic Backend Architecture
- **Date:** 2026-06-26
- **Decision:** All agents, orchestrator, and API routes run in a single FastAPI process
- **Reason:** A 2-person B.Tech team cannot maintain 5+ microservices. Operational overhead of service discovery, inter-service communication, distributed logging, and individual deployment pipelines would consume more time than actual feature development.
- **Alternatives Considered:**
  1. *Microservices (one container per agent)* — True A2A isolation, independent scaling. Rejected: operational complexity far exceeds team capacity.
  2. *Serverless functions (one Lambda per agent)* — Pay-per-use, auto-scaling. Rejected: cold start latency (10-30s) violates low-latency requirement; no GCP credits for Lambda.
- **Trade-offs:** We lose independent scaling and agent isolation, but gain simplicity, faster development, and easier debugging. The code is structured with modular packages so it can be split later if needed.
- **Final Selection:** ✅ Monolithic FastAPI with modular package boundaries

---

### DEC-002: Gemini 1.5 Flash + Pro via Vertex AI
- **Date:** 2026-06-26
- **Decision:** Use Gemini 1.5 Flash for speed-critical agents (Recon, Financial, Geopolitical) and Gemini 1.5 Pro for quality-critical agents (Synthesis, Devil's Advocate)
- **Reason:** User has $1,000 in GCP Vertex AI credits (expiring April 2027) and zero budget elsewhere. Gemini Flash offers ~2-5s inference (vs ~10-15s for Pro), critical for the "very less waiting time" requirement. Dual-model strategy optimizes cost vs quality.
- **Alternatives Considered:**
  1. *OpenAI GPT-4* — Excellent quality. Rejected: requires paid API key; no budget.
  2. *Claude (Anthropic)* — Good reasoning. Rejected: requires paid API key; no budget.
  3. *Local Llama 2/Mixtral* — Free, private. Rejected: requires significant GPU (user machine specs unknown); slower inference than cloud API.
  4. *Gemini Pro only* — Better quality everywhere. Rejected: 2-3× slower and more expensive than Flash for routine retrieval tasks.
  5. *Gemini Flash only* — Fastest and cheapest. Rejected: Flash's reasoning quality may be insufficient for Synthesis and Devil's Advocate.
- **Trade-offs:** Cloud dependency (requires internet), GCP vendor lock-in, credit budget consumed. But: fast responses, high quality, and $1,000 covers ~90,000 queries.
- **Final Selection:** ✅ Gemini 1.5 Flash (data agents) + Gemini 1.5 Pro (reasoning agents) via Vertex AI

---

### DEC-003: Supabase for Application Database + Auth
- **Date:** 2026-06-26
- **Decision:** Use Supabase (free tier) as the application database (PostgreSQL), authentication provider, and realtime engine
- **Reason:** Supabase provides PostgreSQL + Auth + Realtime subscriptions + Row-Level Security in one free service. This eliminates the need to build custom auth, manage a separate PostgreSQL instance, and implement session management.
- **Alternatives Considered:**
  1. *Self-hosted PostgreSQL (Docker)* — Full control, no limits. Rejected: requires building custom auth from scratch; more operational overhead.
  2. *Firebase* — Similar managed offering. Rejected: Firestore is NoSQL (poor fit for relational query/claim data); less PostgreSQL compatibility.
  3. *SQLite* — Simplest possible. Rejected: no auth, no realtime, single-user only, doesn't scale.
  4. *No database (in-memory only)* — Zero setup. Rejected: no query history, no persistence.
- **Trade-offs:** 500MB storage limit (free tier), external dependency, data lives on Supabase servers. But: built-in JWT auth, RLS, realtime subscriptions, and professional-grade infrastructure for free.
- **Final Selection:** ✅ Supabase (free tier)

---

### DEC-004: ChromaDB in Embedded Mode
- **Date:** 2026-06-26
- **Decision:** Use ChromaDB in embedded (in-process) mode, not client-server mode
- **Reason:** Embedded mode eliminates network latency between the backend and vector DB, which directly reduces query response time. For a monolithic architecture, there's no reason to run ChromaDB as a separate server.
- **Alternatives Considered:**
  1. *ChromaDB client-server* — Better for microservices. Rejected: unnecessary overhead in monolithic arch.
  2. *Pinecone* — Managed, scalable. Rejected: free tier has severe limits (100K vectors); requires API key.
  3. *Weaviate* — Feature-rich. Rejected: heavier Docker footprint; more complex setup for no clear benefit at demo scale.
  4. *FAISS* — Facebook's vector library. Rejected: no metadata filtering; lower-level API; no persistence built-in.
- **Trade-offs:** ChromaDB embedded is limited to single-process access (can't scale horizontally). But: zero latency, zero setup, sufficient for demo scale (~10K chunks).
- **Final Selection:** ✅ ChromaDB embedded mode

---

### DEC-005: Neo4j Community Edition (Docker)
- **Date:** 2026-06-26
- **Decision:** Use Neo4j Community Edition running in Docker
- **Reason:** Community Edition is free and provides full Cypher query support. Docker deployment integrates cleanly with the existing Docker Compose setup.
- **Alternatives Considered:**
  1. *Neo4j AuraDB* — Managed cloud, easier ops. Rejected: free tier is limited and may expire; cloud dependency.
  2. *Amazon Neptune* — Managed graph DB. Rejected: not free; AWS-specific.
  3. *NetworkX (Python)* — In-memory graph library. Rejected: no persistence; no Cypher; limited query capability.
  4. *No graph database* — RAG-only approach. Rejected: GraphRAG is a core differentiator of the project.
- **Trade-offs:** Community Edition lacks clustering, role-based access, and some enterprise features. But: full Cypher support, APOC procedures, sufficient for demo-scale graph (~5K nodes).
- **Final Selection:** ✅ Neo4j 5 Community (Docker)

---

### DEC-006: React + Vite (No Next.js)
- **Date:** 2026-06-26
- **Decision:** Use plain React with Vite for the frontend, not Next.js
- **Reason:** AEGIS is a single-page dashboard application. It doesn't need server-side rendering (SSR), static site generation (SSG), or Next.js routing. The backend is FastAPI, so adding Next.js would introduce a second server and complicate deployment.
- **Alternatives Considered:**
  1. *Next.js* — SSR, file-based routing, API routes. Rejected: SSR unnecessary for dashboard; adds complexity; conflicts with FastAPI backend.
  2. *Angular* — Enterprise-grade framework. Rejected: steeper learning curve; overkill for this project.
  3. *Vue + Vite* — Simpler than React. Rejected: React has larger ecosystem and more learning resources.
  4. *Svelte* — Excellent performance. Rejected: smaller ecosystem; less hiring appeal for portfolio.
- **Trade-offs:** No SSR means no SEO (irrelevant for a dashboard app). But: faster builds, simpler deployment, cleaner separation from FastAPI backend.
- **Final Selection:** ✅ React + Vite

---

### DEC-007: FastAPI Native WebSockets (No Socket.IO)
- **Date:** 2026-06-26
- **Decision:** Use FastAPI's built-in WebSocket support, not Socket.IO
- **Reason:** FastAPI has excellent native WebSocket support. Adding Socket.IO would require a separate dependency on both backend (python-socketio) and frontend (socket.io-client), with minimal benefit.
- **Alternatives Considered:**
  1. *Socket.IO* — Auto-reconnection, rooms, fallback to polling. Rejected: extra dependency; FastAPI's native WS is sufficient.
  2. *Server-Sent Events (SSE)* — Simpler, HTTP-based. Rejected: unidirectional only; can't receive client messages.
  3. *Supabase Realtime* — Built into Supabase. Rejected: designed for database change events, not custom application events.
- **Trade-offs:** Must implement reconnection logic manually on the frontend. But: no extra dependencies, native FastAPI integration, simpler architecture.
- **Final Selection:** ✅ FastAPI native WebSockets

---

### DEC-008: LangGraph Only (No LlamaIndex)
- **Date:** 2026-06-26
- **Decision:** Use LangGraph (which includes LangChain primitives) as the sole orchestration framework. Do not use LlamaIndex.
- **Reason:** The technical document mentions both LangChain/LlamaIndex, but using both creates duplicated abstractions for retrieval, memory, and agent management. LangGraph provides state-machine-based agent orchestration plus all of LangChain's retrieval tools.
- **Alternatives Considered:**
  1. *LangChain + LlamaIndex* — Both have RAG capabilities. Rejected: overlapping functionality; confusing API boundaries.
  2. *LlamaIndex only* — Good RAG, okay agents. Rejected: LangGraph's state machine is better suited for multi-round agent orchestration.
  3. *Custom orchestrator (no framework)* — Full control. Rejected: reinventing agent state management is not worth the effort.
- **Trade-offs:** LangGraph/LangChain is rapidly evolving (breaking changes risk). But: rich ecosystem, good documentation, industry standard for agent systems.
- **Final Selection:** ✅ LangGraph (with LangChain utilities)

---

### DEC-009: DuckDuckGo for Web Search
- **Date:** 2026-06-26
- **Decision:** Use the `duckduckgo-search` Python package for web search, not Google/Bing/SerpAPI
- **Reason:** Zero cost, no API key required, no rate limit (within reason), and sufficient quality for an academic project.
- **Alternatives Considered:**
  1. *Google Custom Search API* — High quality, 100 free queries/day. Rejected: 100/day is too limiting for development + testing.
  2. *Bing Search API* — Good quality. Rejected: requires Azure subscription and API key; costs money after free tier.
  3. *SerpAPI* — Excellent Google results. Rejected: 100 free searches/month; costs money.
  4. *Tavily* — AI-optimized search. Rejected: limited free tier; API key required.
- **Trade-offs:** DuckDuckGo results may be slightly lower quality than Google/Bing. But: unlimited free usage, no API key, simple integration.
- **Final Selection:** ✅ DuckDuckGo (`duckduckgo-search` package)

---

### DEC-010: Max 2 Rounds for Devil's Advocate Loop
- **Date:** 2026-06-26
- **Decision:** Limit the Devil's Advocate adversarial loop to a maximum of 2 re-run rounds, with a 60-second timeout per round
- **Reason:** Unlimited debate rounds would cause unpredictable latency and LLM cost. 2 rounds provides sufficient adversarial validation while keeping total response time under 60 seconds.
- **Alternatives Considered:**
  1. *Unlimited rounds (until convergence)* — Most thorough. Rejected: unpredictable latency; potential infinite loops; high cost.
  2. *Single round only* — Simplest. Rejected: may miss important contradictions that emerge after initial correction.
  3. *3+ rounds* — More thorough. Rejected: diminishing returns; each round adds 10-15s latency.
- **Trade-offs:** Some valid challenges may be missed in edge cases. But: predictable latency, controlled cost, and 2 rounds catches the vast majority of significant contradictions.
- **Final Selection:** ✅ Max 2 rounds + 60s timeout per round

---

### DEC-011: spaCy for Named Entity Recognition
- **Date:** 2026-06-26
- **Decision:** Use spaCy (en_core_web_sm model) for entity extraction in the GraphRAG pipeline, with optional Gemini fallback for complex documents
- **Reason:** spaCy is free, runs offline (no API calls), is fast (~10ms per document), and provides reliable NER for organizations, people, and locations — the primary entity types needed for the knowledge graph.
- **Alternatives Considered:**
  1. *Gemini for all NER* — Better for complex/ambiguous entities. Rejected as primary: adds latency and API cost for every document.
  2. *Hugging Face NER models* — BERT-based, high quality. Rejected: heavier model loading; more complex setup for marginal quality gain.
  3. *Custom regex/rules* — No ML needed. Rejected: too brittle; misses entity variations.
- **Trade-offs:** spaCy's small model (en_core_web_sm) may miss domain-specific entities. Gemini fallback can handle complex cases when needed.
- **Final Selection:** ✅ spaCy (primary) + Gemini (fallback for complex docs)

---

### DEC-012: Docker Compose Only (No Kubernetes)
- **Date:** 2026-06-26
- **Decision:** Use Docker Compose for all environments (dev, demo). No Kubernetes.
- **Reason:** Kubernetes is designed for multi-node production clusters. A 2-person academic project running on local machines gains zero benefit from Kubernetes while incurring massive operational complexity.
- **Alternatives Considered:**
  1. *Kubernetes (Minikube)* — Production-like. Rejected: overkill; resource-hungry; complex YAML management.
  2. *Docker Swarm* — Simpler orchestration. Rejected: unnecessary for single-machine deployment.
  3. *No containers (bare metal)* — Simplest. Rejected: "it works on my machine" problems; Neo4j installation complexity.
- **Trade-offs:** Cannot demonstrate horizontal scaling or production-grade deployment. But: Docker Compose is standard for development; can mention Kubernetes as future work in the report.
- **Final Selection:** ✅ Docker Compose

---

## UI Decisions

### DEC-013: Shadcn/ui + Tailwind CSS for Frontend Styling
- **Date:** 2026-06-26
- **Decision:** Use Shadcn/ui component library with Tailwind CSS for the React frontend
- **Reason:** Shadcn/ui provides beautiful, accessible, production-quality components that are copy-pasted into your project (not a dependency). Combined with Tailwind CSS, it enables rapid development of premium-looking UIs. Both are free and well-documented.
- **Alternatives Considered:**
  1. *Material UI (MUI)* — Comprehensive. Rejected: Google's Material Design aesthetic may look dated; heavier bundle.
  2. *Ant Design* — Enterprise-grade. Rejected: opinionated styling; harder to customize.
  3. *Chakra UI* — Good DX. Rejected: smaller ecosystem than Tailwind; slightly less flexibility.
  4. *Custom CSS* — Full control. Rejected: too time-consuming for a 2-person team.
- **Trade-offs:** Tailwind requires learning utility-class approach. But: faster development, consistent design, modern aesthetic.
- **Final Selection:** ✅ Shadcn/ui + Tailwind CSS

---

## Data Decisions

### DEC-014: Vertex AI text-embedding-005 for Embeddings
- **Date:** 2026-06-26
- **Decision:** Use Google's text-embedding-005 model via Vertex AI for all text embeddings
- **Reason:** Native GCP integration (covered by credits), high-quality embeddings (768 dimensions), and consistent with the Gemini LLM choice. Using the same cloud provider for LLM and embeddings simplifies authentication and billing.
- **Alternatives Considered:**
  1. *OpenAI text-embedding-ada-002* — Industry standard. Rejected: requires separate API key and budget.
  2. *Sentence-BERT (SBERT)* — Free, local. Rejected: lower quality than Vertex AI; requires model download and GPU for fast inference.
  3. *Cohere Embed* — Good quality. Rejected: requires API key and budget.
- **Trade-offs:** Cloud dependency for embedding generation. But: covered by existing credits; high quality; batch API available for ingestion.
- **Final Selection:** ✅ Vertex AI text-embedding-005

---

### DEC-015: GDELT for Geopolitical Event Data
- **Date:** 2026-06-26
- **Decision:** Use the GDELT (Global Database of Events, Language, and Tone) project for geopolitical event data
- **Reason:** GDELT is the largest open database of global events, updated every 15 minutes, and completely free. It provides structured event data (actors, event types, locations, sentiment) that maps perfectly to the Neo4j graph schema.
- **Alternatives Considered:**
  1. *Global News API* — Curated news. Rejected: paid API key required after free trial.
  2. *NewsAPI.org* — Popular news aggregator. Rejected: free tier limited to 100 requests/day and headlines only.
  3. *RSS feeds only* — Simple, free. Rejected: unstructured; requires significant parsing; inconsistent coverage.
- **Trade-offs:** GDELT data is raw and requires parsing. But: unmatched coverage, free, structured event format, historical data available.
- **Final Selection:** ✅ GDELT + supplementary RSS feeds

---

*This document will be updated as new decisions are made during development.*
