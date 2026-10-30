# AEGIS — Project Explanation

> **For:** Team members, faculty reviewers, viva preparation, and anyone who needs to understand the project quickly
> **Last Updated:** 2026-06-26

---

## What is AEGIS?

**AEGIS** stands for **AI-driven Early Warning Intelligence System**.

Imagine you're a strategic analyst and you need to answer a complex question like:

> *"What would be the impact of new EU AI regulations on US tech companies, considering both financial markets and geopolitical tensions?"*

Today, answering this requires hours of manual research across multiple domains — reading news articles, analyzing stock data, studying policy documents, cross-referencing sources, and synthesizing everything into a coherent brief.

**AEGIS automates this entire process using a team of AI agents that work together, challenge each other, and produce a transparent, confidence-scored intelligence brief in under 60 seconds.**

---

## The Problem We're Solving

Traditional AI chatbots (ChatGPT, Claude, etc.) have fundamental limitations for intelligence analysis:

| Problem | Description |
|---------|-------------|
| **Single perspective** | One LLM gives one opinion — no cross-validation |
| **No source tracking** | You can't verify where information came from |
| **Hallucination risk** | AI confidently states incorrect information |
| **No confidence measure** | You don't know how much to trust the answer |
| **No adversarial testing** | Nobody challenges the AI's claims |
| **Opaque reasoning** | You can't see how the AI reached its conclusion |

**AEGIS solves all of these** by replacing a single AI with a coordinated **team of specialized AI agents** that research, debate, challenge, and score their own work.

---

## How Does AEGIS Work? (The Workflow)

Here's exactly what happens when a user submits a query, step by step:

### Step 1: User Submits a Query
The user types a strategic question into the AEGIS dashboard, for example:
> *"Analyze the impact of semiconductor export controls on the global chip supply chain"*

The query is sent from the **React frontend** to the **FastAPI backend** via a REST API call.

### Step 2: The Orchestrator Takes Over
The **LangGraph Orchestrator** (the "brain" of AEGIS) receives the query and:
1. Decomposes it into **subtasks** — one for each specialist agent
2. Creates a WebSocket channel to stream live updates to the user
3. Dispatches all agents **simultaneously** (in parallel) for speed

```
User Query: "Impact of semiconductor export controls"
  │
  ├── Subtask 1 → Recon Agent: "Gather OSINT on export control policies"
  ├── Subtask 2 → Financial Agent: "Analyze semiconductor stock impacts"
  └── Subtask 3 → Geopolitical Agent: "Map country positions and alliances"
```

### Step 3: Agents Gather Intelligence (In Parallel)

Three specialized agents work **simultaneously**, each with their own data sources and expertise:

#### 🔍 Recon Agent (Intelligence Reconnaissance)
- **What it does:** Searches the open web and official filings for relevant information
- **Data sources:**
  - **DuckDuckGo** — free web search for latest news and articles
  - **SEC Edgar** — official US government financial filings (free)
  - **ChromaDB (RAG)** — searches a pre-loaded knowledge base of documents using AI similarity matching
  - **Neo4j (GraphRAG)** — traverses a knowledge graph of entities and relationships
- **Output:** A list of claims with source citations

#### 💰 Financial Agent
- **What it does:** Analyzes market data and financial implications
- **Data sources:**
  - **Yahoo Finance (yfinance)** — free stock prices, company financials, market data
  - **ChromaDB (RAG)** — retrieves relevant financial news and analysis documents
  - **Neo4j (GraphRAG)** — queries company relationships, supply chains, sector data
- **Output:** Financial analysis with market data and citations

#### 🌍 Geopolitical Agent
- **What it does:** Analyzes political dynamics, policy implications, and international relations
- **Data sources:**
  - **GDELT** — the world's largest free database of global events, updated every 15 minutes
  - **RSS feeds** — major news outlet feeds for breaking news
  - **ChromaDB (RAG)** — retrieves relevant policy documents and analysis
  - **Neo4j (GraphRAG)** — queries geopolitical actor relationships, sanctions, alliances
- **Output:** Geopolitical analysis with policy context and citations

