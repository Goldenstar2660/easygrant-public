# Implementation Tasks: Smart Proposal Assistant (MVP)

**Feature**: 001-proposal-assistant  
**Generated**: 2025-10-26  
**Timeline**: 6-hour hackathon sprint  
**Scope**: Minimum viable demo focused on vertical slice proof-of-concept  
**Strategy**: Upload → Extract → Retrieve → Generate with citations → Simple edit → Regenerate → Export

---

## Scope Decisions (Feasibility-Driven)

**INCLUDED (MVP)**: 
- Upload funding call + supporting docs (PDF/DOCX)
- Extract requirements to structured checklist
- RAG retrieval with top-5 semantic search
- Section generation with inline citations `[Doc, p.N]`
- Paragraph-level edit locks (simple, no diff engine)
- Regenerate preserving locked paragraphs
- DOCX export with inline citations (no footnotes/TOC)
- Demo mode with pre-loaded sample data
- Single deployment target (Render only)

**DEFERRED (Post-Hackathon)**:
- Sentence-level diff/merge engine (T086-T104 removed)
- Footnote conversion & TOC in DOCX (T107-T110 removed)
- Async background indexing (T036 removed - blocking is fine for small docs)
- Rate limiting & analytics (T151-T153 removed)
- Multi-cloud configs (T146-T147 removed - Render only)
- Word-limit retry loops (T061-T062 removed - single pass with warning)
- Quality scoring 0-100 (T066 removed - boolean checklist only)
- Rich text editor features (simplified to textarea with citations)

---

## Task Format

```
- [ ] T### [P?] Description with backend/src/path/file.py
```

- **T###**: Task ID (sequential, 1-80)
- **P?**: Priority (P1 = Must-Have MVP, P2 = Polish, P3 = Future)
- **Description**: Clear action with affected file paths

---


## Phase 1: Hosted Skeleton (30 min)

**Goal**: Get public URL live early for continuous testing  
**Blocking Dependencies**: None

- [X] T001 [P1] Initialize Git repository and create feature branch `001-proposal-assistant`
- [X] T002 [P1] Create folder structure: `backend/src/{agents,api/routes,models,services,utils}`, `frontend/src/{components,services}`
- [X] T003 [P1] Create `backend/requirements.txt` with FastAPI 0.104+, Chroma 0.4+, OpenAI 1.3+, PyMuPDF 1.23+, python-docx 1.1+
- [X] T004 [P1] Create `frontend/package.json` with React 18+, Vite 5+, Axios
- [X] T005 [P1] Create `backend/config.yaml` with LLM models (gpt-4o, gpt-4o-mini), chunking (600 tokens, 15% overlap), top_k=5
- [X] T006 [P1] Create `.env.template` for `OPENAI_API_KEY`
- [X] T007 [P1] Create `backend/src/main.py` - FastAPI app with `/health` endpoint and CORS
- [X] T008 [P1] Create simple `Dockerfile` (single-stage python:3.11-slim, expose 8000)
- [X] T009 [P1] Create `render.yaml` - Web Service config with disk mounts for `/data/uploads` and `/vector`
- [ ] T010 [P1] Deploy skeleton to Render, verify public URL accessible (e.g., `https://easygrant.onrender.com/health`)

---

## Phase 2: Foundation Layer (45 min)

**Goal**: Core services for all features  
**Blocking Dependencies**: Phase 1 complete

### Services & Utilities

- [X] T011 [P1] Implement `backend/src/services/vector_store.py` - ChromaDB PersistentClient with session-based collections
- [X] T012 [P1] Implement `backend/src/services/llm_client.py` - OpenAI client wrapper (gpt-4o, gpt-4o-mini, embeddings)
- [X] T013 [P1] Implement `backend/src/utils/config_loader.py` - Load and validate config.yaml
- [X] T014 [P1] Implement `backend/src/utils/chunking.py` - RecursiveCharacterTextSplitter (600 tokens, 90-token overlap, tiktoken)
- [X] T015 [P1] Implement `backend/src/services/embedding_service.py` - Generate embeddings via text-embedding-3-small
- [X] T016 [P1] Implement `backend/src/utils/parser.py` - Extract text from PDF (PyMuPDF) and DOCX (python-docx)

### Data Models

