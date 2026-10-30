# AEGIS — Git Workflow & Repository Design

> **Repository:** [https://github.com/ShlokNoval/AEGIS.git](https://github.com/ShlokNoval/AEGIS.git)
> **Created:** 2026-06-26
> **Status:** Active

---

## 1. Branch Strategy

### Branch Purposes

| Branch | Purpose | Protected | Owner |
|--------|---------|-----------|-------|
| `main` | Production-ready code. Only merged via approved PRs. | ✅ Yes | Both |
| `Shlok` | Shlok's development branch — AI agents, RAG, GraphRAG, orchestrator | ❌ No | Shlok |
| `Aditya` | Aditya's development branch — Frontend, APIs, Auth, Deployment | ❌ No | Aditya |

### Branch Flow

```
main (stable, production-ready)
  ├── Shlok (AI/backend development)
  │     ├── feature/recon-agent
  │     ├── feature/financial-agent
  │     ├── feature/devil-advocate
  │     └── ...
  └── Aditya (frontend/platform development)
        ├── feature/dashboard-ui
        ├── feature/auth-setup
        ├── feature/websocket-stream
        └── ...
```

**Feature branches** are optional but recommended for larger features. They branch from the developer's branch and merge back into it.

---

## 2. Merge Strategy

### Rules

1. **Developer branches → `main`:** Only via Pull Request (PR)
2. **Feature branches → developer branch:** Direct merge or PR (developer's choice)
3. **`main` → developer branches:** Regular rebases to stay up-to-date (at least weekly)
4. **Merge type:** **Squash merge** for PRs into `main` (clean history)
5. **Rebase:** Developers should `git rebase main` on their branches before creating a PR

### Merge Flow

```
Shlok branch ──PR──▶ main ◀──PR── Aditya branch
                       │
                       ├── Shlok rebases from main
                       └── Aditya rebases from main
```

---

## 3. Pull Request Process

### Creating a PR

1. Ensure your branch is rebased on latest `main`
2. Run all tests locally: `pytest` and `npm run lint`
3. Create PR with the following template:

```markdown
## What Changed
Brief description of changes.

## Why
Rationale and context.

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Refactor
- [ ] Documentation
- [ ] Config/DevOps

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing done

## Files Changed
List key files.

## Screenshots (if UI changes)
Attach screenshots.
```

### PR Approval Rules

| Scenario | Reviewer Required | Auto-merge |
|----------|------------------|------------|
| Shlok's AI code → main | Aditya reviews | ❌ No |
| Aditya's platform code → main | Shlok reviews | ❌ No |
| Documentation only | Either can approve | ✅ Yes |
| Hotfix (critical bug) | Self-approve with comment | ✅ Yes |
| Shared code (schemas, configs) | Both must approve | ❌ No |

---

## 4. Code Review Requirements

### What to Review

| Area | Check |
|------|-------|
| **Correctness** | Does the code do what it claims? |
| **Schema compliance** | Does it use shared Pydantic models? |
| **Error handling** | Are edge cases handled? |
| **Security** | No hardcoded secrets, proper input validation? |
| **Performance** | No obvious inefficiencies? |
| **Documentation** | Are docstrings/comments adequate? |
| **Tests** | Are there tests for new functionality? |

### Review SLA
- Reviews should be completed within **24 hours** on weekdays
- Critical/blocking PRs: same-day review

---

## 5. Conflict Resolution Process

### Prevention
1. **Shared code is in `shared/`** — both members edit this carefully
2. **Lock files** (e.g., `requirements.txt`, `package-lock.json`) — always rebase before editing
3. **Communicate** before touching shared schemas or configs

### Resolution Steps

1. **Automated merge succeeds:** ✅ Proceed
2. **Conflict in personal code** (agents, frontend): The PR author resolves
3. **Conflict in shared code** (`shared/`, `schemas/`, `config/`):
   - Both developers review the conflict together
   - Use the version that matches the latest schema
   - Document the resolution in the PR
4. **Irreconcilable conflict:** Schedule a sync call, resolve live, document in PR

---

## 6. Commit Naming Conventions

### Format

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(recon): add DuckDuckGo search tool` |
| `fix` | Bug fix | `fix(api): handle empty query gracefully` |
| `refactor` | Code restructure | `refactor(agents): extract base agent class` |
| `docs` | Documentation | `docs: update ARCHITECTURE_REVIEW.md` |
| `test` | Add/update tests | `test(confidence): add unit tests for scoring` |
| `chore` | Config/build changes | `chore: update Docker Compose services` |
| `style` | Formatting only | `style(frontend): fix linting warnings` |
| `perf` | Performance | `perf(rag): cache ChromaDB query results` |
| `ci` | CI/CD changes | `ci: add GitHub Actions lint workflow` |

### Scopes

| Scope | Owner | Description |
|-------|-------|-------------|
| `orchestrator` | Shlok | LangGraph orchestrator |
| `recon` | Shlok | Recon Agent |
| `financial` | Shlok | Financial Agent |
| `geopolitical` | Shlok | Geopolitical Agent |
| `synthesis` | Shlok | Synthesis Agent |
| `devil` | Shlok | Devil's Advocate Agent |
| `confidence` | Shlok | Confidence Engine |
| `rag` | Shlok | RAG/ChromaDB retrieval |
| `graphrag` | Shlok | Neo4j GraphRAG |
| `api` | Aditya | FastAPI routes |
| `frontend` | Aditya | React frontend |
| `auth` | Aditya | Supabase Auth |
| `db` | Aditya | Supabase PostgreSQL |
| `ws` | Aditya | WebSocket streaming |
| `deploy` | Aditya | Docker/deployment |
| `shared` | Both | Shared schemas/config |

### Examples

```
feat(recon): implement web search via DuckDuckGo
fix(devil): prevent infinite loop with max_rounds=2
refactor(shared): add AgentResponse Pydantic model
docs: add Git workflow documentation
test(confidence): add scoring formula unit tests
chore(deploy): add Neo4j to Docker Compose
perf(rag): switch to batch embedding for ingestion
ci: add pytest to GitHub Actions workflow
```

---

## 7. Repository Structure

```
AEGIS/
├── docs/                          # All project documentation
│   ├── ARCHITECTURE_REVIEW.md
│   ├── GIT_WORKFLOW.md            # This file
│   ├── IMPLEMENTATION_PLAN.md
│   ├── TEAM_OWNERSHIP.md
│   ├── ROADMAP.md
│   ├── PROJECT_DECISIONS.md
│   └── PROCESS_LOG.md
│
├── backend/                       # FastAPI monolithic backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── config.py              # Settings & environment
│   │   ├── agents/                # All AI agents (Shlok)
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base agent class
│   │   │   ├── recon.py
│   │   │   ├── financial.py
│   │   │   ├── geopolitical.py
│   │   │   ├── synthesis.py
│   │   │   └── devil_advocate.py
│   │   ├── orchestrator/          # LangGraph orchestrator (Shlok)
│   │   │   ├── __init__.py
│   │   │   ├── graph.py           # LangGraph state graph
│   │   │   └── state.py           # State definitions
│   │   ├── retrieval/             # RAG pipeline (Shlok)
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py      # Vertex AI embeddings
│   │   │   ├── chunking.py        # Document chunking
│   │   │   ├── vector_store.py    # ChromaDB interface
│   │   │   └── ingestion.py       # Document ingestion pipeline
│   │   ├── graph_rag/             # GraphRAG pipeline (Shlok)
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_client.py    # Neo4j connection & queries
│   │   │   ├── entity_extraction.py
│   │   │   └── schema.py          # Graph schema definitions
│   │   ├── confidence/            # Confidence Engine (Shlok)
│   │   │   ├── __init__.py
│   │   │   ├── engine.py          # Scoring logic
│   │   │   └── models.py          # Confidence data models
│   │   ├── validation/            # Source trust & validation (Shlok)
│   │   │   ├── __init__.py
│   │   │   ├── trust_scoring.py
│   │   │   └── source_tiers.py
│   │   ├── api/                   # FastAPI routes (Aditya)
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── query.py       # Main query endpoint
│   │   │   │   ├── auth.py        # Auth routes (Supabase)
│   │   │   │   ├── history.py     # Query history
│   │   │   │   └── health.py      # Health check
│   │   │   └── websocket.py       # WebSocket handler (Aditya)
│   │   ├── database/              # Supabase integration (Aditya)
│   │   │   ├── __init__.py
│   │   │   ├── supabase_client.py
│   │   │   └── models.py          # SQLAlchemy/Supabase models
│   │   └── shared/                # Shared schemas (Both)
│   │       ├── __init__.py
│   │       ├── schemas.py         # Pydantic I/O contracts
│   │       └── constants.py       # Shared constants
│   ├── tests/                     # Backend tests
│   │   ├── test_agents/
│   │   ├── test_retrieval/
│   │   ├── test_api/
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/                      # React + Vite frontend (Aditya)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/              # API & WebSocket clients
│   │   ├── store/                 # State management
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── data/                          # Demo corpus & seed data
│   ├── documents/                 # Sample PDFs, policy docs
│   ├── seed/                      # Neo4j seed data
│   └── README.md
│
├── docker-compose.yml             # All services orchestration
├── .env.example                   # Environment template
├── .gitignore
├── README.md
└── LICENSE
```

---

## 8. .gitignore (Essential)

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Node
node_modules/
dist/
.vite/

# Environment
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp

# Docker
docker-compose.override.yml

# Data (large files)
data/chroma_db/
data/neo4j/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# GCP
service-account-key.json
```
