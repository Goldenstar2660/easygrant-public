# Implementation Plan Summary: Smart Proposal Assistant

**Branch**: `001-proposal-assistant`  
**Date**: 2025-10-26  
**Status**: ✅ Planning Complete - Ready for Task Breakdown

---

## Planning Phases Completed

### ✅ Phase 0: Research & Technical Decisions
**File**: `research.md`

**Key Decisions**:
1. **Docker Deployment**: Multi-stage Dockerfile (frontend build → backend + static serving)
2. **Chunking Strategy**: RecursiveCharacterTextSplitter with tiktoken (600 tokens, 15% overlap)
3. **Chroma Configuration**: PersistentClient with session-based collections
4. **Requirements Extraction**: Hybrid regex + GPT-4o for robust parsing
5. **Sticky Edits**: Diff-based merge with user edit priority
6. **Word Limit Enforcement**: Three-tier (prompt + validation + auto-retry)
7. **Citations**: Metadata-driven insertion with `[Doc Title, p.N]` format

**Technology Stack Finalized**:
- Backend: FastAPI 0.104+, Python 3.11+
- Frontend: React 18+, Vite 5+
- Vector Store: Chroma 0.4+
- LLMs: GPT-4o (requirements/QC), GPT-4o-mini (drafting)
- Embeddings: text-embedding-3-small
- Parsing: PyMuPDF 1.23+, python-docx 1.1+
- Text Processing: LangChain, tiktoken

### ✅ Phase 1: Design & Contracts
**Files**: `data-model.md`, `contracts/openapi.yaml`, `contracts/README.md`, `quickstart.md`

**Entities Defined** (6 total):
1. **FundingCall**: Uploaded PDF with extracted requirements blueprint
2. **SupportingDocument**: Local context files (community plans, budgets)
3. **SectionRequirement**: Individual required section from blueprint
4. **GeneratedSection**: AI-drafted text with citations and edit tracking
5. **UserSession**: Temporary workspace for demo session
6. **DocumentChunk**: 600-token chunks in Chroma vector store

**API Contracts** (10 endpoints):
- POST `/api/upload/funding-call` - Upload & extract requirements
- POST `/api/upload/supporting-docs` - Upload 1-5 context docs
- GET `/api/requirements/{session_id}` - Get checklist
- POST `/api/sections/generate` - Generate section with citations
- GET `/api/sections/{section_id}` - Get section details
- PATCH `/api/sections/{section_id}` - Apply user edits
- POST `/api/sections/{section_id}/regenerate` - Regenerate (keep edits)
- POST `/api/sections/{section_id}/lock` - Lock section
- POST `/api/export/docx` - Export proposal
- DELETE `/api/data/{session_id}` - One-click data deletion

**Quickstart Guide**: Step-by-step setup for local dev, Docker, and deployment to Render/Railway/Hugging Face Spaces

---

## Constitution Compliance

**All 9 Principles Verified** ✅:

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Local Context First | ✅ PASS | Upload to `/data/uploads`, Chroma indexing, RAG retrieval |
| II. Requirements-Driven | ✅ PASS | Blueprint extraction (FR-001), word limit enforcement (FR-007) |
| III. Transparency | ✅ PASS | Inline citations (FR-006), sources panel (FR-008) |
| IV. Editability | ✅ PASS | Sticky edits (FR-009), section locking (FR-010) |
| V. Simplicity | ✅ PASS | Three-panel UI (FR-013), sensible defaults (config.yaml) |
| VI. Neutral Language | ✅ PASS | Prompts specify grant-appropriate tone (FR-016) |
| VII. Privacy | ✅ PASS | Server-side only (FR-003), one-click delete (FR-012) |
| VIII. Maintainability | ✅ PASS | Config.yaml params, minimal dependencies |
| IX. Hostability | ✅ PASS | Single Dockerfile, free-tier compatible (<512MB) |

**No Violations**: No complexity tracking required.

---

## Project Structure

### Documentation
```
specs/001-proposal-assistant/
├── plan.md              ✅ Implementation plan (this summary's source)
├── research.md          ✅ Technical decisions & rationale
├── data-model.md        ✅ 6 entities with relationships
├── quickstart.md        ✅ Setup & deployment guide
├── contracts/
│   ├── openapi.yaml     ✅ Full OpenAPI 3.0 spec (10 endpoints)
│   └── README.md        ✅ Contract documentation
├── checklists/
│   └── requirements.md  ✅ Spec quality validation (16/16 passed)
├── spec.md              ✅ Feature specification (5 user stories)
└── SUMMARY.md           ✅ Spec executive summary
```

