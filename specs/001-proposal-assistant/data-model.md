# Data Model: Smart Proposal Assistant

**Feature**: 001-proposal-assistant  
**Phase**: 1 (Design & Contracts)  
**Date**: 2025-10-26  
**Purpose**: Define entities, relationships, and validation rules from feature requirements

---

## Entity Definitions

### 1. FundingCall

Represents the uploaded funding opportunity document with extracted requirements.

**Attributes**:
- `id` (string, UUID): Unique identifier for this funding call
- `filename` (string): Original filename of uploaded PDF
- `upload_timestamp` (datetime): When the PDF was uploaded
- `file_path` (string): Server path to stored PDF (e.g., `/data/uploads/{session_id}/{filename}`)
- `file_size_bytes` (integer): Size of uploaded file for validation (<10MB per FR-001)
- `total_pages` (integer): Number of pages in PDF
- `extraction_status` (enum): `pending`, `processing`, `completed`, `failed`
- `extracted_at` (datetime, nullable): When requirements extraction completed
- `blueprint` (JSON object): Structured requirements (see Blueprint schema below)

**Validation Rules**:
- `filename` must end with `.pdf`
- `file_size_bytes` ≤ 10,485,760 (10MB)
- `blueprint` must conform to Blueprint schema (see below)

**State Transitions**:
```
pending → processing (on upload complete)
processing → completed (on successful extraction)
processing → failed (on extraction error)
failed → processing (on retry)
```

**Blueprint Schema** (JSON):
```json
{
  "sections": [
    {
      "name": "Community Need Statement",
      "order": 1,
      "word_limit": 500,
      "char_limit": null,
      "format_requirements": "Narrative paragraph",
      "scoring_weight": 20
    }
  ],
  "eligibility_criteria": [
    "Must serve population <5000",
    "Must be registered non-profit"
  ],
  "deadline": "2025-12-31",
  "funding_amount": "$50,000 - $100,000",
  "scoring_criteria": {
    "need": 20,
    "approach": 30,
    "capacity": 25,
    "budget": 25
  }
}
```

---

### 2. SupportingDocument

Represents uploaded local context files (community plans, budgets, prior proposals).

**Attributes**:
- `id` (string, UUID): Unique identifier
- `filename` (string): Original filename
- `file_type` (enum): `pdf`, `docx`, `txt`
- `upload_timestamp` (datetime): When uploaded
- `file_path` (string): Server path (e.g., `/data/uploads/{session_id}/{filename}`)
- `file_size_bytes` (integer): File size for quota validation
- `total_pages` (integer): Number of pages (PDF/DOCX only, null for TXT)
- `extraction_status` (enum): `pending`, `processing`, `completed`, `failed`
- `extracted_text` (text, nullable): Full text content after parsing
- `chunk_count` (integer, nullable): Number of 600-token chunks created
- `indexed_at` (datetime, nullable): When vector indexing completed

**Validation Rules**:
- `file_type` must be one of: `pdf`, `docx`, `txt`
- `file_size_bytes` ≤ 10,485,760 (10MB per file)
- Total of all supporting docs ≤ 52,428,800 (50MB per FR-002)
- Maximum 5 supporting documents per session (FR-002)

**Relationships**:
- Belongs to one `UserSession`
- Has many `DocumentChunk` (via vector store, not direct DB relation)

---

### 3. SectionRequirement

Individual required section extracted from funding call blueprint.

**Attributes**:
- `id` (string, UUID): Unique identifier
- `funding_call_id` (string, FK to FundingCall): Parent funding call
- `name` (string): Section name (e.g., "Community Need Statement")
- `order` (integer): Display order in checklist (1-based)
- `word_limit` (integer, nullable): Maximum words (null if char limit specified)
- `char_limit` (integer, nullable): Maximum characters (null if word limit specified)
- `format_requirements` (text, nullable): Free text format constraints
- `scoring_weight` (integer, nullable): Points out of 100 (null if unspecified)
- `generation_status` (enum): `not_started`, `generating`, `completed`, `failed`

