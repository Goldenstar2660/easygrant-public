# Task Generation Summary (MVP Revision)

**Feature**: 001-proposal-assistant  
**Date**: 2025-10-26  
**Phase**: Tasks (Implementation Planning - REVISED FOR FEASIBILITY)  
**Status**: ✅ Complete - Scope Reduced from 168 to 104 tasks

---

## Revision Rationale

**Original Plan**: 168 tasks over 6 hours - **Unfeasible**  
**Revised Plan**: 104 tasks over 6 hours - **Achievable vertical slice**

### Critical Scope Cuts:
1. **Sticky edits**: Sentence-level diff/merge → **Paragraph-level locking** (80% value, 20% effort)
2. **DOCX export**: Footnotes + TOC → **Inline citations only** (faster, good enough)
3. **Indexing**: Async background → **Blocking** (small docs, fast enough)
4. **Word limits**: Retry loops → **Single pass with warning** (simpler, lower risk)
5. **Quality checker**: 0-100 scoring → **Boolean checklist** (less complexity)
6. **Deployment**: Multi-cloud → **Render only** (less config debugging)
7. **Infrastructure**: Rate limiting, analytics → **Removed** (not demo-critical)

---

## Tasks Generated (MVP)

**File**: `specs/001-proposal-assistant/tasks.md`  
**Total Tasks**: 104 tasks (reduced from 168)  
**Timeline**: 6-hour hackathon sprint  
**Organization**: 10 phases focused on winning demo

### Task Breakdown by Phase

1. **Phase 1: Hosted Skeleton** - 10 tasks, 30 min
   - Deploy skeleton to Render early (get public URL live)
   - Simple single-stage Dockerfile, FastAPI `/health` endpoint
   
2. **Phase 2: Foundation Layer** - 12 tasks, 45 min
   - Vector store (Chroma), LLM clients (OpenAI), data models
   - **Shared components** used across all features
   
3. **Phase 3: Upload → Parse → Index** - 14 tasks, 60 min
   - Upload funding call + supporting docs (PDF/DOCX)
   - **Blocking indexing** (no async - simpler, fast enough)
   - Document chunking (600 tokens, 15% overlap)
   
4. **Phase 4: Requirements Extraction** - 10 tasks, 35 min
   - Hybrid regex + GPT-4o structured output
   - Extract requirements to JSON checklist
   
5. **Phase 5: Retrieve → Generate with Citations** - 19 tasks, 65 min
   - RAG retrieval (top-5 semantic search)
   - Section generation with inline citations `[Doc, p.N]`
   - Sources panel showing retrieved chunks
   
6. **Phase 6: Simple Edit + Regenerate** - 8 tasks, 27 min
   - **Paragraph locking** (user marks paragraphs to preserve)
   - Regenerate merges only unlocked paragraphs
   - **No diff engine** (huge time saver)
   
7. **Phase 7: Export DOCX** - 10 tasks, 27 min
   - Simple DOCX export with **inline citations** (no footnote conversion)
   - No TOC (not needed for demo)
   
8. **Phase 8: Demo Mode** - 5 tasks, 18 min
   - **Critical for judges**: Auto-load sample data button
   - Zero-setup demo experience
   
9. **Phase 9: Optional Data Purge** - 4 tasks, 10 min
   - One-click privacy deletion (P3 - nice to have)
   
10. **Phase 10: Polish & Final Testing** - 12 tasks, 43 min
    - UI polish: pinned acceptance criteria, 4-panel layout
    - E2E testing, public URL validation

---

## Task Priority Distribution

- **P1 (Must-Have)**: 87 tasks - Core vertical slice (Phases 1-7)
- **P2 (Polish)**: 13 tasks - Demo mode, UI enhancements, docs
- **P3 (Optional)**: 4 tasks - Data purge feature

---

## Critical Path

**Longest Dependency Chain**: ~309 minutes (5.15 hours)

```
Phase 1 (Hosted Skeleton)
  ↓ 30 min
Phase 2 (Foundation: Vector Store + LLM + Models)
  ↓ 45 min
Phase 3 (Upload + Parse + Index - BLOCKING)
  ↓ 60 min
Phase 4 (Requirements Extraction)
  ↓ 35 min
Phase 5 (RAG Generation + Citations)
  ↓ 65 min
Phase 6 (Paragraph Locks)
  ↓ 27 min
Phase 7 (Export)
  ↓ 27 min
Testing (Final Validation)
  ↓ 20 min
TOTAL: 309 min (5.15 hours)
```

**Buffer**: 45 minutes for unexpected issues  
**Parallel Opportunities**: Frontend/backend tasks can overlap (reduces to ~4.5 hours with 2 devs)

---

## What Was Cut (Deferred to Post-Hackathon)

### Complex Features Removed:
| Feature | Old Tasks | Replacement | Time Saved |
|---------|-----------|-------------|------------|
| Sentence-level diff/merge | T086-T104 (19 tasks) | Paragraph locking (8 tasks) | ~33 min |
| Footnote conversion + TOC | T107-T110 | Inline citations only | ~15 min |
| Async background indexing | T036 | Blocking indexing | ~10 min |
| Word-limit retry loops | T061-T062 | Single pass + warning | ~8 min |
| Quality scoring 0-100 | T066 | Boolean checklist | ~5 min |
| Rate limiting + analytics | T151-T153 | Removed | ~15 min |
| Multi-cloud configs | T146-T147 | Render only | ~12 min |
| Multi-stage Dockerfile | T140 | Single-stage | ~8 min |

**Total Time Saved**: ~106 minutes (1.77 hours)

### Why These Cuts Work:
- **Paragraph locking**: Judges won't notice the difference from sentence-level diff
- **Inline citations**: Readable and traceable (footnotes are polish, not core value)
- **Blocking indexing**: 5 docs × 20 pages = ~100 chunks, indexes in <5 seconds
- **Single deployment**: Less debugging, faster iteration
- **Demo mode**: Makes judges' lives easier (zero setup = higher scores)

---

## Judge Criteria Mapping (MVP Coverage)

All 9 judge criteria still covered with reduced scope:

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

1. **✅ COMPLETED**: Task breakdown revised (104 tasks, MVP scope)
2. **⏳ PENDING**: Begin Phase 1 (hosted skeleton - 30 min to public URL)
3. **⏳ PENDING**: Checkpoint after Phase 5 (upload → extract → generate working)
4. **⏳ PENDING**: Implement Phase 8 (demo mode) early for judge testing
5. **⏳ PENDING**: Final validation (T100-T104) before submission

---

## Files Created/Updated

- ✅ `specs/001-proposal-assistant/tasks.md` - 104 implementation tasks (REVISED)
- ✅ `specs/001-proposal-assistant/TASKS_SUMMARY.md` - This summary document (UPDATED)

---

**Path to Win**: 
- Vertical slice proof-of-concept beats feature-bloated half-finish
- Smooth demo with demo mode = zero friction for judges
- Public URL in README/video = professional presentation
- Paragraph locks are "good enough" for editability demo
- Inline citations are traceable and readable

**Task generation phase complete with feasible scope** ✅  
**Ready to ship in 6 hours** 🚀