> **Key insight:** These agents don't just ask an AI to guess — they **retrieve real evidence** from databases and the web, then use AI to reason over that evidence.

### Step 4: Devil's Advocate Challenges Everything

This is what makes AEGIS unique. After all agents submit their findings, the **Devil's Advocate Agent** reviews every single claim:

```
For each claim from every agent:
  1. Break the claim into assumptions
  2. Search for counter-evidence (from different sources)
  3. If a valid contradiction is found:
     → Flag the claim as challenged
     → Send the challenged agent back to revise its work
  4. The revised claim is re-checked
  5. This can repeat up to 2 rounds maximum
```

**Example:**
- Financial Agent claims: *"NVIDIA stock will drop 15% due to export controls"*
- Devil's Advocate finds: *SEC filing shows NVIDIA has already diversified supply chains* (Tier 1 source)
- Financial Agent is re-run with this objection → produces a revised, more nuanced claim

The user sees this debate happening **live** on their screen via WebSocket streaming.

### Step 5: Synthesis Agent Compiles the Brief

Once all claims have survived (or been revised through) the adversarial challenge:

- The **Synthesis Agent** collects all validated evidence from all agents
- It composes a structured **strategic intelligence brief** in formal analyst tone
- Every statement includes source citations with trust tiers
- The brief follows a professional format: Executive Summary → Key Findings → Detailed Analysis → Risk Assessment

### Step 6: Confidence Engine Scores Everything

The **Confidence Engine** calculates trust metrics for the entire brief:

| Metric | What It Measures | Example |
|--------|-----------------|---------|
| **Claim Confidence** | How confident we are in each individual claim | 0.87 (87%) |
| **Global Score** | Overall answer confidence | 0.82 (82%) |
| **Evidence Richness** | How many sources back the answer | 3.2 sources/claim |
| **Consensus Score** | How much agents agree with each other | 0.78 (78%) |
| **Challenge Survival Rate** | % of claims that survived Devil's Advocate | 0.85 (85%) |

These scores are **not arbitrary** — they're calculated using a formula based on:
- Number of supporting vs. contradicting sources
- Trust tier of each source (government filings > news > blogs)
- Whether the claim survived adversarial challenge
- How many agents independently reached similar conclusions

### Step 7: User Sees the Result

The final output appears on the dashboard with:
- ✅ A professional strategic brief with sections and citations
- ✅ Real-time log of which agents ran and what they found
- ✅ Which claims were challenged and how they were revised
- ✅ Confidence scores for every claim and the overall answer
- ✅ Source citations with trust tier badges (Tier 1 🟢, Tier 2 🟡, Tier 3 🔴)

---

## What Makes AEGIS Special?

### vs. ChatGPT / Claude / Regular AI

| Feature | ChatGPT | AEGIS |
|---------|---------|-------|
| Multiple specialized agents | ❌ Single model | ✅ 5 agents with different expertise |
| Source citations with trust tiers | ❌ Often fabricates | ✅ Every claim has verified sources |
| Self-challenging (adversarial) | ❌ No self-critique | ✅ Devil's Advocate challenges every claim |
| Confidence scoring | ❌ No confidence measure | ✅ Per-claim and global confidence scores |
| Knowledge graph reasoning | ❌ Text only | ✅ Neo4j graph for entity relationships |
| Real-time transparency | ❌ Black box | ✅ Watch agents work live via WebSocket |
| Evidence retrieval (RAG) | ❌ Training data only | ✅ Searches real databases and web |

### Key Technical Innovations

1. **Hybrid RAG + GraphRAG** — Combines traditional vector similarity search (ChromaDB) with knowledge graph traversal (Neo4j) for richer context retrieval
2. **Adversarial Self-Validation** — The only system that automatically challenges its own conclusions before presenting them
3. **Source Trust Framework** — Tiered credibility scoring where government filings rank higher than blog posts
4. **Confidence Quantification** — Mathematical formulas that turn qualitative trust into quantifiable scores

---

## The Technology Stack

