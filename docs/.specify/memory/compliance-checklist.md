# EasyGrant Constitution Compliance Checklist

**Version**: 1.0.0  
**Last Updated**: 2025-10-26

Use this checklist during spec/plan/task reviews to verify constitutional compliance.

## Core Principles Verification

### ✅ I. Local Context First

- [ ] Feature retrieves context from `/data/uploads` directory
- [ ] No hardcoded templates or generic assumptions in prompts
- [ ] Retrieval queries target user-uploaded documents only
- [ ] Gap analysis identifies missing local context explicitly

**Files to Check**: `core/retriever.py`, `core/gap_analyzer.py`, agent prompts

---

### ✅ II. Requirements-Driven Generation

- [ ] Requirements extraction agent parses funding call into JSON blueprint
- [ ] Blueprint includes: sections, word limits, format constraints, scoring criteria
- [ ] Section generator enforces limits from blueprint
- [ ] Quality checker validates against blueprint requirements

**Files to Check**: `core/requirements_extractor.py`, `core/section_generator.py`,
`core/quality_checker.py`

---

### ✅ III. Transparency & Provenance

- [ ] Every generated claim includes inline citation
- [ ] Citations reference document title + page number
- [ ] Sources panel displays all referenced documents
- [ ] No unsupported claims (hallucination detection active)
- [ ] Retrieval confidence threshold ≥ 0.7 (per `config.yaml`)

**Files to Check**: `core/section_generator.py`, `frontend/src/components/SourcesPanel.jsx`,
`config.yaml` (citations section)

---

### ✅ IV. Editability & User Control

- [ ] User edits stored separately from AI-generated content
- [ ] Regeneration merges edits with new generation (sticky edits)
- [ ] Section locking mechanism implemented (optional for MVP)
- [ ] Feedback input field applies changes explicitly
- [ ] `config.yaml` has `preserve_edits: true`

**Files to Check**: `core/section_generator.py`, `api/endpoints/sections.py`,
`frontend/src/components/SectionEditor.jsx`

---

### ✅ V. Simplicity & User Experience

- [ ] Single-screen workflow: no multi-page navigation
- [ ] Section-by-section flow (one section visible at a time)
- [ ] Sensible defaults in `config.yaml` (no required user config)
- [ ] Minimal clicks: upload → generate → edit → export ≤ 5 actions
- [ ] `config.yaml` has `show_advanced_options: false`

**Files to Check**: `frontend/src/App.jsx`, `frontend/src/components/Workflow.jsx`,
`config.yaml` (ui section)

---

### ✅ VI. Neutral Language

- [ ] Agent prompts specify "neutral, professional, grant-appropriate language"
- [ ] No subjective/promotional tone in generation prompts
- [ ] Quality checker flags non-neutral language

**Files to Check**: `prompts/section_generation.txt`, `prompts/quality_check.txt`

---

### ✅ VII. Privacy & Security

- [ ] All processing server-side (FastAPI backend)
- [ ] No client-side API keys in frontend
- [ ] Storage: local disk only (`/data/uploads`, `/vector`)
- [ ] Delete-all endpoint implemented (`DELETE /api/data`)
- [ ] `config.yaml` has `server_side_processing: true`, `client_api_keys: false`

**Files to Check**: `api/endpoints/data.py`, `api/main.py`, `config.yaml` (privacy section)

---

### ✅ VIII. Maintainability & Configuration

- [ ] All parameters in `config.yaml` (models, chunking, top-k, temperatures)
- [ ] Adapter pattern used for funding call types (if multiple supported)
- [ ] Dependencies minimal: FastAPI, Chroma, OpenAI, PyMuPDF, python-docx
- [ ] No custom ML models or heavy frameworks

**Files to Check**: `config.yaml`, `requirements.txt`, `core/adapters/`

---

### ✅ IX. Hostability & Demo-Readiness

- [ ] FastAPI backend runs with `uvicorn` (single command)
- [ ] React frontend builds with `vite build` (static bundle)
- [ ] No database setup required (Chroma uses local disk)
- [ ] Environment variables documented in `.env.example`
- [ ] Free-tier compatible: ≤512MB memory, small models
- [ ] Public URL deployment guide in `docs/deployment.md`

**Files to Check**: `api/main.py`, `frontend/vite.config.js`, `.env.example`,
`docs/deployment.md`

---

## Technical Architecture Verification

- [ ] Frontend: React + Vite (confirmed in `package.json`)
- [ ] Backend: FastAPI (confirmed in `requirements.txt`)
- [ ] Vector store: Chroma server-side (confirmed in `core/vector_store.py`)
- [ ] Embeddings: text-embedding-3-small (confirmed in `config.yaml`)
- [ ] LLMs: GPT-4o + GPT-4o-mini (confirmed in `config.yaml`)
- [ ] Parsing: PyMuPDF + python-docx (confirmed in `requirements.txt`)

---

## Development Workflow Verification

- [ ] Feature has spec in `/specs/[###-feature]/spec.md`
- [ ] Feature has plan in `/specs/[###-feature]/plan.md`
- [ ] Feature has tasks in `/specs/[###-feature]/tasks.md`
- [ ] Constitution check passed in plan.md (this checklist)
- [ ] Commits reference spec/task IDs
- [ ] End-to-end demo flow tested

---

## Governance Verification

- [ ] Deviation from principles documented with justification
- [ ] Complexity increase justified against Principles V & VIII
- [ ] New dependencies justified (minimal, well-maintained)
- [ ] Amendment (if any) follows: rationale → impact analysis → version increment

---

## Demo Scope Gate

**Critical for MVP**:
- [ ] Upload ≤5 docs + 1 funding call PDF
- [ ] Extract requirements → display checklist
- [ ] Generate two sections with inline citations
- [ ] Accept user edit → regenerate preserving edit
- [ ] Export DOCX with merged sections

**Out of Scope** (must NOT be implemented):
- [ ] Performance tuning beyond basic functionality
- [ ] Advanced logging frameworks (simple `logging` module OK)
- [ ] Accessibility (a11y) features
- [ ] Internationalization (i18n)

---

## Review Signature

**Reviewer**: ___________________________  
**Date**: ___________________________  
**Spec/Plan ID**: ___________________________  
**Compliance Status**: ⬜ Pass  ⬜ Pass with Justifications  ⬜ Fail

**Notes**:
