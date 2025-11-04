# Feature 001: Smart Proposal Assistant - Specification Summary

**Branch**: `001-proposal-assistant`  
**Created**: 2025-10-26  
**Status**: ✅ Specification Complete - Ready for Planning

## Quick Overview

This feature delivers a hosted demo of EasyGrant's Smart Proposal Assistant—a public web application where judges can test the complete grant writing workflow: upload funding call → auto-extract requirements checklist → upload local community documents → generate cited sections with RAG → edit with sticky preservation → export DOCX.

## User Stories (5 total)

### Priority 1 (MVP Critical)
1. **Upload & Requirements Extraction** - Upload funding call PDF + 5 supporting docs, auto-extract structured checklist
2. **Cited Section Generation** - Select section from checklist, generate draft with inline citations [Doc, p.N], view sources panel

### Priority 2 (High Value)
3. **Sticky Edits & Regeneration** - Manual edits persist when regenerating with new context
4. **DOCX Export** - Merge sections in order, format with footnotes, download submission-ready file

### Priority 3 (Privacy/Trust)
5. **One-Click Data Deletion** - Remove all uploads, drafts, and vector indices with confirmation

## Key Requirements

- **Functional**: 20 testable requirements (FR-001 to FR-020)
  - Requirements extraction from PDF
  - Upload limits (5 docs, <50MB total)
  - Server-side RAG with 600-token chunks, top-5 retrieval
  - Inline citations with document + page
  - Word limit enforcement with auto-retry
  - Sticky edits on regeneration
  - DOCX export with footnotes
  - One-click data deletion
  - Three-panel UI (checklist | editor | sources)
  - Single-service deployment to Render/Railway/Hugging Face Spaces

- **Success Criteria**: 10 measurable outcomes (SC-001 to SC-010)
  - Demo accessible and completable in <5 minutes
  - 80%+ extraction accuracy for standard grant RFPs
  - 90%+ sections within word limits on first attempt
  - 100% citation coverage (no hallucinations)
  - 100% edit persistence across regeneration
  - DOCX opens cleanly in Word 2016+
  - Upload/indexing <60sec for 5 docs (~100 pages)
  - Generation <30sec for 500-word section
  - Deletion <5sec with confirmation
  - Runs on free-tier: <512MB RAM, <1GB storage, 10+ concurrent users

## Edge Cases Covered (8)

- Missing requirements in funding call → show warning
- Upload >50MB → block with error
- Generation exceeds word limit → auto-retry with stricter constraints
- No relevant citations found → warning to upload more docs
- User edits exceed word limit → red warning before export
- Network drop during generation → retry dialog with auto-save
- Corrupted/password-protected PDF → parse error
- Out of memory during indexing → suggest reducing upload size

## Validation Results

**Checklist Status**: ✅ 16/16 items passed (100%)

- ✅ No implementation details in spec (tech stack only in Dependencies)
- ✅ User-focused language (grant writers, community staff)
- ✅ All requirements testable and unambiguous
- ✅ Success criteria measurable and technology-agnostic
- ✅ No [NEEDS CLARIFICATION] markers (all assumptions documented)
- ✅ Acceptance scenarios map to functional requirements
- ✅ Scope clearly bounded (Out of Scope section)

**Ready for**: `/speckit.plan` command to generate implementation plan

## Alignment with Constitution

This specification directly implements 7 of 9 constitutional principles:

- ✅ **I. Local Context First** - FR-002, FR-004, FR-005 (upload, index, retrieve local docs)
- ✅ **II. Requirements-Driven** - FR-001, FR-007, FR-017 (extract checklist, enforce limits)
- ✅ **III. Transparency** - FR-006, FR-008 (inline citations, sources panel)
- ✅ **IV. Editability** - FR-009, FR-010 (sticky edits, section locking)
- ✅ **V. Simplicity** - FR-013, SC-001 (three-panel UI, <5min workflow)
- ✅ **VII. Privacy** - FR-003, FR-012 (server-side only, one-click deletion)
- ✅ **IX. Hostability** - FR-014, FR-015, SC-010 (single service, no setup, free-tier)

Principles VI (neutral language) and VIII (maintainability) are addressed in FR-016 and Dependencies section.

## Files Created

```
specs/001-proposal-assistant/
├── spec.md                          # Main specification (this document's source)
├── checklists/
│   └── requirements.md              # Quality validation checklist
└── SUMMARY.md                       # This file
```

## Next Steps

1. Run `/speckit.plan` to generate implementation plan with:
   - Technical context (FastAPI + React stack)
   - Constitution compliance gates
   - Project structure (frontend/, api/, core/)
   - Phased implementation roadmap

2. After plan approval, run `/speckit.tasks` to break down into:
   - Phase 1: Setup (project init, dependencies)
   - Phase 2: Foundation (upload, parsing, vector store)
   - Phase 3: User Story 1 implementation (upload + extraction)
   - Phase 4: User Story 2 implementation (generation + citations)
   - And so on...

3. Begin implementation with constitution compliance verification at each phase

---

**Estimated Effort**: 6-hour hackathon (as per project scope)  
**Demo Readiness**: High - all acceptance criteria are judge-testable via public URL