### Complete Stack Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER'S BROWSER                              │
│                                                                  │
│   React + Vite + Shadcn/ui + Tailwind CSS                       │
│   ┌──────────┐ ┌──────────────┐ ┌───────────────────────────┐  │
│   │ Query UI │ │ Agent Stream │ │ Brief + Confidence Scores │  │
│   └────┬─────┘ └──────▲───────┘ └────────────▲──────────────┘  │
│        │ REST          │ WebSocket            │ REST             │
└────────┼───────────────┼─────────────────────┼──────────────────┘
         │               │                      │
┌────────▼───────────────┼──────────────────────┼──────────────────┐
│              FASTAPI BACKEND (Python)                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  LangGraph Orchestrator                                    │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────────┐                │  │
│  │  │  Recon  │ │Financial │ │Geopolitical │  ← Parallel     │  │
│  │  │ (Flash) │ │ (Flash)  │ │  (Flash)    │                 │  │
│  │  └────┬────┘ └────┬─────┘ └──────┬──────┘                │  │
│  │       └───────────┬───────────────┘                        │  │
│  │          ┌────────▼─────────┐                              │  │
│  │          │Devil's Advocate  │ ← Gemini Pro (better reason.)│  │
│  │          │  (max 2 rounds)  │                              │  │
│  │          └────────┬─────────┘                              │  │
│  │          ┌────────▼─────────┐                              │  │
│  │          │Synthesis Agent   │ ← Gemini Pro                 │  │
│  │          └────────┬─────────┘                              │  │
│  │          ┌────────▼─────────┐                              │  │
│  │          │Confidence Engine │                              │  │
│  │          └──────────────────┘                              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ ChromaDB │  │  Neo4j   │  │ Supabase  │  │Free APIs:     │  │
│  │(embedded)│  │ (Docker) │  │ (cloud)   │  │DuckDuckGo     │  │
│  │Vector DB │  │ Graph DB │  │ DB + Auth │  │yfinance       │  │
│  └──────────┘  └──────────┘  └───────────┘  │GDELT, SEC     │  │
│                                              └───────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Technology Breakdown

#### 🧠 AI & Intelligence Layer (Shlok's Domain)

| Technology | What It Does | Why We Chose It |
|-----------|-------------|----------------|
| **Gemini 1.5 Flash** | Powers Recon, Financial, and Geopolitical agents | Fastest Gemini model (~2-5s response); optimized for low latency |
| **Gemini 1.5 Pro** | Powers Synthesis and Devil's Advocate agents | Superior reasoning quality for complex analysis and critique |
| **Vertex AI** | Google Cloud AI platform that hosts Gemini models | $1,000 in free credits; ~90,000 queries of runway |
| **LangGraph** | Orchestrates the multi-agent workflow as a state machine | Industry-standard for complex agent workflows with conditional routing |
| **ChromaDB** | Vector database for RAG (Retrieval-Augmented Generation) | Free, embedded mode (zero latency), handles ~1M vectors |
| **Neo4j** | Graph database for GraphRAG | Free Community Edition; Cypher queries for entity relationships |
| **spaCy** | Named Entity Recognition (NER) for graph population | Free, fast (~10ms/doc), runs offline |
| **text-embedding-005** | Converts text into numerical vectors for similarity search | Google's embedding model; covered by Vertex AI credits |

#### 🌐 Platform Layer (Aditya's Domain)

| Technology | What It Does | Why We Chose It |
|-----------|-------------|----------------|
| **React** | Frontend JavaScript framework for the dashboard UI | Largest ecosystem, component-based, excellent DevTools |
| **Vite** | Build tool for the React app | Instant hot-reload, fast builds, modern JS tooling |
| **Shadcn/ui** | Beautiful, accessible UI component library | Premium-looking components; free; copy-paste (not a dependency) |
| **Tailwind CSS** | Utility-first CSS framework for styling | Rapid development, consistent design, modern aesthetic |
| **FastAPI** | Python backend framework for REST APIs and WebSockets | Async-first, auto-docs (Swagger), built-in WebSocket support |
| **Supabase** | Cloud platform providing PostgreSQL + Auth + Realtime | Free tier: 500MB DB, built-in JWT auth, row-level security |
| **Docker Compose** | Containers for running all services together | One command to start everything; consistent across machines |
| **GitHub Actions** | CI/CD for automated linting and testing | Free for public repos; runs on every push/PR |

