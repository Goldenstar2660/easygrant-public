# Feature Specification: Smart Proposal Assistant (Hosted Demo)

**Feature Branch**: `001-proposal-assistant`  
**Created**: 2025-10-26  
**Status**: Draft  
**Input**: User description: "Build a hosted Smart Proposal Assistant accessible via a public link for judges. Users – community staff or volunteers. Goals – parse funding call → structured checklist; map local docs via RAG; draft cited sections; keep edits sticky; simple UI (left: checklist / center: editor / right: sources); export DOCX. Deployment – single FastAPI + React service deployable on Render/Railway/Hugging Face Spaces."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload & Requirements Extraction (Priority: P1)

A grant writer from a small community receives a new funding opportunity PDF. They open the hosted demo link, upload the funding call document plus up to 5 supporting documents (community plans, prior proposals, budgets), and immediately see a structured checklist showing all required sections, word limits, and eligibility criteria automatically extracted from the funding call.

**Why this priority**: This is the foundational capability. Without requirements extraction and document upload, no other features can function. Demonstrates the core AI value proposition (automated parsing) and establishes the context (local documents) for all subsequent generation.

**Independent Test**: Can be fully tested by uploading a funding call PDF and validating that the system displays a readable, accurate checklist of requirements without any manual input. Delivers immediate value by saving grant writers hours of manual requirement analysis.

**Acceptance Scenarios**:

1. **Given** user opens the public demo URL, **When** they click "Upload Funding Call", **Then** they see a file picker accepting PDF files up to 10MB
2. **Given** user has selected a funding call PDF, **When** upload completes, **Then** system displays a loading indicator with status "Extracting requirements..."
3. **Given** requirements extraction completes, **When** results are ready, **Then** checklist appears in left panel showing: section names, word/character limits, format requirements, scoring criteria, eligibility conditions
4. **Given** checklist is displayed, **When** user clicks "Upload Supporting Docs", **Then** they can select up to 5 additional files (PDF, DOCX, TXT) containing local context
5. **Given** supporting docs are uploaded, **When** processing completes, **Then** system shows confirmation with document count and total pages indexed

---

### User Story 2 - Cited Section Generation (Priority: P1)

After uploading documents and seeing the requirements checklist, the grant writer clicks on a required section (e.g., "Community Need Statement - max 500 words"). The system retrieves relevant chunks from the uploaded community documents, generates a draft section that stays within the word limit, and displays inline citations showing which source document and page each claim came from. The sources panel on the right shows all referenced documents with retrieval scores.

**Why this priority**: This is the core value delivery of the AI assistant—generating draft text grounded in local context with full transparency. Without this, the system is just a document parser. This story alone demonstrates the complete RAG pipeline and citation mechanism.

**Independent Test**: Can be fully tested by selecting a checklist section, clicking "Generate", and verifying the output includes: (a) text within specified word limit, (b) inline citations in format [Doc Title, p.X], (c) sources panel listing all referenced documents, (d) neutral grant-appropriate language. Delivers immediate drafting value.

**Acceptance Scenarios**:

1. **Given** checklist is displayed with requirements, **When** user clicks on a section item, **Then** section editor opens in center panel with section name and word limit displayed
2. **Given** section editor is open, **When** user clicks "Generate Draft", **Then** loading indicator appears with status "Retrieving local context..."
3. **Given** generation completes, **When** draft appears, **Then** text includes inline citations in format [Source Title, p.N] after each claim
4. **Given** draft is displayed, **When** user views the text, **Then** word count indicator shows current count vs. limit (e.g., "487 / 500 words") and turns red if limit exceeded
5. **Given** draft includes citations, **When** user views right panel, **Then** sources panel lists all referenced documents with: document title, page numbers cited, relevance score

---

### User Story 3 - Sticky Edits & Regeneration (Priority: P2)