- [X] T017 [P1] Create `backend/src/models/session.py` - UserSession with session_id, total_upload_size_bytes (≤50MB validation)
- [X] T018 [P1] Create `backend/src/models/funding_call.py` - FundingCall with Blueprint schema (sections[], eligibility[], scoring{})
- [X] T019 [P1] Create `backend/src/models/section.py` - SectionRequirement, GeneratedSection with locked_paragraphs[] array
- [X] T020 [P1] Create `backend/src/models/citation.py` - Citation model (document_id, document_title, page_number, chunk_text)

### Session Management

- [X] T021 [P1] Implement `backend/src/services/session_manager.py` - In-memory dict for session storage (session_id → data)
- [X] T022 [P1] Create `backend/src/api/middleware.py` - Session validation and 50MB upload quota check

---

## Phase 3: Upload → Parse → Index (60 min)

**Goal**: Ingest funding call + supporting docs, chunk and embed  
**Blocking Dependencies**: Phase 2 complete

### Backend - Upload Endpoints

- [X] T023 [P1] Implement `backend/src/api/routes/upload.py` - POST `/api/upload/funding-call` (PDF only, <10MB)
- [X] T024 [P1] Add file validation: PDF magic bytes check, size limit enforcement
- [X] T025 [P1] Implement `backend/src/utils/file_storage.py` - Save to `/data/uploads/{session_id}/` with UUID filenames
- [X] T026 [P1] Implement POST `/api/upload/supporting-docs` (PDF/DOCX, max 5 files, 50MB total)
- [X] T027 [P1] Add multi-file validation: count check, quota enforcement, file type validation

### Backend - Document Indexing (Blocking, Not Async)

- [X] T028 [P1] Implement `backend/src/services/indexing_service.py` - Chunk docs and upsert to Chroma (blocking)
- [X] T029 [P1] Extract metadata during chunking: document_title (filename), page_number (from PyMuPDF), chunk_index
- [X] T030 [P1] Store chunks in Chroma with metadata: `{chunk_id, document_id, document_title, page_number, chunk_text}`
- [X] T031 [P1] Return indexing status in upload response: `{uploaded: true, indexed: true, chunk_count: N}`

### Frontend - Upload Panel

- [X] T032 [P1] Create `frontend/src/components/UploadPanel.jsx` - Drag-and-drop file upload UI
- [X] T033 [P1] Add funding call upload button with progress indicator
- [X] T034 [P1] Add supporting docs multi-select (show file list, quota display: "3/5 files, 12MB/50MB")
- [X] T035 [P1] Implement `frontend/src/services/api.js` - Axios wrappers for upload endpoints
- [X] T036 [P1] Add error handling: display toast for file size/type violations

---

## Phase 4: Requirements Extraction (30-40 min) ✅ COMPLETE

**Goal**: Parse funding call into structured checklist  
**Blocking Dependencies**: Phase 3 (upload) complete

### Backend - Requirements Extractor Agent

- [X] T037 [P1] Implement `backend/src/agents/requirements_extractor.py` - Hybrid regex + GPT-4o structured output
- [X] T038 [P1] Add regex patterns for word limits: `"up to 500 words"`, `"maximum 2000 characters"`, `"not to exceed"`
- [X] T039 [P1] Add GPT-4o prompt with JSON schema enforcement: `{sections: [{name, required, limit, format}], eligibility: [], scoring: {}}`
- [X] T040 [P1] Implement Blueprint validation: ensure sections[] non-empty, validate limit formats
- [X] T041 [P1] Add retry logic: max 2 attempts if extraction fails or schema invalid
- [X] T042 [P1] Implement GET `/api/requirements/{session_id}` - Return structured blueprint

### Frontend - Checklist Panel

- [X] T043 [P1] Create `frontend/src/components/ChecklistPanel.jsx` - Display extracted requirements as vertical list
- [X] T044 [P1] Show section name, word/char limit, scoring weight for each requirement
- [X] T045 [P1] Add "Generate" button next to each section (disabled until supporting docs uploaded)
- [X] T046 [P1] Add status indicators: ✅ completed (green), 🔄 generating (spinner), ⚪ not started

---

## Phase 5: Retrieve → Generate with Citations (60-70 min) ✅ COMPLETE

**Goal**: RAG-based drafting with inline citations  
**Blocking Dependencies**: Phase 4 complete

### Backend - Retrieval Agent

