<!--
SYNC IMPACT REPORT
==================
Version Change: [NEW] → 1.0.0
Modified Principles: N/A (initial constitution)
Added Sections:
  - Core Principles (9 principles)
  - Technical Architecture
  - Development Workflow
  - Governance
Templates Status:
  ✅ plan-template.md - reviewed, aligns with constitution checks
  ✅ spec-template.md - reviewed, user story prioritization aligns
  ✅ tasks-template.md - reviewed, phased approach aligns
Follow-up TODOs: None
-->

# EasyGrant Constitution

## Core Principles

### I. Local Context First

**MUST** retrieve all context from uploaded community documents: strategic plans, prior
grant applications, budgets, community reports, and other local assets.

**MUST NOT** generate proposals based solely on generic templates or external assumptions.

**Rationale**: Small and remote communities have unique contexts, histories, and needs that
cannot be captured by generic templates. Competitive proposals demonstrate deep local
knowledge and alignment with community-defined priorities.

### II. Requirements-Driven Generation

**MUST** extract a machine-readable checklist from every funding call document, including:
required sections, word/character limits, formatting constraints, scoring criteria, and
eligibility requirements.

**MUST** enforce all extracted requirements during section generation and quality checking.

**Rationale**: Grant applications are judged against explicit rubrics. Missing a required
section or exceeding a word limit leads to automatic rejection. Compliance is non-negotiable.

### III. Transparency & Provenance

**MUST** provide inline citations for every generated claim, linking to specific source
documents and page numbers.

**MUST** display a sources panel showing all referenced documents and retrieval metadata.

**MUST NOT** generate unsupported claims or "hallucinate" facts not grounded in uploaded
context.

**Rationale**: Grant reviewers expect verifiable claims. Transparency builds trust and enables
users to validate and defend every statement in their proposal.

### IV. Editability & User Control

**MUST** preserve user edits when regenerating sections (sticky edits).

**MUST** apply user feedback explicitly during regeneration without discarding manual changes.

**MUST** provide a clear mechanism for users to lock sections against further AI modification.

**Rationale**: Users are domain experts on their communities. The AI assists but does not
override. User edits reflect critical local knowledge and judgment that must be respected.

### V. Simplicity & User Experience

**MUST** implement a single-screen, section-by-section workflow with minimal navigation.

**MUST** provide sensible defaults for all configuration (models, chunking, retrieval
parameters).

**MUST** minimize user clicks and cognitive load; essential actions only.

**Rationale**: Target users are grant writers in under-resourced communities, often working
under tight deadlines. Complexity is a barrier to adoption. Simplicity ensures accessibility.

### VI. Neutral Language

**MUST** generate proposal text in neutral, professional, grant-appropriate language.

**MUST NOT** inject subjective opinions, advocacy tone, or promotional language unless
explicitly present in source documents.

**Rationale**: Grant reviewers expect objective, evidence-based language. Overly promotional
or subjective tone undermines credibility and scoring.

### VII. Privacy & Security

**MUST** process all uploaded documents server-side; no client-side API keys or sensitive
data exposure.

**MUST** provide a one-click "Delete all data" option to remove uploads, vector indices, and
generated content.

**MUST** store data on local disk only (`/data/uploads`, `/vector`); no third-party storage.

**Rationale**: Community documents may contain confidential information (budgets, strategies,
demographic data). Privacy and user control over data deletion are mandatory.

### VIII. Maintainability & Configuration

**MUST** externalize all operational parameters (models, embedding dimensions, chunk size,
overlap, top-k retrieval) in a single `config.yaml` file.

**MUST** use adapter patterns for different funding call types to minimize code changes.

**MUST** minimize third-party dependencies; prefer standard library and well-maintained,
widely-adopted packages.

**Rationale**: This is a hackathon prototype with limited ongoing maintenance. Config-driven
design and minimal dependencies reduce technical debt and enable rapid iteration.

### IX. Hostability & Demo-Readiness

**MUST** run as a lightweight hosted web application deployable to Render, Railway, or Hugging
Face Spaces with a single public URL.

**MUST** support basic upload → generate → export flow without local setup or credentials.

**MUST** operate within free-tier constraints of hosting platforms (low bandwidth, small
default models, server-side RAG).

**Rationale**: Hackathon judges and potential users need to test the application immediately
via a public URL. Self-hosting complexity is a barrier to evaluation and adoption.

## Technical Architecture

**Stack**: React + Vite (frontend), FastAPI (backend), Chroma (server-side vector store),
text-embedding-3-small embeddings (600 tokens, 15% overlap), GPT-4o (requirements & QC),
GPT-4o-mini (drafting), PyMuPDF + python-docx (parsing).

**Data Storage**: Local disk only (`/data/uploads`, `/vector`); no cloud or third-party
persistence.

**Agent Architecture**: Six-agent pipeline—(1) Requirements Extraction, (2) Retriever,
(3) Gap Analysis, (4) Section Generator, (5) Quality Checker, (6) Assembler (DOCX export).

**Folder Structure**: `/frontend`, `/api`, `/core`, `/data/uploads`, `/vector`, `/prompts`,
`/config.yaml`.

**Demo Scope**: Upload ≤5 documents + 1 funding call PDF; extract requirements → checklist;
generate two sections with citations; accept edit → regenerate preserving it; export DOCX.

**Out of Scope**: Performance tuning beyond demo requirements, advanced logging frameworks,
accessibility (a11y), internationalization (i18n).

## Development Workflow

**Phase Discipline**: All features follow spec → plan → tasks → implement → validate workflow
as defined in `.specify/templates/*.md`.

**Prototype Constraints**: 6-hour hackathon timeline; prioritize working demo over polish.

**Testing**: Focus on end-to-end demo flow; unit tests optional unless blocking critical paths.

**Version Control**: Commit at phase boundaries; clear commit messages referencing spec or task
IDs.

**Documentation**: Inline comments for non-obvious logic; README covers setup and demo flow;
prompts in `/prompts` for agent configurations.

## Governance

This constitution supersedes all other development practices. Any deviation from core
principles (I–IX) MUST be documented with explicit justification and user approval.

**Amendment Process**: Amendments require (1) documentation of rationale, (2) impact analysis
on templates and codebase, (3) version increment per semantic versioning.

**Compliance Verification**: During spec/plan/task reviews, verify alignment with:
- Local context retrieval (Principle I)
- Requirements extraction and enforcement (Principle II)
- Citation and provenance (Principle III)
- Edit preservation (Principle IV)
- Simplicity and UX constraints (Principle V)
- Privacy and data control (Principle VII)
- Config-driven architecture (Principle VIII)
- Hostability requirements (Principle IX)

**Complexity Justification**: Any feature increasing cognitive load, requiring additional
dependencies, or adding navigation steps MUST be justified against Principles V and VIII.

**Version**: 1.0.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-10-26