#### 📡 External Data Sources (All Free)

| Source | Data Type | Cost |
|--------|-----------|------|
| **DuckDuckGo** | Web search results | Free, no API key |
| **SEC Edgar** | US government financial filings | Free, no API key |
| **Yahoo Finance (yfinance)** | Stock prices, market data, company financials | Free, no API key |
| **GDELT** | Global geopolitical events (updated every 15 min) | Free, no API key |
| **RSS Feeds** | Breaking news from major outlets | Free |

---

## What is RAG? (Retrieval-Augmented Generation)

**RAG** is the technique that prevents AI from hallucinating. Instead of relying solely on training data, the AI **retrieves relevant documents first**, then uses them as context to generate an answer.

### How RAG Works in AEGIS

```
                    The AI doesn't guess — it reads real evidence first

1. INGESTION (done beforehand)
   ┌──────────────┐     ┌───────────┐     ┌─────────────┐     ┌──────────┐
   │ PDF / Text   │ ──► │  Chunk    │ ──► │  Embed      │ ──► │ ChromaDB │
   │ documents    │     │ into 500  │     │ into vectors│     │ (stored) │
   └──────────────┘     │ token pcs │     │ via Vertex  │     └──────────┘
                        └───────────┘     └─────────────┘

2. RETRIEVAL (at query time)
   ┌──────────┐     ┌───────────┐     ┌─────────────┐     ┌──────────────┐
   │ User     │ ──► │ Embed     │ ──► │ Search      │ ──► │ Top 8 most   │
   │ query    │     │ query     │     │ ChromaDB    │     │ relevant     │
   └──────────┘     └───────────┘     │ by cosine   │     │ chunks       │
                                      │ similarity  │     └──────┬───────┘
                                      └─────────────┘            │
                                                                 │
3. GENERATION                                                    ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Gemini prompt: "Based on these documents: [chunks],           │
   │  answer: [user query]. Cite your sources."                     │
   └─────────────────────────────────────────────────────────────────┘
```

### What is GraphRAG? (Our Enhancement)

Standard RAG finds documents by **text similarity** — but misses **relationships** between entities. GraphRAG adds a knowledge graph layer:

```
Standard RAG:  "Find documents similar to 'NVIDIA export controls'"
               → Returns text chunks mentioning NVIDIA

GraphRAG:      "Find documents similar to 'NVIDIA export controls'"
               → Returns text chunks mentioning NVIDIA
               + ALSO queries Neo4j:
                 NVIDIA ──supplies_to──► Apple, Microsoft, Tesla
                 NVIDIA ──headquartered_in──► USA
                 USA ──sanctioned──► China (chip exports)
                 NVIDIA ──has_competitor──► AMD, Intel

               → The AI now has BOTH textual context AND
                 structured relationship knowledge
```

This is why AEGIS produces richer, more connected analysis than standard RAG systems.

---

## What is the Confidence Engine?

The Confidence Engine answers: **"How much should I trust this answer?"**

### Per-Claim Scoring

Every claim gets a confidence score (0% to 100%) based on:

```
confidence = base_confidence
             + 0.1 × (supporting_sources - contradicting_sources)
             + 0.2 × (survived_challenge ? +1 : -1)
```

**Example:**
| Factor | Value | Impact |
|--------|-------|--------|
| Base confidence (from agent) | 0.70 | — |
| Supported by 3 sources, contradicted by 1 | +0.2 | 3-1 = 2, × 0.1 |
| Survived Devil's Advocate challenge | +0.2 | × 0.2 |
| **Final confidence** | **0.90 (90%)** | — |

### Source Trust Tiers

Not all sources are equal. A government filing is more trustworthy than a blog post:

| Tier | Trust Score | Examples |
|------|-----------|----------|
| 🟢 **Tier 1** (Official) | 0.85 – 1.0 | Government reports, SEC filings, academic journals |
| 🟡 **Tier 2** (Major) | 0.60 – 0.84 | Reuters, Bloomberg, BBC, major think-tanks |
| 🔴 **Tier 3** (General) | 0.30 – 0.59 | Blogs, social media, opinion pieces |