The grant writer reviews a generated section and notices it missed a key detail from their strategic plan. They manually add a sentence describing their rural broadband initiative. After adding more supporting documents, they click "Regenerate (keep edits)" to update other parts of the section. The system preserves their manually added sentence while updating surrounding text with new context, maintaining all word limits and citations.

**Why this priority**: This demonstrates user control and trust—the AI assists but doesn't override local expertise. Critical for adoption by communities who know their context best. Without sticky edits, users lose work on every regeneration.

**Independent Test**: Can be fully tested by (a) generating initial draft, (b) manually editing specific sentences, (c) clicking "Regenerate (keep edits)", (d) verifying edited sentences remain unchanged while other text updates. Delivers confidence that user expertise is respected.

**Acceptance Scenarios**:

1. **Given** generated draft is displayed in editor, **When** user types/edits text directly, **Then** edited regions are highlighted or marked to indicate user modifications
2. **Given** user has made edits, **When** they click "Regenerate (keep edits)", **Then** confirmation dialog asks "This will update AI-generated text while preserving your edits. Continue?"
3. **Given** user confirms regeneration, **When** process completes, **Then** manually edited sentences remain exactly as user typed them
4. **Given** regeneration preserves edits, **When** new draft appears, **Then** surrounding AI-generated text updates with new context while respecting word limits
5. **Given** edits are sticky across regenerations, **When** user clicks "Lock Section", **Then** section becomes read-only and excluded from future regenerations

---

### User Story 4 - DOCX Export (Priority: P2)

After drafting and editing multiple sections, the grant writer clicks "Export Proposal". The system merges all completed sections in checklist order, formats them according to funding call requirements, includes all citations as footnotes, and downloads a DOCX file. The grant writer opens the file in Microsoft Word and sees properly formatted sections ready for final review and submission.

**Why this priority**: Export is essential for real-world usage—grant applications are submitted as formatted documents, not web forms. Without export, the system is a demo toy. DOCX format ensures compatibility with all grant portals and funder requirements.

**Independent Test**: Can be fully tested by (a) generating at least 2 sections, (b) clicking "Export Proposal", (c) opening downloaded DOCX file, (d) verifying sections appear in correct order, word limits are met, citations are formatted as footnotes, and file opens cleanly in Word. Delivers submission-ready output.

**Acceptance Scenarios**:

1. **Given** at least one section is generated, **When** user clicks "Export Proposal", **Then** modal appears showing export options: include incomplete sections (yes/no), citation format (inline/footnotes)
2. **Given** user selects export options, **When** they click "Download DOCX", **Then** file downloads with naming format: `[FundingCallName]_Proposal_[Date].docx`
3. **Given** DOCX file downloads, **When** user opens in Microsoft Word, **Then** sections appear in checklist order with proper headings, paragraph spacing, and page breaks
4. **Given** exported document includes citations, **When** user views footnotes, **Then** each citation shows full document title, page number, and retrieval timestamp
5. **Given** export is complete, **When** user returns to web app, **Then** green checkmarks appear next to exported sections in checklist

---

### User Story 5 - One-Click Data Deletion (Priority: P3)

A community member finishes their demo and wants to ensure confidential budget documents are removed from the system. They click "Delete All Data" in settings. The system immediately removes all uploaded files, generated drafts, and vector indices, shows confirmation with details of what was deleted, and returns to the empty upload screen.

**Why this priority**: Privacy and trust are critical per Constitution Principle VII, especially for confidential community documents. However, this is lower priority than core drafting functionality for a demo—judges will test upload/generate/export first.

**Independent Test**: Can be fully tested by (a) uploading documents and generating sections, (b) clicking "Delete All Data", (c) verifying confirmation shows file count and storage cleared, (d) checking that upload screen is empty and previous documents are gone. Delivers privacy assurance.

**Acceptance Scenarios**:

1. **Given** user has uploaded documents and generated content, **When** they click settings menu, **Then** "Delete All Data" option is visible with warning icon
2. **Given** user clicks "Delete All Data", **When** confirmation dialog appears, **Then** message shows: "This will permanently delete [N] uploaded files, [M] generated sections, and vector index. This cannot be undone."
3. **Given** user confirms deletion, **When** process completes, **Then** success message shows: "Deleted [N] files ([X] MB), [M] sections, vector index. All data removed."
4. **Given** deletion is complete, **When** user views UI, **Then** checklist is empty, all sections are cleared, upload screen shows "No documents uploaded"
5. **Given** data is deleted, **When** user checks server storage, **Then** `/data/uploads` and `/vector` directories are empty

---

### Edge Cases

- What happens when uploaded funding call PDF is missing requirements sections? (Show warning: "Could not extract complete requirements. Please verify checklist manually.")
- What happens when supporting documents total >50MB? (Block upload with message: "Total upload size exceeds 50MB limit. Please reduce file count or size.")
- What happens when generation exceeds word limit despite constraints? (Show error: "Generated text exceeded [X] word limit by [N] words. Regenerating..." and auto-retry with stricter limits)
- What happens when no citations are found for a section? (Show warning: "No relevant context found in uploaded documents for this section. Please upload additional materials or write manually.")
- What happens when user edits exceed word limit? (Show red warning: "Word count [X] exceeds limit of [Y]. Please reduce before exporting.")
- What happens when network connection drops during generation? (Show retry dialog: "Connection lost. Retry generation?" with auto-save of draft up to point of failure)
- What happens when user uploads corrupted or password-protected PDF? (Show error: "Could not parse [filename]. Please ensure file is not password-protected.")
- What happens when hosting platform runs out of memory during vector indexing? (Show error: "Upload too large for demo environment. Please reduce to <5 documents or contact support for production deployment.")

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept uploaded funding call PDF and automatically extract requirements into a structured checklist showing: section names, word/character limits, format constraints, scoring criteria, eligibility requirements
- **FR-002**: System MUST accept up to 5 additional supporting documents in PDF, DOCX, or TXT format, with total upload size <50MB
- **FR-003**: System MUST store all uploaded documents server-side only (no client-side storage or API key exposure)
- **FR-004**: System MUST index uploaded documents into a vector store using server-side embedding with 600-token chunks and 15% overlap
- **FR-005**: System MUST retrieve relevant context chunks for each checklist section using semantic similarity search with top-5 retrieval
- **FR-006**: System MUST generate draft sections that include inline citations in format [Document Title, p.N] referencing source document and page number
- **FR-007**: System MUST enforce word/character limits during generation, showing warning if limit is exceeded and auto-retrying with stricter constraints
- **FR-008**: System MUST display sources panel showing all documents referenced in current section with relevance scores
- **FR-009**: System MUST preserve user edits when regenerating sections (sticky edits), updating only AI-generated portions
- **FR-010**: System MUST provide section locking mechanism to prevent further AI modifications after user approval
- **FR-011**: System MUST export completed sections as DOCX file with proper formatting, checklist order, and citations as footnotes
- **FR-012**: System MUST provide one-click data deletion that removes all uploaded files, generated content, and vector indices with confirmation message
- **FR-013**: System MUST display three-panel UI layout: left panel (checklist), center panel (section editor), right panel (sources)
- **FR-014**: System MUST be deployable as single service to Render, Railway, or Hugging Face Spaces with public URL access
- **FR-015**: System MUST load and function without requiring users to provide API keys, credentials, or local setup
- **FR-016**: System MUST use neutral, professional grant language in all generated sections (no promotional or subjective tone)
- **FR-017**: System MUST validate uploaded funding call contains parseable requirements before allowing section generation
- **FR-018**: System MUST show real-time word count indicator during editing (e.g., "487 / 500 words") with visual warning when limit exceeded
- **FR-019**: System MUST auto-save draft sections every 30 seconds to prevent data loss
- **FR-020**: System MUST handle generation errors gracefully with retry options and clear error messages

### Key Entities

