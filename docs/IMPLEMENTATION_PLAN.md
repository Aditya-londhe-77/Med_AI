# AEGIS — Master Implementation Plan

> **Document Type:** Permanent Source of Truth
> **Created:** 2026-06-26
> **Last Updated:** 2026-09-06
> **Status:** Fully Implemented, Tested & Ready for Final Viva Defense (Milestones 1–6 Complete)

---

## 1. Project Vision

AEGIS (AI-driven Early Warning Intelligence System) is an orchestrator-led multi-agent intelligence platform that produces transparent, evidence-grounded strategic briefs. Unlike single-LLM pipelines that produce opaque, unverified answers, AEGIS deploys a coordinated team of specialized AI agents that independently gather intelligence, self-challenge conclusions through adversarial debate, and quantify confidence — delivering analyst-grade strategic briefings with full source traceability.

### Core Differentiators
1. **Multi-Agent Specialization** — Domain-specific agents (Recon, Financial, Geopolitical) with tailored tools and prompts
2. **Adversarial Self-Validation** — Devil's Advocate agent that challenges every claim, triggering targeted re-runs
3. **GraphRAG** — Hybrid retrieval combining vector similarity (ChromaDB) with knowledge graph traversal (Neo4j)
4. **Confidence Quantification** — Per-claim and global confidence scoring with full explainability
5. **Source Trust Framework** — Tiered source credibility with trust propagation across evidence networks

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React + Vite Frontend                     │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│   │ Query UI │  │ Agent Stream │  │ Briefing + Confidence    │  │
│   └────┬─────┘  └──────▲───────┘  └──────────▲───────────────┘  │
│        │               │                      │                  │
│        │          WebSocket                   │                  │
└────────┼───────────────┼──────────────────────┼──────────────────┘
         │               │                      │
    REST POST       WS Push                REST GET
         │               │                      │
┌────────▼───────────────┼──────────────────────┼──────────────────┐
│                   FastAPI Backend (Monolithic)                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  LangGraph Orchestrator                      │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐            │ │
│  │  │  Recon   │  │ Financial │  │ Geopolitical │  (parallel) │ │
│  │  │  Agent   │  │  Agent    │  │   Agent      │            │ │
│  │  └────┬─────┘  └─────┬─────┘  └──────┬───────┘            │ │
│  │       │              │               │                     │ │
│  │       └──────────────┼───────────────┘                     │ │
│  │                      ▼                                     │ │
│  │            ┌───────────────────┐                           │ │
│  │            │ Devil's Advocate  │ ◄── max 2 rounds          │ │
│  │            │     Agent         │                           │ │
│  │            └────────┬──────────┘                           │ │
│  │                     ▼                                      │ │
│  │            ┌───────────────────┐                           │ │
│  │            │ Synthesis Agent   │                           │ │
│  │            └────────┬──────────┘                           │ │
│  │                     ▼                                      │ │
│  │            ┌───────────────────┐                           │ │
│  │            │ Confidence Engine │                           │ │
│  │            └───────────────────┘                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ ChromaDB │  │  Neo4j   │  │ Supabase  │  │  External     │  │
│  │ (embed.) │  │ (Docker) │  │ (cloud)   │  │  APIs (free)  │  │
│  └──────────┘  └──────────┘  └───────────┘  └───────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Architecture Principles
1. **Monolithic backend** with modular package boundaries (no microservices)
2. **Async-first** — all I/O operations use `asyncio` for parallelism
3. **Schema-driven** — Pydantic models define all data contracts
4. **Stream-first** — WebSocket pushes updates as they happen
5. **Zero-cost infrastructure** — all services free-tier or GCP credits

---

## 3. Agent Architecture

### Base Agent Contract

Every agent implements this interface:

```python
class BaseAgent(ABC):
    """Base agent interface. All agents must implement this."""
    
    agent_name: str
    llm_model: str  # "gemini-1.5-flash" or "gemini-1.5-pro"
    
    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent's task and return structured output."""
        pass
    
    async def retrieve_context(self, query: str) -> list[RetrievedChunk]:
        """RAG retrieval from ChromaDB."""
        pass
    
    async def query_graph(self, cypher: str) -> list[GraphResult]:
        """GraphRAG query from Neo4j."""
        pass
```

### Agent Specifications

| Agent | LLM | Purpose | Tools | Priority |
|-------|-----|---------|-------|----------|
| **Recon** | Gemini 1.5 Flash | OSINT gathering | DuckDuckGo, SEC Edgar, RAG, GraphRAG | P0 |
| **Financial** | Gemini 1.5 Flash | Market & financial analysis | yfinance, financial RAG, GraphRAG | P0 |
| **Geopolitical** | Gemini 1.5 Flash | Policy & geopolitical context | GDELT, RSS feeds, policy RAG, GraphRAG | P0 |
| **Devil's Advocate** | Gemini 1.5 Pro | Adversarial claim challenge | RAG, GraphRAG, source trust DB | P0 |
| **Synthesis** | Gemini 1.5 Pro | Final briefing compilation | All agent outputs, confidence scores | P0 |

### Agent I/O Schemas

```python
class AgentRequest(BaseModel):
    query: str
    subtask: str
    context: dict = {}              # Orchestrator-injected context
    objection: str | None = None    # Devil's Advocate objection (for re-runs)
    max_sources: int = 10
    source_tiers: list[int] = [1, 2, 3]

class Claim(BaseModel):
    claim_id: str
    text: str
    confidence: float               # 0.0 - 1.0
    sources: list[SourceCitation]
    assumptions: list[str]

class SourceCitation(BaseModel):
    source_id: str
    title: str
    url: str | None
    excerpt: str
    tier: int                       # 1=official, 2=major news, 3=blogs
    trust_score: float              # 0.0 - 1.0
    retrieved_at: datetime

class AgentResponse(BaseModel):
    agent_name: str
    status: Literal["success", "error", "partial"]
    claims: list[Claim]
    reasoning: str
    evidence_summary: str
    execution_time_ms: int
    llm_tokens_used: int
    error: str | None = None
```

---

## 4. Data Flow

### Query Processing Pipeline

```
1. User submits query via React UI
   └── POST /api/query { query: "Impact of new EU AI Act on tech companies" }

2. FastAPI receives, validates, creates session in Supabase
   └── Assigns query_id, creates WebSocket channel

3. LangGraph Orchestrator decomposes query into subtasks
   └── Subtask 1: "Gather OSINT on EU AI Act provisions"
   └── Subtask 2: "Analyze financial impact on major tech stocks"
   └── Subtask 3: "Map geopolitical implications and country positions"

4. Parallel Agent Execution (via asyncio.gather)
   ├── Recon Agent
   │   ├── DuckDuckGo search → web results
   │   ├── ChromaDB RAG → relevant document chunks
   │   ├── Neo4j GraphRAG → entity relationships
   │   └── Returns: AgentResponse with claims
   ├── Financial Agent
   │   ├── yfinance → stock/market data
   │   ├── ChromaDB RAG → financial news chunks
   │   ├── Neo4j GraphRAG → company/sector relationships
   │   └── Returns: AgentResponse with claims
   └── Geopolitical Agent
       ├── GDELT → geopolitical events
       ├── ChromaDB RAG → policy document chunks
       ├── Neo4j GraphRAG → actor/alliance relationships
       └── Returns: AgentResponse with claims

5. Devil's Advocate Review (max 2 rounds)
   ├── Round 1: Reviews all claims, generates challenges
   │   ├── If valid challenges → targeted re-run of challenged agent
   │   └── WebSocket: push challenge notifications
   └── Round 2: Reviews revised claims
       └── If still challenged → final note; proceed anyway

6. Synthesis Agent compiles final briefing
   └── Structured narrative with citations and confidence annotations

7. Confidence Engine scores everything
   └── Per-claim scores + global confidence + trust metrics

8. Result streamed to frontend via WebSocket
   └── Final briefing stored in Supabase
```

---

## 5. API Architecture

### REST Endpoints

