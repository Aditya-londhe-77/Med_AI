# AI_Based_Strategic_Intelligence_Assistant (AISIA)

> **Evidence-Grounded Medical Intelligence & Multi-Agent Clinical AI Orchestration Platform**  
> *Final Year B.Tech Project*  
> **Product Category:** Medical AI Research and Information Platform  
> **User-Facing Tagline:** "Evidence-Grounded Medical Intelligence"

---

## 1. Executive System Overview

**AI_Based_Strategic_Intelligence_Assistant** (**AISIA**) is an orchestrator-led multi-agent medical intelligence application engineered to produce transparent, evidence-grounded clinical summaries, pharmacological monographs, and multi-domain research dossiers.

Unlike generic LLM chatbots that output unverified, hallucinated text, AISIA deploys a coordinated swarm of 7 specialized healthcare AI operatives that independently gather peer-reviewed medical literature (PubMed, WHO, CDC, FDA, Cochrane, Mayo Clinic), evaluate disease presentation and pathophysiology, cross-examine drug mechanisms and contraindications, self-challenge conclusions through adversarial evidence peer-review, and enforce rigorous healthcare safety guardrails.

### Core Architecture Pillars

1. **Strict Medical Domain Restriction:** Gateway validation using `MedicalDomainGuard` that accepts healthcare and biomedical inquiries while categorically rejecting non-medical queries (finance, geopolitics, military, general programming, sports, entertainment).
2. **Emergency Fast-Path Screening:** Immediate life-threatening symptom detection (acute coronary syndrome, stroke, toxic ingestion, anaphylaxis) with instant urgent-care advisory cards before extensive pipeline execution.
3. **7 Specialized Healthcare AI Agents:**
   - **Medical Intake & Domain Classification Agent:** Maps queries into 16 clinical subspecialties and extracts conditions, symptoms, medications, and anatomical structures.
   - **Medical Literature Research Agent:** Searches indexed medical sources, WHO clinical guidelines, and clinical trial findings.
   - **Clinical Information Analysis Agent:** Analyzes symptom constellations, diagnostic workup pathways, staging systems (Wells, CURB-65), and disease pathophysiology.
   - **Medication Reference Agent:** Details pharmacodynamics, mechanism of action, boxed warnings, high-risk drug-drug interactions, and contraindications.
   - **Medical Evidence Validation Agent:** Adversarial clinical peer-reviewer evaluating evidence grades (GRADE framework), detecting contradictions, and exposing evidentiary gaps.
   - **Medical Report Synthesis Agent:** Synthesizes multi-agent findings into structured dossiers with key clinical takeaways, evidence evaluations, and primary source citations.
   - **Medical Safety & Domain Guard Agent:** Applies clinical safety gates, sanitizes individual dosage claims, and injects mandatory institutional disclaimers.
4. **Conditional LangGraph Orchestration:** Stateful acyclic graph supporting conditional parallel dispatch (activating pharmacology or clinical agents based on inquiry intent) and iterative peer-review revision loops.
5. **GRADE Evidence Calibration:** Quantifies evidence trustworthiness (Grade A: RCTs/Guidelines, Grade B: Observational/Cohort, Grade C: Educational Synthesis).
6. **Premium Pink & Purple Healthcare SaaS Interface:** Clean lavender and white surfaces, primary purple (`#7652D6`), deep purple (`#4B2B91`), and pink accent (`#E879B9`) styling across 8 dedicated clinical workflow pages.

---

## 2. System Architecture

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
│  │  Medical Domain Guard (Gateway Gatekeeper)                │  │
│  │  ┌────────────────────────────────────────────────────┐   │  │
│  │  │ LangGraph Medical Multi-Agent State Machine        │   │  │
│  │  │                                                    │   │  │
│  │  │  [Medical Intake & Domain Classification Agent]    │   │  │
│  │  │                         │                          │   │  │
│  │  │              (Conditional Dispatch)                │   │  │
│  │  │          ┌──────────────┼──────────────┐           │   │  │
│  │  │          ▼              ▼              ▼           │   │  │
│  │  │     [Literature]   [Clinical]    [Medication]      │   │  │
│  │  │          └──────────────┬──────────────┘           │   │  │
│  │  │                         ▼                          │   │  │
│  │  │         [Medical Evidence Validation Agent]        │   │  │
│  │  │                         │                          │   │  │
│  │  │            (Optional Revision Loop)                │   │  │
│  │  │                         ▼                          │   │  │
│  │  │         [Medical Report Synthesis Agent]           │   │  │
│  │  │                         │                          │   │  │
│  │  │         [Medical Safety & Domain Guard Agent]      │   │  │
│  │  └────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ ChromaDB │  │  Neo4j   │  │ Supabase  │  │ DuckDuckGo   │  │
│  │(Medical  │  │(Medical  │  │(Session   │  │ Medical News │  │
│  │ Corpus)  │  │ KG)      │  │ History)  │  │ Search)      │  │
│  └──────────┘  └──────────┘  └───────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Dedicated Healthcare Frontend (8 Required Pages)