- **Funding Call**: Represents uploaded funding opportunity document; attributes include extracted sections, word limits, scoring criteria, eligibility rules, deadline
- **Supporting Document**: Represents uploaded local context file (community plan, budget, prior proposal); attributes include filename, file type, page count, upload timestamp, vector index status
- **Section Requirement**: Individual required section from funding call; attributes include name, word/character limit, format constraints, ordering position, generation status
- **Generated Section**: AI-drafted text for a requirement; attributes include content, citations list, word count, user edits, locked status, generation timestamp
- **Citation**: Reference to source material; attributes include document title, page number, chunk text, relevance score, position in section
- **User Session**: Temporary workspace for a grant writer; attributes include uploaded documents list, checklist state, completed sections, export history; deleted on data deletion request

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Judges can access public demo URL and complete full workflow (upload → checklist → generate → edit → export) in under 5 minutes without setup or credentials
- **SC-002**: System extracts at least 80% of funding call requirements accurately (section names, word limits, criteria) from standard grant RFP formats
- **SC-003**: Generated sections stay within specified word limits on first attempt in 90% of cases; auto-retry succeeds within 3 attempts for remaining 10%
- **SC-004**: Every generated claim includes verifiable citation (document + page) with no uncited assertions or hallucinated facts
- **SC-005**: User edits persist across regeneration in 100% of cases—edited sentences remain character-identical after "Regenerate (keep edits)"
- **SC-006**: Exported DOCX files open cleanly in Microsoft Word 2016+ with proper formatting and readable footnotes
- **SC-007**: Upload and indexing of 5 documents (total ~25MB, ~100 pages) completes in under 60 seconds on free-tier hosting
- **SC-008**: Section generation (retrieval + drafting) completes in under 30 seconds for 500-word section
- **SC-009**: One-click data deletion removes all files and indices within 5 seconds with visible confirmation
- **SC-010**: Demo runs within free-tier constraints: <512MB memory, <1GB storage, supports ≥10 concurrent users

## Assumptions

- Funding calls follow standard grant RFP formats with identifiable section headers, word limits, and evaluation criteria
- Users have basic digital literacy (can upload files, click buttons, edit text)
- Uploaded supporting documents contain relevant local context in English language
- Word limits in funding calls are specified in words (not characters) unless explicitly stated otherwise
- Users access demo via modern web browsers (Chrome, Firefox, Safari, Edge) released within last 2 years
- Hosting platforms provide persistent storage for uploaded files and vector indices during user session
- Users complete workflow within single session (no multi-day drafting with saved state)
- Export format (DOCX) is acceptable for target grant funders (most common submission format)
- Auto-deletion after 30 days (per constitution privacy policy) is acceptable for demo purposes
- Users understand this is a demo/prototype, not production-grade grant management system

## Dependencies

- External: OpenAI API for embeddings (text-embedding-3-small) and generation (GPT-4o, GPT-4o-mini)
- External: Hosting platform with support for Python/FastAPI backend and static file serving for React frontend
- External: PDF parsing capability (PyMuPDF library)
- External: DOCX generation capability (python-docx library)
- Internal: Constitution principles must be validated (local context, requirements-driven, transparency, sticky edits, simplicity, privacy, hostability)
- Internal: `config.yaml` must be configured with model settings, chunking parameters, top-k retrieval before deployment

## Out of Scope

- Multi-user collaboration or team workspaces (single-user demo sessions only)
- User authentication or account management (public access, session-based)
- Saving/loading draft proposals across sessions (no persistent user storage)
- Advanced formatting options beyond basic DOCX structure (headings, paragraphs, footnotes)
- PDF export (DOCX only for MVP)
- Integration with grant portal submission systems (manual file upload by user)
- Support for non-English documents or multilingual generation
- Mobile-responsive UI optimization (desktop browser demo priority)
- Performance tuning beyond basic free-tier compatibility
- Advanced logging, monitoring, or analytics dashboards
- Accessibility (a11y) features (keyboard navigation, screen readers)
- Internationalization (i18n) or localization