---

## What Does the User See?

### The Dashboard Experience

When a user submits a query, they see:

1. **Real-time Agent Activity Panel** — Watch each agent start, search, and complete
2. **Challenge Notifications** — See when Devil's Advocate challenges a claim
3. **Strategic Brief** — Professional formatted analysis with sections
4. **Confidence Badges** — Per-claim confidence scores with color coding
5. **Source Citations** — Click to see the original source with tier badge
6. **Global Metrics** — Overall confidence, evidence richness, consensus score

### Example Output Preview

```
╔══════════════════════════════════════════════════════════╗
║  AEGIS Strategic Intelligence Brief                      ║
║  Query: "Impact of EU AI Act on US tech companies"       ║
║  Confidence: 82% 🟢                                     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  EXECUTIVE SUMMARY                                       ║
║  The EU AI Act will significantly impact US tech...      ║
║                                                          ║
║  KEY FINDINGS                                            ║
║  ┌────────────────────────────────────────────────────┐  ║
║  │ 1. Compliance costs estimated at $5-15M per firm   │  ║
║  │    Confidence: 87% 🟢                              │  ║
║  │    Sources: EU AI Act text [Tier 1], Reuters [T2]  │  ║
║  │    ✅ Survived Devil's Advocate challenge           │  ║
║  ├────────────────────────────────────────────────────┤  ║
║  │ 2. High-risk AI systems require conformity assess. │  ║
║  │    Confidence: 92% 🟢                              │  ║
║  │    Sources: EU Official Journal [T1], NIST [T1]    │  ║
║  ├────────────────────────────────────────────────────┤  ║
║  │ 3. US tech lobbying may delay enforcement          │  ║
║  │    Confidence: 61% 🟡                              │  ║
║  │    Sources: Politico [T2], blog analysis [T3]      │  ║
║  │    ⚠️ Challenged by Devil's Advocate - revised     │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
║  AGENT ACTIVITY LOG                                      ║
║  ✅ Recon Agent: 5 claims, 3.2s                          ║
║  ✅ Financial Agent: 4 claims, 4.1s                      ║
║  ✅ Geopolitical Agent: 3 claims, 3.8s                   ║
║  ⚔️ Devil's Advocate: 2 challenges, 1 revision           ║
║  ✅ Synthesis: Brief compiled, 2.1s                      ║
║  Total time: 28s                                         ║
╚══════════════════════════════════════════════════════════╝
```

---

## Project Cost Summary

| Resource | Cost | Notes |
|----------|------|-------|
| Gemini LLM (Vertex AI) | $1,000 credits (free) | ~90,000 queries of runway |
| All other infrastructure | $0 | Everything is free-tier or open-source |
| **Total project cost** | **$0** | — |
| Est. cost per query | ~$0.011 | Well within credit budget |

---

## Project Timeline

| Weeks | Milestone | What Gets Built |
|-------|-----------|----------------|
| 1-2 | Foundation | Docker setup, shared schemas, project skeleton |
| 3-5 | RAG + Backend | ChromaDB, Recon Agent, FastAPI APIs, basic frontend |
| 5-7 | GraphRAG | Neo4j, entity extraction, hybrid retrieval |
| 7-10 | Multi-Agent | Financial + Geo agents, LangGraph orchestrator, Synthesis |
| 10-13 | Adversarial + Confidence | Devil's Advocate, confidence scoring, trust engine |
| 13-16 | Polish + Demo | Integration testing, UI polish, demo preparation |

**Deadline: ~8 weeks from now (end of August 2026)**

---

## Team Structure

| Member | Role | Owns |
|--------|------|------|
| **Shlok Noval** | Lead AI Architect | Agents, LangGraph, RAG, GraphRAG, Neo4j, Confidence Engine, Predictive Forecasting |
| **Aditya** | Lead Platform Engineer | Frontend, FastAPI, Supabase, Auth, WebSocket, Docker, CI/CD |
| **Both** | Shared | Integration testing, documentation, demo, final report |

---

## One-Paragraph Summary (For Presentations)