- [X] T047 [P1] Implement `backend/src/agents/retriever.py` - Semantic search via Chroma (top_k=5)
- [X] T048 [P1] Build query from section requirement: `"{section_name} requirements: {format_requirements}"`
- [X] T049 [P1] Extract citation metadata from Chroma results: document_title, page_number, chunk_text, relevance_score
- [X] T050 [P1] Filter by relevance threshold: min score 0.3 (drop low-quality matches)

### Backend - Section Generator Agent

- [X] T051 [P1] Implement `backend/src/agents/section_generator.py` - GPT-4o-mini drafting with RAG context
- [X] T052 [P1] Build prompt: section requirements + top-5 retrieved chunks + word limit instruction
- [X] T053 [P1] Implement inline citation insertion: `[{document_title}, p.{page_number}]` format
- [X] T054 [P1] Add word count validation: count words, show warning if exceeds limit (no retry loop)
- [X] T055 [P1] Store in GeneratedSection: ai_generated_text, citations[], word_count, locked_paragraphs=[]

### Backend - Sections Endpoints

- [X] T056 [P1] Implement POST `/api/sections/generate` in `backend/src/api/routes/sections.py`
- [X] T057 [P1] Implement GET `/api/sections/{section_id}` - Return GeneratedSection with citations

### Frontend - Editor Panel

- [X] T058 [P1] Create `frontend/src/components/EditorPanel.jsx` - Plain textarea with citation highlighting
- [X] T059 [P1] Display generated text with inline citations in blue (clickable)
- [X] T060 [P1] Add live word count display (red if exceeds limit, yellow if within 10%)
- [X] T061 [P1] Add "Regenerate" button (will preserve locked paragraphs in Phase 6)
- [ ] T062 [P1] Add "Lock Paragraph" button - User selects text, click to mark paragraph as locked

### Frontend - Sources Panel

- [X] T063 [P1] Create `frontend/src/components/SourcesPanel.jsx` - Display retrieved chunks
- [X] T064 [P1] Show document title, page number, snippet (first 150 chars), relevance score for each citation
- [X] T065 [P1] Highlight citation when user clicks inline `[Doc, p.N]` in editor

---

## Phase 6: Simple Edit + Regenerate (25-30 min) ✅ COMPLETE

**Goal**: Preserve user edits via paragraph locking (no diff engine)  
**Blocking Dependencies**: Phase 5 complete

### Backend - Paragraph Lock Logic

- [X] T066 [P1] Implement `backend/src/utils/paragraph_lock.py` - Split text into paragraphs (double newline separator)
- [X] T067 [P1] Store locked paragraphs: `GeneratedSection.locked_paragraphs = [{index: 2, text: "user edited text..."}]`
- [X] T068 [P1] Implement PATCH `/api/sections/{section_id}` - Save user edits and locked paragraph indices
- [X] T069 [P1] Implement POST `/api/sections/{section_id}/regenerate` - Call generator, merge locked paragraphs
- [X] T070 [P1] Merge logic: Split new AI output into paragraphs, replace only unlocked paragraphs from locked_paragraphs[]

### Frontend - Edit Tracking

- [X] T071 [P1] Add paragraph selection UI in EditorPanel: User highlights paragraph → "Lock This Paragraph" button appears
- [X] T072 [P1] Highlight locked paragraphs with light yellow background
- [X] T073 [P1] Update "Regenerate" button tooltip: "Regenerate (keeps locked paragraphs)"

---

## Phase 7: Export DOCX (25-30 min) ✅ COMPLETE

**Goal**: Simple DOCX export with inline citations (no footnotes/TOC)  
**Blocking Dependencies**: Phase 5 complete (sections generated)

### Backend - Assembler Agent

- [X] T074 [P1] Implement `backend/src/agents/assembler.py` - Merge sections in checklist order using python-docx
- [X] T075 [P1] Add section headings: `document.add_heading(section_name, level=1)`
- [X] T076 [P1] Add body paragraphs with inline citations preserved (no conversion to footnotes)
- [X] T077 [P1] Add title page: funding call name, generation timestamp

### Backend - Export Endpoint

