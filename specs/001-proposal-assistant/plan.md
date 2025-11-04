# Implementation Plan: Smart Proposal Assistant (Hosted Demo)

**Branch**: `001-proposal-assistant` | **Date**: 2025-10-26 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/001-proposal-assistant/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a hosted web application where judges can test the complete grant writing workflow via a public URL. Users upload a funding call PDF (auto-extracted into a structured requirements checklist) plus up to 5 supporting community documents (indexed via RAG). They select checklist sections to generate cited drafts grounded in local context, make edits that persist across regenerations, and export a submission-ready DOCX file. Entire system deploys as a single containerized FastAPI + React service to Render/Railway/Hugging Face Spaces with no user setup required.

**Technical Approach**: React + Vite frontend (three-panel UI: checklist | editor | sources), FastAPI backend (6-agent pipeline: requirements extraction, retrieval, gap analysis, section generation, quality check, DOCX assembly), Chroma vector store (server-side, 600-token chunks with 15% overlap), OpenAI APIs (text-embedding-3-small for embeddings, GPT-4o for requirements/QC, GPT-4o-mini for drafting), PyMuPDF + python-docx for parsing/export. Single Dockerfile with multi-stage build; backend on :8000, frontend on :5173 (or static bundle served by FastAPI in production).

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript ES2022+ (frontend with TypeScript optional)  
**Primary Dependencies**: FastAPI 0.104+, React 18+, Vite 5+, Chroma 0.4+, OpenAI Python SDK 1.3+, PyMuPDF (fitz) 1.23+, python-docx 1.1+  
**Storage**: Local disk (Docker volume mounts: `/data/uploads` for PDFs/DOCX, `/vector` for Chroma persistence)  
**Testing**: pytest (backend contract/integration), Vitest (frontend unit tests - optional for MVP)  
**Target Platform**: Linux container (Docker) deployed to Render/Railway/Hugging Face Spaces web service  
**Project Type**: Web application (backend/ + frontend/)  
**Performance Goals**: Upload/index 5 docs (~100 pages) <60sec; section generation (500 words) <30sec; support 10+ concurrent demo users on free tier  
**Constraints**: <512MB memory (free-tier limit), <1GB ephemeral storage (uploads cleared on container restart unless volume mounted), server-side processing only (no client API keys), single-session usage (no persistent auth/accounts)  
**Scale/Scope**: Demo/prototype for 6-hour hackathon; ~2 sections generated end-to-end; export functional; judges can repeat full workflow via public link

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Local Context First
- ✅ **PASS**: Documents uploaded to `/data/uploads`, indexed into Chroma vector store (FR-002, FR-004)
- ✅ **PASS**: Retrieval agent queries local vector store only, no external templates (FR-005)
- ✅ **PASS**: Gap analysis identifies missing local context explicitly (agent pipeline design)

### Principle II: Requirements-Driven Generation
- ✅ **PASS**: Requirements extraction agent parses funding call into JSON blueprint (FR-001)
- ✅ **PASS**: Blueprint includes sections, word limits, format constraints, scoring criteria (spec requirements)
- ✅ **PASS**: Section generator enforces word limits with auto-retry (FR-007)
- ✅ **PASS**: Quality checker validates against blueprint (agent pipeline design)

### Principle III: Transparency & Provenance
- ✅ **PASS**: Inline citations in format [Document Title, p.N] for every claim (FR-006)
- ✅ **PASS**: Sources panel displays referenced documents with relevance scores (FR-008)
- ✅ **PASS**: Retrieval confidence threshold ≥0.7 per config.yaml (citation section)

### Principle IV: Editability & User Control
- ✅ **PASS**: User edits stored separately, merged during regeneration (FR-009)
- ✅ **PASS**: "Regenerate (keep edits)" preserves manual changes (spec US3)
- ✅ **PASS**: Section locking mechanism prevents further AI mods (FR-010)

### Principle V: Simplicity & User Experience
- ✅ **PASS**: Three-panel single-screen UI (FR-013)
- ✅ **PASS**: Sensible defaults in config.yaml (models, chunking, top-k) (config file exists)
- ✅ **PASS**: Minimal workflow: upload → checklist → generate → edit → export ≤5 actions (spec SC-001)

### Principle VI: Neutral Language
- ✅ **PASS**: Generation prompts specify "neutral, professional, grant-appropriate language" (FR-016)
- ✅ **PASS**: Quality checker flags non-neutral tone (agent design requirement)