| Method | Path | Description | Owner |
|--------|------|-------------|-------|
| `POST` | `/api/query` | Submit a new intelligence query | Aditya |
| `GET` | `/api/query/{id}` | Get query result by ID | Aditya |
| `GET` | `/api/query/{id}/status` | Get query processing status | Aditya |
| `GET` | `/api/history` | List past queries | Aditya |
| `DELETE` | `/api/query/{id}` | Delete a query and its results | Aditya |
| `GET` | `/api/health` | Health check | Aditya |
| `POST` | `/api/auth/signup` | Register (via Supabase) | Aditya |
| `POST` | `/api/auth/login` | Login (via Supabase) | Aditya |
| `POST` | `/api/auth/logout` | Logout | Aditya |
| `GET` | `/api/auth/me` | Current user info | Aditya |

### WebSocket

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `connect` | Client→Server | `{ token, query_id }` | Establish WS for a query |
| `agent_started` | Server→Client | `{ agent_name, subtask }` | Agent begins execution |
| `agent_completed` | Server→Client | `{ agent_name, claims_count, time_ms }` | Agent finished |
| `challenge_raised` | Server→Client | `{ agent_name, claim_id, challenge }` | DA found an issue |
| `agent_rerun` | Server→Client | `{ agent_name, reason }` | Agent re-executing |
| `synthesis_started` | Server→Client | `{}` | Synthesis begins |
| `briefing_ready` | Server→Client | `{ briefing, confidence }` | Final result |
| `error` | Server→Client | `{ message, code }` | Error occurred |

### Request/Response Examples

```json
// POST /api/query
{
  "query": "What is the impact of new EU AI regulations on US tech companies?",
  "options": {
    "max_rounds": 2,
    "source_tiers": [1, 2],
    "include_graph_context": true
  }
}

// Response (or via WebSocket briefing_ready)
{
  "query_id": "q_abc123",
  "briefing": {
    "title": "Impact Analysis: EU AI Act on US Tech Sector",
    "executive_summary": "...",
    "sections": [...],
    "claims": [
      {
        "claim_id": "c_001",
        "text": "Major US tech companies will face compliance costs...",
        "confidence": 0.87,
        "sources": [
          { "title": "EU AI Act Final Text", "tier": 1, "trust_score": 0.95 }
        ]
      }
    ]
  },
  "confidence": {
    "global_score": 0.82,
    "evidence_richness": 0.90,
    "consensus_score": 0.78,
    "challenge_survival_rate": 0.85
  },
  "metadata": {
    "total_time_ms": 28000,
    "agents_used": ["recon", "financial", "geopolitical"],
    "da_rounds": 1,
    "total_tokens": 15420
  }
}
```

---

## 6. Database Architecture

### Supabase PostgreSQL Schema

```sql
-- Users (managed by Supabase Auth, extended here)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    display_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Query sessions
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    query_text TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed
    options JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    total_time_ms INTEGER
);

-- Agent executions within a query
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    subtask TEXT,
    status TEXT DEFAULT 'pending',
    response JSONB,           -- Full AgentResponse JSON
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    round_number INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Final briefings
CREATE TABLE briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID UNIQUE REFERENCES queries(id) ON DELETE CASCADE,
    title TEXT,
    executive_summary TEXT,
    full_briefing JSONB,      -- Complete structured briefing
    confidence JSONB,         -- Confidence metrics
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Claims (per-claim tracking for confidence engine)
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    claim_text TEXT NOT NULL,
    confidence_before FLOAT,
    confidence_after FLOAT,
    support_count INTEGER DEFAULT 0,
    contradict_count INTEGER DEFAULT 0,
    trust_score FLOAT,
    challenged BOOLEAN DEFAULT FALSE,
    challenge_text TEXT,
    revised BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Source citations
CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    source_title TEXT,
    source_url TEXT,
    excerpt TEXT,
    tier INTEGER CHECK (tier BETWEEN 1 AND 3),
    trust_score FLOAT,
    supports_claim BOOLEAN DEFAULT TRUE,
    retrieved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_queries_user ON queries(user_id);
CREATE INDEX idx_queries_status ON queries(status);
CREATE INDEX idx_agent_exec_query ON agent_executions(query_id);
CREATE INDEX idx_claims_query ON claims(query_id);
CREATE INDEX idx_citations_claim ON citations(claim_id);
```

### Row-Level Security (RLS)

```sql
-- Users can only see their own queries
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
CREATE POLICY queries_user_policy ON queries
    FOR ALL USING (user_id = auth.uid());

-- Cascade to related tables
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;
CREATE POLICY briefings_user_policy ON briefings
    FOR ALL USING (query_id IN (SELECT id FROM queries WHERE user_id = auth.uid()));
```

---

## 7. Neo4j Graph Design

### Node Types

| Label | Properties | Description |
|-------|-----------|-------------|
| `Organization` | name, type, country, sector, description | Companies, NGOs, govt bodies |
| `Person` | name, title, organization, nationality | Key individuals |
| `Country` | name, iso_code, region, gdp | Nations |
| `Event` | name, date, type, description, impact_score | Geopolitical/financial events |
| `Product` | name, category, organization | Products/services |
| `Policy` | name, jurisdiction, effective_date, description | Regulations/policies |
| `Document` | doc_id, title, source, tier, url, ingested_at | Source documents |
| `Chunk` | chunk_id, text, doc_id, embedding_id | Document chunks (links to ChromaDB) |

### Edge Types

| Type | From → To | Properties |
|------|-----------|-----------|
| `HAS_INVESTOR` | Organization → Organization | stake_pct, since |
| `HAS_COMPETITOR` | Organization → Organization | market |
| `HEADQUARTERED_IN` | Organization → Country | |
| `OPERATES_IN` | Organization → Country | since |
| `AFFILIATED_WITH` | Person → Organization | role, since |
| `ENACTED` | Country → Policy | date |
| `AFFECTED_BY` | Organization → Event | impact |
| `RELATED_TO` | Event → Event | relationship_type |
| `SUPPLIES_TO` | Organization → Organization | product_category |
| `SANCTIONED_BY` | Country → Country | since, reason |
| `ALLIED_WITH` | Country → Country | treaty |
| `HAS_CHUNK` | Document → Chunk | position |
| `MENTIONS` | Chunk → Organization/Person/Country | count |

### Example Cypher Queries

```cypher
// Find all companies affected by a policy
MATCH (p:Policy {name: "EU AI Act"})<-[:ENACTED]-(c:Country)
MATCH (o:Organization)-[:OPERATES_IN]->(c)
RETURN o.name, c.name, p.effective_date

// Multi-hop: Find competitors of companies in a supply chain
MATCH (target:Organization {name: "NVIDIA"})
      -[:SUPPLIES_TO]->(customer:Organization)
      -[:HAS_COMPETITOR]->(competitor:Organization)
RETURN customer.name, competitor.name

// Get document chunks mentioning an entity
MATCH (e:Organization {name: "Palantir"})<-[:MENTIONS]-(chunk:Chunk)
      <-[:HAS_CHUNK]-(doc:Document)
RETURN doc.title, chunk.text, doc.tier
ORDER BY doc.tier ASC
```

---

## 8. ChromaDB Design

### Collection Schema

| Collection | Embedding Model | Metadata Fields | Purpose |
|-----------|----------------|----------------|---------|
| `recon_docs` | text-embedding-005 | source, tier, date, doc_id, url | Recon Agent retrieval |
| `financial_docs` | text-embedding-005 | source, tier, date, doc_id, sector | Financial Agent retrieval |
| `geopolitical_docs` | text-embedding-005 | source, tier, date, doc_id, region | Geopolitical Agent retrieval |
| `general_docs` | text-embedding-005 | source, tier, date, doc_id | Cross-agent fallback |

### Chunking Strategy

```python
CHUNK_CONFIG = {
    "chunk_size": 500,          # tokens
    "chunk_overlap": 50,        # tokens
    "separator": "\n\n",        # paragraph-level splits
    "metadata_fields": ["source", "tier", "date", "doc_id"],
}
```