**Validation Rules**:
- At least one of `word_limit` or `char_limit` must be non-null (or both null if no limit)
- `order` must be unique within a `funding_call_id`
- `scoring_weight` must be 0-100 if specified

**Relationships**:
- Belongs to one `FundingCall`
- Has zero or one `GeneratedSection`

---

### 4. GeneratedSection

AI-drafted text for a section requirement, including citations and edit tracking.

**Attributes**:
- `id` (string, UUID): Unique identifier
- `section_requirement_id` (string, FK to SectionRequirement): Parent requirement
- `ai_generated_text` (text): Original AI output (baseline for diff)
- `user_edits` (JSON array): List of edit operations (see Edit schema below)
- `final_text` (text): Merged view (AI text + user edits applied)
- `word_count` (integer): Current word count of `final_text`
- `char_count` (integer): Current character count of `final_text`
- `citations` (JSON array): List of citation objects (see Citation schema below)
- `is_locked` (boolean): If true, exclude from regeneration (FR-010)
- `generated_at` (datetime): Initial generation timestamp
- `last_regenerated_at` (datetime, nullable): Most recent regeneration
- `regeneration_count` (integer): Number of times regenerated

**Validation Rules**:
- `word_count` must match `len(final_text.split())` (computed on save)
- If `section_requirement.word_limit` is set, `word_count` ≤ `word_limit` (warning if exceeded)
- `citations` must be non-empty (FR-006, Constitution III)

**Edit Schema** (JSON array):
```json
[
  {
    "edit_id": "edit_001",
    "timestamp": "2025-10-26T10:30:00Z",
    "start_char": 120,
    "end_char": 150,
    "original_text": "in our rural area",
    "replacement_text": "in our remote mountain community with limited broadband"
  }
]
```

**Citation Schema** (JSON array):
```json
[
  {
    "citation_id": "cite_001",
    "position_in_text": 145,
    "document_id": "doc_uuid_123",
    "document_title": "Strategic Plan 2024",
    "page_number": 5,
    "chunk_text": "...our community lacks reliable internet...",
    "relevance_score": 0.87
  }
]
```

**Relationships**:
- Belongs to one `SectionRequirement`
- References multiple `SupportingDocument` via citations (indirect via document_id)

---

### 5. UserSession

Temporary workspace for a grant writer's demo session.

**Attributes**:
- `session_id` (string, UUID): Unique session identifier
- `created_at` (datetime): Session start time
- `last_activity_at` (datetime): Most recent API call (for auto-cleanup)
- `ip_address` (string, nullable): Client IP (for rate limiting, optional)
- `funding_call_id` (string, FK to FundingCall, nullable): Associated funding call
- `total_upload_size_bytes` (integer): Running total of uploaded file sizes (for 50MB quota)
- `export_count` (integer): Number of DOCX exports (for analytics)

**Validation Rules**:
- `total_upload_size_bytes` ≤ 52,428,800 (50MB per FR-002)
- Supporting document count ≤ 5 (enforced at upload endpoint)

**Relationships**:
- Has zero or one `FundingCall`
- Has zero to many `SupportingDocument` (max 5)
- Has one Chroma collection (named `session_{session_id}`)

**Lifecycle**:
- Created on first API call (or explicitly via `/api/session/create`)
- Updated on every API interaction (`last_activity_at`)
- Deleted on `/api/data` DELETE request (FR-012)
- Auto-deleted after 30 days of inactivity (Constitution VII privacy policy)

---

### 6. DocumentChunk (Vector Store Metadata)

Represents a 600-token chunk stored in Chroma vector store (not a database table).

**Attributes** (stored as Chroma metadata):
- `chunk_id` (string): Unique identifier (format: `{document_id}_chunk_{index}`)
- `document_id` (string): Reference to SupportingDocument UUID
- `document_title` (string): Original filename for citation display
- `page_number` (integer): Page where chunk originates (PDF/DOCX only)
- `chunk_index` (integer): 0-based index within document
- `chunk_text` (string): The 600-token text content (stored as Chroma document)
- `embedding` (vector, 1536 dims): Generated by text-embedding-3-small (stored in Chroma)