### Principle VII: Privacy & Security
- ✅ **PASS**: All processing server-side (FastAPI backend), no client API keys (FR-003)
- ✅ **PASS**: Storage on local disk only `/data/uploads`, `/vector` (Technical Context: Storage)
- ✅ **PASS**: One-click delete endpoint removes all data (FR-012)

### Principle VIII: Maintainability & Configuration
- ✅ **PASS**: All parameters in config.yaml (models, chunking, top-k, temperatures) (root config.yaml exists)
- ✅ **PASS**: Minimal dependencies: FastAPI, Chroma, OpenAI, PyMuPDF, python-docx (Technical Context)
- ✅ **PASS**: No custom ML models or heavy frameworks (using OpenAI APIs)

### Principle IX: Hostability & Demo-Readiness
- ✅ **PASS**: Single Dockerfile with multi-stage build (Technical Approach in Summary)
- ✅ **PASS**: FastAPI backend :8000 + Vite frontend :5173 (or static bundle) (Technical Approach)
- ✅ **PASS**: Free-tier compatible: <512MB memory, <1GB storage (Technical Context: Constraints)
- ✅ **PASS**: No setup required: public URL, no credentials, no local install (FR-015)

**GATE STATUS**: ✅ **ALL PRINCIPLES SATISFIED** - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/001-proposal-assistant/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi.yaml     # FastAPI endpoint contracts
│   └── README.md        # Contract documentation
├── checklists/
│   └── requirements.md  # Spec quality validation (already created)
├── spec.md              # Feature specification (already created)
└── SUMMARY.md           # Spec summary (already created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/                 # 6-agent pipeline
│   │   ├── requirements_extractor.py
│   │   ├── retriever.py
│   │   ├── gap_analyzer.py
│   │   ├── section_generator.py
│   │   ├── quality_checker.py
│   │   └── assembler.py
│   ├── api/                    # FastAPI endpoints
│   │   ├── routes/
│   │   │   ├── upload.py       # POST /api/upload
│   │   │   ├── requirements.py # GET /api/requirements
│   │   │   ├── sections.py     # POST /api/sections/generate
│   │   │   ├── export.py       # POST /api/export
│   │   │   └── data.py         # DELETE /api/data
│   │   └── main.py             # FastAPI app initialization
│   ├── core/                   # Core services
│   │   ├── vector_store.py     # Chroma wrapper
│   │   ├── parser.py           # PyMuPDF + python-docx
│   │   ├── embeddings.py       # OpenAI embedding client
│   │   └── llm.py              # OpenAI chat client
│   ├── models/                 # Pydantic models
│   │   ├── funding_call.py
│   │   ├── document.py
│   │   ├── section.py
│   │   └── citation.py
│   └── utils/
│       ├── config.py           # Load config.yaml
│       └── prompts.py          # Load prompt templates
├── tests/
│   ├── contract/               # API contract tests
│   └── integration/            # End-to-end workflow tests
├── prompts/                    # Agent prompt templates
│   ├── requirements_extraction.txt
│   ├── gap_analysis.txt
│   ├── section_generation.txt
│   └── quality_check.txt
└── requirements.txt            # Python dependencies

frontend/
├── src/
│   ├── components/
│   │   ├── UploadPanel.jsx     # File upload UI
│   │   ├── ChecklistPanel.jsx  # Left panel: requirements list
│   │   ├── EditorPanel.jsx     # Center panel: section editor
│   │   ├── SourcesPanel.jsx    # Right panel: citations/docs
│   │   └── ExportButton.jsx    # DOCX download trigger
│   ├── services/
│   │   └── api.js              # Fetch wrapper for backend
│   ├── App.jsx                 # Main three-panel layout
│   └── main.jsx                # Vite entry point
├── public/
└── package.json                # Node dependencies

data/
├── uploads/                    # Uploaded PDFs/DOCX (volume mount)
└── temp/                       # Temporary processing files

vector/                         # Chroma persistence (volume mount)

config.yaml                     # Centralized configuration (already created)
Dockerfile                      # Multi-stage build (backend + frontend)
docker-compose.yml              # Local dev orchestration (optional)
.env.example                    # Environment variables template
README.md                       # Project overview (already updated)
```

**Structure Decision**: Web application structure selected (backend/ + frontend/) per constitution Technical Architecture and user requirement for "simple UI (left: checklist / center: editor / right: sources)". Single Dockerfile deploys both services: FastAPI backend on :8000 serves API + static frontend bundle for production; Vite dev server on :5173 for local development. Docker volumes mount `/data/uploads` and `/vector` for persistence across container restarts on hosted platforms.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles satisfied.