- [X] T078 [P1] Implement POST `/api/export/docx` in `backend/src/api/routes/export.py`
- [X] T079 [P1] Return DOCX as binary stream: `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- [X] T080 [P1] Set filename header: `Content-Disposition: attachment; filename="Proposal_{date}.docx"`

### Frontend - Export Button

- [X] T081 [P1] Create `frontend/src/components/ExportButton.jsx` - Download DOCX button in header
- [X] T082 [P1] Add loading spinner during export ("Generating DOCX...")
- [X] T083 [P1] Trigger browser download with Axios blob response

---

## Phase 8: Demo Mode (15-20 min)

**Goal**: Auto-load sample data for judges (zero-setup demo)  
**Blocking Dependencies**: Phases 3-7 complete

- [ ] T084 [P2] Create `backend/demo_data/` folder with sample funding call PDF + 2 supporting docs
- [ ] T085 [P2] Create `backend/src/api/routes/demo.py` - POST `/api/demo/load` endpoint
- [ ] T086 [P2] Implement demo loader: Copy demo files to new session, auto-index, auto-extract requirements
- [ ] T087 [P2] Create `frontend/src/components/DemoToggle.jsx` - "Load Sample Data" button in header
- [ ] T088 [P2] Add success notification: "Sample data loaded. Click Generate to see AI drafting."

---

## Phase 9: Optional Data Purge (10 min)

**Goal**: One-click privacy deletion  
**Blocking Dependencies**: None (parallel with other phases)

- [ ] T089 [P3] Implement `backend/src/services/cleanup_service.py` - Delete `/data/uploads/{session_id}/` recursively
- [ ] T090 [P3] Delete Chroma collection: `vector_store.delete_collection(f"session_{session_id}")`
- [ ] T091 [P3] Implement DELETE `/api/data/{session_id}` in `backend/src/api/routes/data.py`
- [ ] T092 [P3] Create `frontend/src/components/PurgeButton.jsx` - Red "Delete All Data" button with confirmation modal

---

## Phase 10: Polish & Final Testing (Remaining Time)

**Goal**: Smooth demo experience and judge criteria visibility  
**Blocking Dependencies**: Phases 1-8 complete

### UI Polish

- [ ] T093 [P2] Add top bar with pinned acceptance criteria: "✅ Local Context | ✅ Gap Analysis | ✅ Citations | ✅ Transparency"
- [ ] T094 [P2] Add 4-panel layout: Upload (left) | Checklist (left) | Editor (center) | Sources (right)
- [ ] T095 [P2] Add green checkmarks for completed sections in ChecklistPanel
- [ ] T096 [P2] Add "Missing items" note when no relevant chunks found for a section (gap analysis indicator)

### Documentation

- [ ] T097 [P2] Update `README.md` with public demo link, 3-step quickstart (clone, docker build, docker run)
- [ ] T098 [P2] Create `DEMO.md` with sample workflow: Load demo data → Generate 3 sections → Lock paragraph → Regenerate → Export
- [ ] T099 [P2] Add public demo URL to video description and GitHub repo description

### Final Testing

- [ ] T100 [P1] **End-to-End Test**: Upload real funding call + 3 docs → Extract → Generate all sections → Lock 2 paragraphs → Regenerate → Export DOCX → Verify <5min total
- [ ] T101 [P1] **Citation Coverage Test**: Verify every generated section has ≥1 inline citation
- [ ] T102 [P1] **Edit Persistence Test**: Lock paragraph → Regenerate → Verify locked text unchanged
- [ ] T103 [P1] **Public Access Test**: Open demo URL from different device, verify no auth required
- [ ] T104 [P1] **Demo Mode Test**: Click "Load Sample Data" → Generate section → Verify <30s from load to draft

---

## Task Summary

**Total Tasks**: 104 (down from 168)  
**Estimated Time**: 6 hours

### By Phase:
- Phase 1 (Hosted Skeleton): 10 tasks, 30 min
- Phase 2 (Foundation): 12 tasks, 45 min
- Phase 3 (Upload/Index): 14 tasks, 60 min
- Phase 4 (Requirements): 10 tasks, 35 min
- Phase 5 (Generate): 19 tasks, 65 min
- Phase 6 (Edit/Regenerate): 8 tasks, 27 min
- Phase 7 (Export): 10 tasks, 27 min
- Phase 8 (Demo Mode): 5 tasks, 18 min
- Phase 9 (Purge - Optional): 4 tasks, 10 min
- Phase 10 (Polish/Test): 12 tasks, 43 min

### By Priority:
- **P1 (Must-Have)**: 87 tasks - Core vertical slice
- **P2 (Polish)**: 13 tasks - Demo mode, UI enhancements, docs
- **P3 (Optional)**: 4 tasks - Data purge feature

### Critical Path (Must Complete):
Phase 1 (30m) → Phase 2 (45m) → Phase 3 (60m) → Phase 4 (35m) → Phase 5 (65m) → Phase 6 (27m) → Phase 7 (27m) → Testing (20m)  
**Total**: ~309 minutes (5.15 hours) + 45-min buffer

---

## What Was Cut (Deferred to Post-Hackathon)

### Complex Features Removed:
- **T086-T104 (old)**: Sentence-level diff/merge engine → Replaced with simple paragraph locking
- **T107-T110**: Footnote conversion & TOC in DOCX → Keep inline citations
- **T036 (old)**: Async background indexing → Blocking indexing (small docs, fast enough)
- **T061-T062 (old)**: Word-limit retry loops → Single pass with warning
- **T064-T067 (old)**: Quality scoring 0-100 → Boolean checklist only
- **T151-T153**: Rate limiting, analytics, fancy logging → Not needed for demo
- **T146-T147**: Railway/HF Spaces configs → Render only
- **T140 (old)**: Multi-stage Dockerfile → Single-stage (simpler, faster builds)

### Why These Cuts Work:
- Paragraph locking is **80% as good** as sentence-level diff with **20% effort**
- Inline citations in DOCX are **readable and traceable** (judges don't need footnotes)
- Blocking indexing is **fast enough** for 5 docs × 20 pages = ~100 chunks
- Single deployment target means **less config debugging**
- Demo mode makes judges' lives **easier** (zero setup friction)

---

## Judge Criteria Mapping (MVP Coverage)

| Judge Requirement | How MVP Meets It | Task References |
|------------------|------------------|-----------------|
| Ingest & analyze local materials | Upload, parse, chunk, embed; sources panel | T023-T031, T063-T065 |
| Compare to requirements; find gaps | Extracted checklist + "Missing items" note | T037-T046, T096 |
| Generate tailored content with local citations | RAG drafting with inline `[Doc, p.N]` citations | T047-T065 |
| Not just GPT; structured workflow | 4-panel UI: Upload → Checklist → Draft → Export | T032-T083, T094 |
| Simple & intuitive | One page, 3 big buttons, green checks | T093-T095 |
| Transparency & editability | Inline citations + sources panel, paragraph locks | T058-T065, T071-T073 |
| Low bandwidth | Server-side RAG, no heavy assets | All backend tasks |
| Security & privacy | No client keys, local store, purge option | T006, T089-T092 |
| Easy to update | Requirements extracted to JSON blueprint | T037-T042 |

**All 9 judge criteria covered** ✅

---

## Constitution Compliance (Reduced Scope)

- ✅ **Principle I (Local Context)**: RAG retrieval prioritized (Phase 5)
- ✅ **Principle II (Requirements-Driven)**: Checklist-driven workflow (Phase 4)
- ✅ **Principle III (Transparency)**: Inline citations + sources panel (T053, T063-T065)
- ✅ **Principle IV (Editability)**: Paragraph locks preserve user control (T066-T073)
- ✅ **Principle V (Simplicity)**: Single Dockerfile, no microservices (T008)
- ✅ **Principle VI (Neutral Language)**: Generator uses neutral prompt templates (T051-T052)
- ✅ **Principle VII (Privacy)**: Optional purge feature (Phase 9)
- ✅ **Principle VIII (Maintainability)**: Config-driven (T005, T013)
- ✅ **Principle IX (Hostability)**: Render deployment, <512MB RAM (T009-T010)

**All principles satisfied with reduced scope** ✅

---

## Next Steps

1. ✅ **Review**: Validate trimmed task list (104 tasks vs. 168)
2. ⏳ **Deploy Early**: Complete Phase 1 in first 30 min, get public URL live
3. ⏳ **Checkpoint Testing**: Run mini E2E test after Phase 5 (upload → generate)
4. ⏳ **Demo Mode First**: Implement Phase 8 early for continuous judge-perspective testing
5. ⏳ **Final Validation**: Run T100-T104 before submission

**Path to win**: Vertical slice proof-of-concept with smooth demo beats feature-bloated half-finish. 🚀