### Retrieval Parameters

```python
RETRIEVAL_CONFIG = {
    "top_k": 8,                 # chunks per query
    "similarity_threshold": 0.7, # minimum cosine similarity
    "rerank": True,             # re-rank by source tier weight
    "tier_weights": {1: 1.5, 2: 1.0, 3: 0.5},
    "time_decay_days": 90,      # recency weight halving period
}
```

---

## 9. GraphRAG Flow

### Hybrid Retrieval Process

```
User Query
  │
  ├── 1. Vector Search (ChromaDB)
  │   └── Top-k semantically similar chunks
  │
  ├── 2. Entity Extraction (spaCy / Gemini)
  │   └── Extract entities from query: organizations, people, countries
  │
  ├── 3. Graph Traversal (Neo4j)
  │   └── Cypher queries for entity relationships (1-2 hops)
  │
  └── 4. Context Fusion
      ├── Merge vector chunks + graph context
      ├── Weight by source tier + trust score
      ├── Deduplicate overlapping information
      └── Assemble into agent prompt context
```

### Entity Extraction Pipeline

```python
# Step 1: Extract entities using spaCy (free, offline)
nlp = spacy.load("en_core_web_sm")
doc = nlp(query)
entities = [(ent.text, ent.label_) for ent in doc.ents]

# Step 2: Map entities to Neo4j nodes
for entity_text, entity_type in entities:
    cypher = """
    MATCH (n) 
    WHERE n.name CONTAINS $name 
    AND labels(n)[0] IN $allowed_labels
    RETURN n LIMIT 5
    """
    results = neo4j_session.run(cypher, name=entity_text, 
                                 allowed_labels=map_ner_to_neo4j(entity_type))

# Step 3: Expand with 1-2 hop relationships
for node in matched_nodes:
    cypher = """
    MATCH (n)-[r]-(m) WHERE id(n) = $node_id
    RETURN type(r) as rel, labels(m)[0] as label, m.name as name
    """
```

---

## 10. Confidence Engine Design

### Scoring Architecture

```python
class ConfidenceEngine:
    ALPHA = 0.1        # Weight per supporting/contradicting source
    BETA = 0.2         # Weight for challenge survival
    MIN_CONFIDENCE = 0.1
    MAX_CONFIDENCE = 1.0
    
    def score_claim(self, claim: Claim, challenge_survived: bool) -> float:
        """
        confidence_after = min(1.0, confidence_before 
                              + α × (support_count - contradict_count)
                              + β × (1 if survived_challenge else -1))
        """
        base = claim.confidence
        evidence_delta = self.ALPHA * (claim.support_count - claim.contradict_count)
        challenge_delta = self.BETA * (1 if challenge_survived else -1)
        
        return max(self.MIN_CONFIDENCE, 
                   min(self.MAX_CONFIDENCE, base + evidence_delta + challenge_delta))
    
    def global_confidence(self, claims: list[Claim]) -> dict:
        """Aggregate per-claim scores into global metrics."""
        claim_scores = [c.confidence for c in claims]
        trust_scores = [s.trust_score for c in claims for s in c.sources]
        
        return {
            "global_score": mean(claim_scores) * mean(trust_scores),
            "evidence_richness": len(trust_scores) / max(len(claims), 1),
            "consensus_score": 1 - stdev(claim_scores) if len(claim_scores) > 1 else 1.0,
            "challenge_survival_rate": sum(1 for c in claims if not c.challenged) / max(len(claims), 1)
        }
```

### Metrics Breakdown

| Metric | Formula | Range | Meaning |
|--------|---------|-------|---------|
| **Claim Confidence** | `base + α(support-contradict) + β(challenge_survived)` | 0.1–1.0 | How confident we are in a single claim |
| **Global Score** | `mean(claim_confidences) × mean(trust_scores)` | 0.0–1.0 | Overall answer confidence |
| **Evidence Richness** | `total_sources / total_claims` | 0.0–∞ | How well-sourced the answer is |
| **Consensus Score** | `1 - stdev(claim_confidences)` | 0.0–1.0 | Agreement among claims |
| **Challenge Survival Rate** | `unchallenged_claims / total_claims` | 0.0–1.0 | Robustness against critique |