> AEGIS is an autonomous multi-agent intelligence platform that produces transparent, evidence-grounded strategic briefs with multi-horizon predictive outcome forecasting. When a user submits any strategic query, LangGraph dispatches three specialized AI agents (Recon, Financial, Geopolitical) in parallel to gather live OSINT, real-time market valuations (yfinance), and policy intelligence (GraphRAG). A dedicated Devil's Advocate agent challenges claims by evaluating counter-evidence (stockpiles, recycling, alternative routing, waivers), triggering targeted agent re-runs. A Synthesis Engine compiles the vetted evidence into an analyst-grade dossier featuring 3 probability-weighted scenarios (Baseline 65%, Escalation 25%, Mitigation 10%), a 30/90/180-day timeline horizon, and actionable countermeasures, while a Confidence Engine mathematically quantifies trust using source credibility tiers and adversarial survival rates.

---

## Viva Evaluation Defense & PPT Cheat Sheet

### 1. The Predictive Outcome Forecasting Engine

Unlike traditional chatbots that simply summarize past documents, AEGIS provides **forward-looking strategic foresight**:

1. **Probability-Weighted Multi-Horizon Modeling:**
   - **Baseline Scenario (~65% Probability):** The most likely operational trajectory over 30–90 days, accounting for institutional absorption, secondary market buffers, and standard regulatory enforcement.
   - **Escalation / Disruption Scenario (~25% Probability):** The high-impact risk trajectory over 90–180 days, triggered by retaliatory sanctions, critical chokepoint closures, or acute supply crunches.
   - **Mitigation / De-escalation Scenario (~10% Probability):** The adaptation trajectory over 180+ days, driven by bilateral waivers, international trade corridors, or recycling ramp-ups.
2. **Temporal Impact Progression (30 / 90 / 180 Days):**
   - **T+30 Days (Shock):** Immediate inventory audits, emergency buffer allocations, and statutory filings.
   - **T+90 Days (Realignment):** Contract renegotiations, financial hedging adjustments, and secondary supplier qualification.
   - **T+180 Days (Equilibrium):** Structural realignment, dual-sourced supply chain architectures, and sovereign capex reallocation.

---

### 2. Top 10 Viva Questions & Expert Answers

#### Q1: What is the fundamental advantage of LangGraph over traditional linear LangChain chains?
**Answer:** Traditional chains are Directed Acyclic Graphs (DAGs) that only move forward in a single linear pass. Strategic intelligence requires **cycles and stateful conditional re-investigation**. LangGraph implements a cyclic state machine where nodes (agents) mutate a shared, typed state dictionary (`OrchestratorState`). If the Devil's Advocate raises an evidentiary challenge, the conditional router (`should_continue`) routes execution back to the challenged agent for a revision pass, capped at `MAX_DEBATE_ROUNDS=2` to ensure guaranteed mathematical termination.

#### Q2: Why combine Vector RAG (ChromaDB) with GraphRAG (Neo4j)?
**Answer:** Vector search relies on cosine similarity in semantic embedding space. It excels at finding paragraphs describing concepts (e.g. "what are the DUV restrictions?"), but is blind to multi-hop relational dependencies. GraphRAG extracts named entities (Organizations, Countries, Policies) into a Neo4j property graph. When queried, it traverses 1-to-2 hop relationships (e.g., `ASML -[SUPPLIES_TO]-> TSMC -[FABRICATES_FOR]-> NVIDIA -[DEPENDS_ON]-> HBM3e`). Fusing vector chunks with graph relational paths (`hybrid.py`) gives the LLM both unstructured textual depth and structured dependency topology.

#### Q3: How does the Devil's Advocate prevent circular arguments or infinite debate loops?
**Answer:** Three controls ensure convergence:
1. **Bounded State Counter:** The orchestrator enforces `max_rounds=2`.
2. **Single Challenge per Round:** The DA focuses scrutiny on the highest-impact unchallenged claim.
3. **Evidentiary Bar:** Challenges must cite counter-evidence (e.g., secondary scrap recycling supplying 30% of gallium, domestic stockpiles, third-party logistics rerouting). The originating agent must integrate this counter-evidence in its revised statement rather than stubbornly repeating its initial claim.

#### Q4: How is the Confidence Engine formula derived and calibrated?
**Answer:** The formula balances three empirical factors:
$$\text{Confidence} = \max\left(0.1, \min\left(1.0, \text{Base} + \alpha(\text{Support} - \text{Contradict}) + \beta(\text{Survived})\right)\right)$$
- $\text{Base}$ is anchored to the source credibility tier (Tier 1 = 0.90, Tier 2 = 0.80, Tier 3 = 0.50).
- $\alpha = 0.1$ rewards cross-source corroboration and penalizes uncorroborated assertions.
- $\beta = 0.2$ provides a significant trust boost for surviving adversarial scrutiny or penalizes claims that failed to defend against challenges.
Global confidence aggregates claim scores weighted by average source credibility.

#### Q5: How does the system handle real-time market and commodity volatility?
**Answer:** The `FinancialAgent` does not rely on static training data. It uses a dynamic keyword-to-ticker resolver that detects assets mentioned in any query (`NVDA`, `TSM`, `ASML`, `CL=F` for Crude Oil, `GC=F` for Gold, `LMT`/`ITA` for Defense primes, `QQQ`, `SPY`). It queries `yfinance` live to fetch real-time market prices, currency, 24h percentage change, and market capitalization, infusing real numbers directly into its strategic claims.

#### Q6: What happens if Vertex AI or the Gemini API is offline during the viva demo?
**Answer:** AEGIS is engineered with a **Dual-Mode Resilient Architecture** (`backend/app/shared/llm.py`). When `GEMINI_API_KEY` is present, it uses Gemini 1.5 Pro and Flash. If the key is absent or network drops occur, AEGIS seamlessly falls back to its built-in analytical heuristic engine. It extracts entities via spaCy, queries local ChromaDB vectors, retrieves live market quotes via yfinance, and synthesizes structured multi-scenario briefings with 100% zero downtime.

#### Q7: Why use WebSockets instead of HTTP polling for live agent activity?
**Answer:** Intelligence gathering takes 10–25 seconds across multiple parallel operatives. HTTP polling introduces latency, server load, and jitter. The FastAPI WebSocket manager (`/ws/{query_id}`) creates a persistent bi-directional channel that streams granular state transitions (`agent_started`, `agent_completed`, `challenge_raised`, `synthesis_started`, `briefing_ready`) as they occur, driving the real-time visual LangGraph pipeline on the React frontend.

#### Q8: How are source tiers structured and verified?
**Answer:** Sources are strictly partitioned into three credibility tiers:
- **Tier 1 (Official & Statutory, Trust 0.85–1.0):** Government gazettes, BIS directives, SEC 10-K filings, EU Official Journal, USGS commodity summaries, Lloyd's Market Association tariffs.
- **Tier 2 (Major Institutional Press, Trust 0.60–0.84):** Reuters, Bloomberg, Nikkei Asia, BBC World, major think tanks.
- **Tier 3 (Open Web & Commentary, Trust 0.30–0.59):** General blogs, social media posts, unverified forums.

#### Q9: How was the project divided between team members?
**Answer:**
- **Shlok Noval (Lead AI Architect):** Multi-agent LangGraph orchestrator, Recon/Financial/Geopolitical agent design, Devil's Advocate adversarial loop, Hybrid GraphRAG (ChromaDB + Neo4j), Confidence Engine mathematical scoring, and Predictive Outcome Modeling.
- **Aditya (Lead Platform Engineer):** Defense War Room React frontend, WebSocket streaming architecture, FastAPI REST endpoints, Supabase PostgreSQL persistence, Docker containerization, and GitHub Actions CI/CD.

#### Q10: What makes AEGIS superior to a generic enterprise chatbot?
**Answer:** Generic chatbots produce single-perspective, opaque text without verifiable provenance or self-challenge. AEGIS provides:
1. Multi-domain parallel intelligence gathering.
2. Adversarial stress-testing of every conclusion.
3. Quantifiable, explainable confidence metrics.
4. An interactive Evidence Citation Inspector linking every statement to its exact source and trust tier.
5. Actionable predictive outcome scenarios with probability ratings.