### Source Code (To Be Implemented)
```
backend/
├── src/
│   ├── agents/          # 6-agent pipeline
│   ├── api/routes/      # FastAPI endpoints (10 routes)
│   ├── core/            # Vector store, parser, LLM clients
│   ├── models/          # Pydantic schemas
│   └── utils/           # Config loader, prompts
├── tests/               # Contract & integration tests
├── prompts/             # Agent prompt templates
└── requirements.txt     # Python dependencies

frontend/
├── src/
│   ├── components/      # 5 main components (Upload, Checklist, Editor, Sources, Export)
│   ├── services/        # API client
│   └── App.jsx          # Three-panel layout
└── package.json         # Node dependencies

data/uploads/            # Uploaded PDFs/DOCX (volume mount)
vector/                  # Chroma persistence (volume mount)
config.yaml              ✅ Already created (root)
Dockerfile               # To be created (multi-stage build)
```

---

## Performance Targets (Success Criteria)

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Demo completable in | <5 min | End-to-end workflow test |
| Requirements extraction accuracy | 80%+ | Manual review of 10 sample RFPs |
| Sections within word limits (first attempt) | 90%+ | Generate 20 sections, measure compliance |
| Citation coverage | 100% | QC agent flags uncited claims |
| Edit persistence | 100% | Regenerate after edits, verify unchanged |
| DOCX opens in Word 2016+ | 100% | Test on Windows/Mac |
| Upload/index 5 docs (~100 pages) | <60 sec | Timed test on free-tier hosting |
| Section generation (500 words) | <30 sec | Timed test with top-5 retrieval |
| Data deletion | <5 sec | Timed test with confirmation check |
| Free-tier compatible | <512MB RAM, 10+ users | Load test with concurrent sessions |

---

## Risk Mitigation

| Risk | Mitigation Strategy | Owner |
|------|---------------------|-------|
| OpenAI API rate limits | Retry with exponential backoff; use GPT-4o-mini for drafting | Backend dev |
| Free-tier memory limits | Limit upload to 50MB; batch chunk processing | Backend dev |
| PDF parsing failures (scanned images) | Show clear error message; suggest text-based PDFs | Backend dev |
| Word limit exceeded despite retries | Allow manual editing; QC agent flags violation | Backend dev |
| Sticky edits merge conflicts | Always prefer user edits; provide "Reset to AI" option | Backend dev |
| Deployment platform downtime | Test on multiple platforms; provide fallback URL | DevOps |

---

## Next Steps

### 1. Run Task Breakdown
```bash
# Generate task list from this plan
/speckit.tasks
```

Expected output: `tasks.md` with phased implementation:
- **Phase 1: Setup** - Project init, dependencies, folder structure
- **Phase 2: Foundation** - Upload endpoints, parsing, vector store
- **Phase 3: User Story 1** - Upload & requirements extraction (P1)
- **Phase 4: User Story 2** - Cited section generation (P1)
- **Phase 5: User Story 3** - Sticky edits & regeneration (P2)
- **Phase 6: User Story 4** - DOCX export (P2)
- **Phase 7: User Story 5** - One-click data deletion (P3)

### 2. Begin Implementation

Follow task order:
1. Create project structure (backend/, frontend/, Dockerfile)
2. Install dependencies (requirements.txt, package.json)
3. Implement foundational services (vector store, parser, LLM clients)
4. Build API endpoints per contract (openapi.yaml)
5. Develop frontend components (three-panel UI)
6. Integrate agents (6-agent pipeline)
7. Test end-to-end workflow
8. Deploy to Render/Railway/HF Spaces

### 3. Validation at Each Phase

- **After Phase 2**: Verify upload + parsing works
- **After Phase 4**: Test section generation with citations
- **After Phase 5**: Confirm sticky edits preserved
- **After Phase 7**: Run full demo workflow for judges

---

## Files Created This Session

| File | Purpose | Status |
|------|---------|--------|
| `plan.md` | Implementation plan template (filled) | ✅ Complete |
| `research.md` | Technical decisions & rationale (7 decisions) | ✅ Complete |
| `data-model.md` | Entity definitions (6 entities + relationships) | ✅ Complete |
| `contracts/openapi.yaml` | API specification (10 endpoints) | ✅ Complete |
| `contracts/README.md` | Contract documentation | ✅ Complete |
| `quickstart.md` | Setup & deployment guide | ✅ Complete |

**Total Documentation**: 6 files, ~3,500 lines

---

## Alignment with Hackathon Goals

**6-Hour Timeline**: Plan supports rapid implementation:
- **Hour 1-2**: Setup + foundational services
- **Hour 3-4**: User Stories 1-2 (upload, extraction, generation)
- **Hour 5**: User Story 4 (export) + polish
- **Hour 6**: Deployment + demo prep

**Minimal Demo Targets** (All Met in Plan):
- ✅ Generate 2 sections end-to-end (US1 + US2)
- ✅ Export works in hosted instance (US4 + Dockerfile)
- ✅ Judges can repeat workflow via public link (quickstart deployment guides)

---

**Planning Status**: ✅ **COMPLETE**  
**Ready For**: Task breakdown (`/speckit.tasks`)  
**Constitution Compliance**: ✅ All 9 principles satisfied  
**Estimated Implementation Time**: 6 hours (per hackathon scope)