---

## 11. Devil's Advocate Workflow

### Process Flow

```
Input: All agent responses (list of AgentResponse)
Config: max_rounds=2, timeout=60s

FOR round IN 1..max_rounds:
  FOR each claim IN all_claims:
    1. Decompose claim into assumptions
    2. Search RAG (prioritize Tier 1 sources) for counter-evidence
    3. Search Neo4j graph for contradictory relationships
    4. Generate counterargument with citations
    
    IF valid_challenge(counterargument):
      - Flag claim as challenged
      - Record challenge_text and counter_evidence
      - Mark originating agent for re-run
    
  IF any agents flagged for re-run:
    FOR each flagged_agent:
      - Re-execute agent with updated prompt:
        "You previously claimed X. Objection: Y. Revise accordingly."
      - Collect revised AgentResponse
    
  IF no challenges found:
    BREAK  // Convergence

Output: Updated claims with challenge metadata
```

### Challenge Validity Criteria

A challenge is considered **valid** if:
1. Counter-evidence comes from a Tier 1 or Tier 2 source (trust_score ≥ 0.5)
2. The contradiction is **direct** (not tangential)
3. The counter-evidence is from a **different source** than the original claim's evidence
4. The challenge introduces **new information** not already considered

---

## 12. Source Credibility Framework

### Source Tiers

| Tier | Score Range | Examples | Weight in Retrieval |
|------|-----------|----------|-------------------|
| **Tier 1** (Official) | 0.85–1.0 | Government reports, SEC filings, academic journals, UN/OECD docs | 1.5× |
| **Tier 2** (Major) | 0.60–0.84 | Reuters, BBC, Bloomberg, major think-tanks, established news | 1.0× |
| **Tier 3** (General) | 0.30–0.59 | Blogs, social media, opinion pieces, lesser-known outlets | 0.5× |

### Trust Score Calculation

```python
def calculate_trust_score(source_tier: int, 
                          age_days: int,
                          corroboration_count: int,
                          contradiction_count: int) -> float:
    """
    trust = base_trust(tier) × recency_factor × corroboration_bonus
    """
    base_trust = {1: 0.9, 2: 0.7, 3: 0.4}[source_tier]
    recency = max(0.3, 1.0 - (age_days / 365))  # Decays over 1 year, min 0.3
    corroboration = min(1.3, 1.0 + 0.05 * corroboration_count)
    contradiction_penalty = max(0.5, 1.0 - 0.1 * contradiction_count)
    
    return min(1.0, base_trust * recency * corroboration * contradiction_penalty)
```

---

## 13. Authentication Design

### Supabase Auth Flow

```
1. User signs up → POST /api/auth/signup → Supabase creates user
2. User logs in → POST /api/auth/login → Supabase returns JWT
3. Frontend stores JWT in httpOnly cookie / localStorage
4. All API requests include Authorization: Bearer <jwt>
5. FastAPI middleware validates JWT with Supabase
6. Supabase RLS enforces row-level access on queries/briefings
```

### Auth Middleware (FastAPI)

```python
from supabase import create_client

async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user
```

---

## 14. Authorization Design

### Role Model (MVP)

| Role | Permissions |
|------|------------|
| `user` | Create queries, view own queries/briefings, delete own queries |
| `admin` | All user permissions + view all queries, manage users |

For MVP, only `user` role is implemented. Admin features are deferred.

### API Authorization

```python
# All query endpoints require authenticated user
@router.post("/api/query")
async def create_query(request: QueryRequest, user = Depends(get_current_user)):
    # user.id is automatically scoped by Supabase RLS
    pass
```

---

## 15. WebSocket Design

### Connection Lifecycle