| Page | Route | Description |
|---|---|---|
| **Medical AI Dashboard** | `/` | Central hub with hero clinical mission, quick medical query composer, agent status matrix, and knowledge source catalog. |
| **Medical AI Workspace** | `/workspace` | Dedicated clinical workspace for subspecialty filtering, multi-agent selection, and validation threshold calibration. |
| **Live Agent Orchestration** | `/query/:id` | Live LangGraph execution timeline, multi-agent telemetry stream, real-time finding cards, and progress metrics. |
| **Medical Report Viewer** | `/results/:id` | Structured clinical report viewer with executive summaries, takeaways, dossier sections, evidence library, and export tools. |
| **Medical Agent Center** | `/agents` | Overview of the 7 clinical AI operatives, Gemini model assignments, tools, and research protocol settings. |
| **Medical Knowledge Explorer** | `/graph` | Interactive Neo4j biomedical graph canvas displaying Condition-Drug-Anatomy-Biomarker relationships. |
| **Research History** | `/history` | Audit trail of past inquiries, domains, timestamps, and one-click links to past dossiers. |
| **System Settings** | `/settings` | System parameters, adversarial validation rounds, evidence grade filters, and database telemetry. |

---

## 4. Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- **Docker** (optional, for Neo4j)

### Step 1: Clone and Set Up Backend
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv .venv
.\.venv\Scripts\activate  # On Windows PowerShell

# Install requirements
pip install -r requirements.txt

# Run medical test suite
python -m pytest tests/test_medical.py -v
```

### Step 2: Set Up Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build frontend to verify TypeScript types and bundles
npm run build

# Start frontend development server
npm run dev
```

### Step 3: Run Full System
You can launch all services using the provided startup script:
```powershell
# Windows PowerShell
.\start.ps1

# Or Windows Command Prompt
.\start.bat
```

- **Frontend Application:** http://localhost:5173
- **FastAPI Backend Documentation:** http://localhost:8000/docs
- **Health Check Endpoint:** http://localhost:8000/health

---

## 5. Automated Verification & Testing

AISIA includes a dedicated test suite verifying domain safety, schema constraints, emergency screening, agent execution, and full LangGraph workflow execution:

```bash
python -m pytest backend/tests/test_medical.py -v
```

### Verified Test Coverage (32/32 Passed)
- **Domain Guard:** Validates acceptance of cardiology, endocrinology, pharmacology, anatomy, and symptom queries; verifies rejection of finance, military, sports, programming, and empty queries.
- **Emergency Screening:** Detects acute chest pain, stroke, and overdose patterns, returning urgent guidance immediately.
- **Safety Agent:** Sanitizes definitive diagnostic phrasing, injects mandatory disclaimers, and adds safety sections.
- **Schema Validation:** Verifies Oxford CEBM / GRADE evidence scoring and confidence bounds.
- **Workflow Execution:** Executes end-to-end multi-agent LangGraph workflow returning structured medical reports.
- **Specialized Agents:** Verifies Clinical, Medication, and Evidence Validation agents.
- **Frontend Build:** `npm run build` compiles 100% cleanly with zero TypeScript errors.

---

## 6. Medical Safety & Ethical Guidelines

> [!IMPORTANT]
> **Institutional Educational Disclaimer**  
> AISIA is an artificial intelligence platform designed for medical education, healthcare research reference, and student informatics. It does NOT provide individual medical diagnoses, prescription dosages, or treatment plans. Users experiencing acute symptoms should immediately contact emergency medical services (911/112/108).