**Retrieval**:
- Query via Chroma: `collection.query(query_texts=[section_prompt], n_results=5)`
- Returns top-5 chunks with metadata + relevance scores

---

## Relationships Diagram

```
UserSession (1) ──< (0..1) FundingCall
    │
    └──< (0..5) SupportingDocument ──< (many) DocumentChunk [Chroma]
    
FundingCall (1) ──< (many) SectionRequirement
    
SectionRequirement (1) ──< (0..1) GeneratedSection
    
GeneratedSection ──references──> (many) SupportingDocument [via citations.document_id]
```

---

## Validation Rules Summary

### Upload Limits (FR-002)
- Individual file: ≤10MB
- Total supporting docs: ≤50MB
- Max supporting docs: 5 per session
- Allowed file types: PDF, DOCX, TXT

### Word Limits (FR-007, FR-018)
- `GeneratedSection.word_count` ≤ `SectionRequirement.word_limit` (if specified)
- Warning displayed if exceeded (red indicator in UI)
- Auto-retry with stricter prompt if first generation exceeds by >10%

### Citation Requirements (FR-006, Constitution III)
- Every `GeneratedSection` must have non-empty `citations` array
- Each claim must reference `document_id` + `page_number`
- Quality checker flags uncited assertions as violations

### Session Limits (Constitution VII)
- Session data auto-deleted after 30 days of inactivity
- One-click delete removes: all files in `/data/uploads/{session_id}/`, Chroma collection, session record

---

## State Machines

### FundingCall Extraction
```
[Upload] → pending
  ↓
[Start Extraction] → processing
  ↓
[Success] → completed
  ↓ (on error)
[Retry] → processing
  ↓ (max retries)
[Fail] → failed
```

### SectionRequirement Generation
```
[Initial] → not_started
  ↓
[Generate Click] → generating
  ↓
[Success] → completed
  ↓ (user edits)
[Edit] → completed (regeneration_count++)
  ↓ (lock)
[Lock] → completed (is_locked=true, no further regen)
```

### UserSession Lifecycle
```
[First API Call] → created
  ↓
[Activity] → active (last_activity_at updated)
  ↓
[30 days idle] → auto_deleted
  OR
[Delete All Data] → manually_deleted
```

---

## Computed Fields

These fields are computed at runtime, not stored:

- `SectionRequirement.completion_percentage`: `(word_count / word_limit) * 100` if limit exists
- `GeneratedSection.limit_exceeded`: `word_count > word_limit` (boolean)
- `UserSession.remaining_upload_quota`: `50MB - total_upload_size_bytes`
- `GeneratedSection.citation_count`: `len(citations)`
- `FundingCall.sections_completed`: Count of `SectionRequirement` with `generation_status == completed`

---

## Indexing & Performance

**Database Indexes** (if using SQLite/PostgreSQL for metadata):
- `UserSession.session_id` (primary key, clustered)
- `FundingCall.id` (primary key)
- `SectionRequirement.funding_call_id` (foreign key index)
- `GeneratedSection.section_requirement_id` (foreign key index)
- `SupportingDocument.upload_timestamp` (for cleanup queries)

**Chroma Indexes**:
- HNSW index on embeddings (default, cosine similarity)
- Metadata filter on `document_id`, `page_number` for targeted retrieval

---

## Migration Notes

**Initial Setup**:
1. Create database tables (if using relational DB) or initialize Pydantic models (if in-memory)
2. Create `/data/uploads` and `/vector` directories with proper permissions
3. Initialize Chroma client with persistent path `/vector`

**Schema Evolution**:
- Add `FundingCall.blueprint_version` if blueprint schema changes
- Add `GeneratedSection.quality_score` if QC agent scores implemented
- Add `UserSession.user_agent` for browser analytics (optional)

---

**Phase 1 (Data Model) Complete**: All entities, relationships, and validation rules defined. Proceeding to contracts generation.