```
1. Client authenticates via REST (gets JWT)
2. Client opens WebSocket: ws://host/ws/{query_id}?token={jwt}
3. Server validates token, joins query channel
4. Server pushes events as agents execute
5. On briefing_ready, client can close connection
6. Server closes after 5 minutes of inactivity
```

### Message Protocol

```python
class WSMessage(BaseModel):
    event: str          # Event type
    data: dict          # Event payload
    timestamp: datetime # Server timestamp
    query_id: str       # Associated query

# Event types
EVENTS = {
    "agent_started": {"agent_name": str, "subtask": str},
    "agent_completed": {"agent_name": str, "claims_count": int, "time_ms": int},
    "challenge_raised": {"agent_name": str, "claim_id": str, "challenge": str},
    "agent_rerun": {"agent_name": str, "reason": str, "round": int},
    "synthesis_started": {},
    "briefing_ready": {"briefing": dict, "confidence": dict},
    "error": {"message": str, "code": str},
}
```

### Reconnection Strategy (Frontend)

```javascript
// Auto-reconnect with exponential backoff
const INITIAL_DELAY = 1000;   // 1 second
const MAX_DELAY = 30000;      // 30 seconds
const MAX_RETRIES = 5;
```

---

## 16. Logging & Monitoring

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Every agent call is logged
logger.info("agent_execution",
    agent_name="recon",
    query_id="q_abc123",
    execution_time_ms=3200,
    tokens_used=1450,
    claims_count=5,
    status="success"
)
```

### Log Storage
- **Application logs:** Structured JSON → stdout (Docker logs)
- **Query audit trail:** Supabase `agent_executions` table
- **Token usage tracking:** Supabase `agent_executions.tokens_used` column

### Monitoring (Free Tier)

| Metric | Tool | Cost |
|--------|------|------|
| Application health | FastAPI `/health` endpoint | Free |
| Error tracking | Python `logging` + structured logs | Free |
| Token usage | Custom Supabase dashboard query | Free |
| API latency | FastAPI middleware timing | Free |

---

## 17. Testing Strategy

### Test Pyramid

```
          ┌──────────┐
          │  E2E (5) │  Full query → briefing (manual + Playwright)
         ┌┴──────────┴┐
         │Integration  │  Agent + DB + RAG (15 tests)
        ┌┴─────────────┴┐
        │  Unit (50+)    │  Agent logic, scoring, schemas, utils
        └────────────────┘
```

### Unit Tests

| Module | What to Test | Framework |
|--------|-------------|-----------|
| `confidence/engine.py` | Scoring formulas, edge cases | pytest |
| `shared/schemas.py` | Pydantic validation, serialization | pytest |
| `retrieval/chunking.py` | Chunk sizes, overlap, metadata | pytest |
| `validation/trust_scoring.py` | Trust score calculation, tiers | pytest |
| `agents/base.py` | Base agent contract enforcement | pytest |

### Integration Tests

| Scenario | Components | Mock |
|----------|-----------|------|
| Agent → ChromaDB retrieval | Agent + ChromaDB | Mock LLM response |
| Agent → Neo4j query | Agent + Neo4j | Mock LLM response |
| Orchestrator → Agent dispatch | LangGraph + Agents | Mock agent responses |
| WebSocket → Event streaming | FastAPI WS + Client | Mock orchestrator |
| API → Supabase auth | FastAPI + Supabase | Test Supabase project |

### Test Commands

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Run only unit tests
pytest backend/tests/ -v -m "not integration"
```

---

## 18. Security Strategy

### Defense Layers

| Layer | Measure | Implementation |
|-------|---------|---------------|
| **Authentication** | JWT via Supabase | Supabase Auth SDK |
| **Authorization** | Row-Level Security | Supabase RLS policies |
| **Input Validation** | Pydantic schemas | All API inputs validated |
| **Prompt Injection** | Content sanitization | Strip control characters, limit input length |
| **API Keys** | Environment variables | `.env` file, never committed |
| **CORS** | Whitelist origins | FastAPI CORSMiddleware |
| **Rate Limiting** | Per-user throttling | slowapi (FastAPI middleware) |
| **Output Sanitization** | Schema validation | Pydantic output models |

### Secret Management

```bash
# .env file (never committed)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

---

## 19. Deployment Strategy

### Local Development (Docker Compose)

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - neo4j
    volumes:
      - ./backend:/app
      - chroma_data:/app/chroma_db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  chroma_data:
  neo4j_data:
```

### Deployment Environments

| Environment | Infrastructure | Purpose |
|------------|---------------|---------|
| **Local Dev** | Docker Compose | Day-to-day development |
| **Demo** | Docker Compose on local machine | Viva/presentation demo |
| **Cloud (optional)** | GCP Cloud Run (free tier) | Remote demo if needed |

---

## 20. CI/CD Strategy

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install ruff
      - run: ruff check backend/

  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v --tb=short

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci && npm run lint

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci && npm run build
```

---

## 21. Cost Optimization

### Zero-Cost Strategy

| Resource | Free Alternative | Limit |
|----------|-----------------|-------|
| LLM (Gemini) | Vertex AI GCP credits | $1,000 (expires Apr 2027) |
| Database | Supabase free tier | 500MB, 50K rows |
| Graph DB | Neo4j Community (Docker) | Unlimited (local) |
| Vector DB | ChromaDB (embedded) | Limited by disk |
| Search | DuckDuckGo (duckduckgo-search) | No hard limit |
| Financial Data | yfinance | No hard limit |
| News | GDELT + RSS | No hard limit |
| CI/CD | GitHub Actions | 2,000 min/month (public repo) |
| Hosting | Local Docker | Free |

### Token Budget Per Query

| Component | Est. Tokens | Est. Cost |
|-----------|------------|-----------|
| 3× Agent prompts (Flash) | ~6,000 | ~$0.0009 |
| 3× Agent responses (Flash) | ~3,000 | ~$0.0005 |
| DA review (Pro) | ~4,000 | ~$0.004 |
| DA challenge + re-run (Flash) | ~3,000 | ~$0.0005 |
| Synthesis (Pro) | ~5,000 | ~$0.005 |
| Embeddings | ~2,000 | ~$0.0001 |
| **Total per query** | **~23,000** | **~$0.011** |

> **$1,000 ÷ $0.011 = ~90,000 queries** — more than enough for the entire project lifecycle.

---

## 22. Scaling Strategy

### MVP Scale Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Concurrent users | 1-5 | Single FastAPI instance |
| Queries/minute | 2-3 | Sequential processing |
| Knowledge base size | ~10K chunks | ChromaDB embedded |
| Graph nodes | ~5K | Neo4j Community |
| Response time | 15-45s | Gemini Flash + parallel agents |

### Future Scaling Path (Post-MVP)

1. **FastAPI workers** — Increase Uvicorn workers for concurrent requests
2. **ChromaDB → Pinecone** — Managed vector DB for larger corpora
3. **Neo4j → AuraDB** — Managed graph DB for production scale
4. **Supabase → dedicated PostgreSQL** — For higher row limits
5. **GCP Cloud Run** — Serverless scaling of the backend
6. **Redis** — Caching layer for repeated queries

---

## 23. Future Enhancements

| Enhancement | Description | Priority |
|------------|-------------|----------|
| **Scenario Simulation Agent** | "What-if" analysis with hypothetical scenarios | P2 |
| **Graph Visualizer** | Interactive D3/Vis.js visualization of Neo4j subgraphs | P2 |
| **Confidence Dashboard** | Heatmaps, risk matrices, gauge charts | P2 |
| **Agent Swap** | Runtime LLM switching per agent | P3 |
| **Legal Compliance Agent** | Regulatory compliance checking | P3 |
| **Fine-tuned Models** | Domain-specific Gemini fine-tuning | P3 |
| **Human-in-the-Loop** | Analyst review of DA objections | P3 |
| **Multi-language** | Support for non-English queries and sources | P3 |
| **Scheduled Monitoring** | Periodic intelligence updates on topics | P3 |
| **Export Formats** | PDF/DOCX export of briefings | P2 |
