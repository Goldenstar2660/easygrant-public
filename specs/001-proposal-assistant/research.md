# Research & Technical Decisions: Smart Proposal Assistant

**Feature**: 001-proposal-assistant  
**Phase**: 0 (Outline & Research)  
**Date**: 2025-10-26  
**Purpose**: Resolve technical unknowns and document architectural decisions

## Research Tasks Completed

### 1. Docker Deployment Strategy for Render/Railway/Hugging Face Spaces

**Question**: How to structure Dockerfile for single-service deployment with FastAPI backend + React frontend?

**Decision**: Multi-stage Dockerfile with production mode serving static frontend via FastAPI

**Rationale**:
- **Stage 1 (Frontend Build)**: Use `node:18-alpine` to run `npm install && npm run build` → produces `/dist` static bundle
- **Stage 2 (Backend)**: Use `python:3.11-slim`, copy frontend `/dist` to `/app/static`, mount via `StaticFiles` in FastAPI
- **Single Port Exposure**: Backend listens on :8000, serves API routes at `/api/*` and static files at `/*`
- **Volume Mounts**: `/data/uploads` and `/vector` persist across container restarts on hosting platforms

**Alternatives Considered**:
- ❌ Separate containers (frontend + backend): Requires orchestration (docker-compose/k8s), violates "single service" requirement
- ❌ Vite dev server in production: Not recommended, adds unnecessary overhead, FastAPI can serve static files efficiently
- ✅ **Selected**: Multi-stage build with FastAPI serving static bundle—simplest for demo deployment, single URL, no CORS issues

**Implementation Notes**:
```dockerfile
# Stage 1: Build frontend
FROM node:18-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend + static files
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/src ./src
COPY --from=frontend /frontend/dist ./static
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 2. Chunking Strategy for RAG (600 tokens, 15% overlap)

**Question**: How to implement 600-token chunks with 15% overlap for text-embedding-3-small?

**Decision**: Use `langchain.text_splitter.RecursiveCharacterTextSplitter` with token counting via `tiktoken`

**Rationale**:
- **Token Counting**: `tiktoken` library (OpenAI's official tokenizer) ensures accurate token counts for `cl100k_base` encoding (used by text-embedding-3-small)
- **Chunk Size**: 600 tokens ≈ 450 words ≈ 2400 characters (avg 4 chars/token)
- **Overlap**: 15% of 600 = 90 tokens ensures context continuity across chunk boundaries
- **Recursive Splitting**: LangChain's recursive splitter preserves semantic units (paragraphs, sentences) better than fixed-length splitting

**Alternatives Considered**:
- ❌ Fixed character splitting: Breaks mid-sentence, poor semantic coherence
- ❌ Sentence-based splitting: Variable chunk sizes, hard to enforce 600-token limit
- ✅ **Selected**: RecursiveCharacterTextSplitter with tiktoken—industry standard, balances semantic coherence with size constraints

**Implementation Notes**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=90,
    length_function=lambda text: len(encoding.encode(text)),
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_text(document_text)
```

---

### 3. Chroma Vector Store Configuration (Server-Side, Persistent)

**Question**: How to configure Chroma for server-side persistence with Docker volume mounts?

**Decision**: Use `chromadb.PersistentClient` with `/vector` directory path, ephemeral session-based collections

**Rationale**:
- **Persistence**: `PersistentClient(path="/vector")` writes index to disk, survives container restarts when `/vector` is volume-mounted
- **Collection Per Session**: Create collection with session ID as name (e.g., `session_abc123`), delete on "Delete All Data" action
- **No Authentication**: Demo mode—no multi-user isolation needed, single collection per session sufficient
- **Embedding Function**: Pass OpenAI embedding function wrapper to ensure consistent embedding model

**Alternatives Considered**:
- ❌ Chroma server (HTTP mode): Adds complexity (separate process), overkill for demo with single backend instance
- ❌ In-memory only: Loses index on container restart, poor UX for demos with volume mounts available
- ✅ **Selected**: PersistentClient with session-based collections—simple, persistent, easy cleanup

**Implementation Notes**:
```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="/vector",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name=f"session_{session_id}",
    metadata={"session_id": session_id}
)

# On delete:
client.delete_collection(name=f"session_{session_id}")
```

---

### 4. Requirements Extraction (Regex + GPT-4o Hybrid Approach)

**Question**: How to reliably extract section names, word limits, and scoring criteria from funding call PDFs?

**Decision**: Two-pass extraction: (1) PyMuPDF text + regex for headings/limits, (2) GPT-4o structured output for JSON blueprint

**Rationale**:
- **Pass 1 (Regex)**: Extract section headings via patterns like `"Section [A-Z0-9]+:"`, word limits via `"maximum \d+ words"`, page numbers
- **Pass 2 (GPT-4o)**: Send extracted text + regex hints to GPT-4o with JSON schema for structured output (sections, limits, eligibility, scoring)
- **Hybrid Accuracy**: Regex catches explicit patterns, LLM handles variations/context ("not to exceed 500 words" vs "500-word limit")
- **Fallback**: If regex finds no limits, GPT-4o infers from context or marks as "unspecified"

**Alternatives Considered**:
- ❌ Regex only: Brittle, fails on non-standard formats ("two pages" vs "500 words")
- ❌ GPT-4o only: Expensive, slower, may miss explicit numbers buried in text
- ✅ **Selected**: Regex + GPT-4o hybrid—cost-effective, robust to format variations

**Implementation Notes**:
```python
import re
import fitz  # PyMuPDF

# Pass 1: Extract text + regex hints
pdf = fitz.open(pdf_path)
text = "\n".join([page.get_text() for page in pdf])
sections = re.findall(r"Section [A-Z0-9]+:(.+?)(?=Section|$)", text, re.DOTALL)
word_limits = re.findall(r"maximum (\d+) words?", text, re.IGNORECASE)

# Pass 2: GPT-4o structured output
prompt = f"Extract requirements from this funding call:\n{text}\nHints: sections={sections}, limits={word_limits}"
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"}
)
blueprint = json.loads(response.choices[0].message.content)
```

---

### 5. Sticky Edits Implementation (Diff-Based Merge)

**Question**: How to preserve user edits when regenerating sections with new context?

**Decision**: Store original AI text + user edits separately; compute diff on regeneration; merge preserved edits into new AI output

**Rationale**:
- **Storage**: `Section` model has `ai_generated_text` (original), `user_edits` (list of {start, end, replacement}), `final_text` (merged view)
- **Edit Detection**: On user edit, compute character-level diff between `final_text` and new user input, store as edit record
- **Regeneration**: Generate new AI text, apply stored `user_edits` by character offset, produce new `final_text`
- **Conflict Handling**: If user edit overlaps with changed AI region, prefer user edit (user is domain expert per Constitution IV)

**Alternatives Considered**:
- ❌ Replace entire section: Loses all user work, violates Constitution IV
- ❌ Block regeneration if edited: Prevents iterative refinement, poor UX
- ✅ **Selected**: Diff-based merge with user edit priority—respects user expertise, enables iteration

**Implementation Notes**:
```python
from difflib import SequenceMatcher

def detect_edits(original: str, edited: str) -> list:
    matcher = SequenceMatcher(None, original, edited)
    edits = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('replace', 'delete', 'insert'):
            edits.append({"start": i1, "end": i2, "replacement": edited[j1:j2]})
    return edits

def apply_edits(ai_text: str, edits: list) -> str:
    result = ai_text
    for edit in sorted(edits, key=lambda e: e['start'], reverse=True):
        result = result[:edit['start']] + edit['replacement'] + result[edit['end']:]
    return result
```

---

### 6. Word Limit Enforcement (Prompt + Post-Processing)

**Question**: How to ensure generated sections stay within specified word limits?

**Decision**: Three-tier enforcement: (1) Include limit in prompt, (2) Post-generation validation, (3) Auto-retry with stricter prompt if exceeded

**Rationale**:
- **Tier 1 (Prompt)**: Explicitly state word limit in system message: "Generate exactly {limit} words, maximum {limit + 10}"
- **Tier 2 (Validation)**: Count words after generation using `len(text.split())`, check against limit
- **Tier 3 (Retry)**: If exceeded by <10%, truncate at sentence boundary; if >10%, regenerate with stricter prompt ("CRITICAL: Hard limit {limit} words")
- **Success Rate**: Targeting 90% first-attempt compliance per SC-003

**Alternatives Considered**:
- ❌ Truncate blindly: Cuts mid-sentence, poor quality
- ❌ No enforcement: Violates Constitution II (requirements-driven), causes auto-rejection
- ✅ **Selected**: Prompt + validate + retry—balances quality with compliance

**Implementation Notes**:
```python
def generate_with_limit(prompt: str, limit: int, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        strictness = "CRITICAL: " if attempt > 0 else ""
        full_prompt = f"{strictness}Generate {limit} words maximum.\n\n{prompt}"
        text = llm.generate(full_prompt)
        word_count = len(text.split())
        
        if word_count <= limit:
            return text
        elif word_count <= limit * 1.1:  # <10% over
            return truncate_at_sentence(text, limit)
        # else retry with stricter prompt
    
    raise Exception(f"Failed to meet word limit after {max_retries} attempts")
```

---

### 7. Citation Format & Extraction

**Question**: How to generate inline citations [Document Title, p.N] from retrieved chunks?

**Decision**: Retriever returns chunks with metadata (doc_id, page_num); generator inserts citations after each claim using metadata lookup

**Rationale**:
- **Chunk Metadata**: Chroma stores each chunk with `{"document_id": "doc123", "page": 5, "title": "Strategic Plan 2024"}`
- **Citation Insertion**: Prompt instructs LLM to mark claims with placeholder `[CITE:chunk_id]`, post-process replaces with `[Strategic Plan 2024, p.5]`
- **Sources Panel**: Aggregate all cited chunks, deduplicate by document, show relevance scores
- **Verification**: Every claim has citation per Constitution III; QC agent flags uncited assertions

**Alternatives Considered**:
- ❌ Let LLM generate citations: Hallucinates page numbers, unreliable
- ❌ Footnotes only: Harder to track provenance while reading, inline citations more transparent
- ✅ **Selected**: Metadata-driven citation insertion—accurate, verifiable, transparent

**Implementation Notes**:
```python
def insert_citations(text: str, chunks: list) -> str:
    for i, chunk in enumerate(chunks):
        placeholder = f"[CITE:{i}]"
        citation = f"[{chunk['metadata']['title']}, p.{chunk['metadata']['page']}]"
        text = text.replace(placeholder, citation)
    return text

# In generation prompt:
"After each factual claim, insert [CITE:N] where N is the chunk index (0-based) supporting that claim."
```

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend Framework | FastAPI | 0.104+ | Async support, auto OpenAPI docs, production-ready |
| Frontend Framework | React | 18+ | Component-based, wide adoption, good for three-panel layout |
| Build Tool | Vite | 5+ | Fast HMR, simple config, optimized production builds |
| Vector Store | Chroma | 0.4+ | Lightweight, embeddable, persistent, no separate server needed |
| Embeddings | text-embedding-3-small | - | Cost-effective, 1536 dims, good for grant domain |
| LLM (Requirements) | GPT-4o | - | Structured output, high accuracy for complex extraction |
| LLM (Drafting) | GPT-4o-mini | - | Cost-effective, sufficient quality for grant writing |
| PDF Parsing | PyMuPDF (fitz) | 1.23+ | Fast, reliable text extraction, page-level metadata |
| DOCX Export | python-docx | 1.1+ | Industry standard, supports formatting + footnotes |
| Text Splitting | LangChain | 0.1+ | RecursiveCharacterTextSplitter with token counting |
| Token Counting | tiktoken | 0.5+ | OpenAI official tokenizer, accurate for embeddings |
| Containerization | Docker | 24+ | Multi-stage builds, volume mounts, platform-agnostic |

---

## Best Practices Applied

### FastAPI
- Async route handlers for file upload/generation (non-blocking I/O)
- Pydantic models for request/response validation
- CORS middleware for local dev (frontend :5173 → backend :8000)
- Static file serving via `StaticFiles` for production bundle
- OpenAPI auto-documentation at `/docs`

### React + Vite
- Functional components with hooks (useState, useEffect)
- Axios/fetch for API calls with error handling
- Component separation: UploadPanel, ChecklistPanel, EditorPanel, SourcesPanel
- Vite proxy for dev (avoid CORS): `proxy: { '/api': 'http://localhost:8000' }`

### Chroma
- Session-based collections for multi-user isolation
- Persistent storage with volume mounts
- Distance function: cosine similarity (default for embeddings)
- Metadata filtering for page-level retrieval

### OpenAI APIs
- Retry logic with exponential backoff (rate limits)
- Token counting before API calls (avoid exceeding limits)
- Streaming responses for long generations (better UX)
- Cost optimization: GPT-4o-mini for drafting (10x cheaper than GPT-4o)

### Docker
- Multi-stage build to minimize image size (frontend build artifacts only)
- Non-root user for security
- Health checks for container orchestration
- Environment variables for API keys (not hardcoded)

---

## Dependencies & Integration Patterns

### External Dependencies
- **OpenAI API**: Requires `OPENAI_API_KEY` env var; retry on rate limits; monitor token usage
- **Hosting Platform**: Render/Railway/HF Spaces must support Docker, volume mounts, env vars
- **Client Browsers**: Modern browsers (Chrome/Firefox/Safari/Edge) with ES2022+ support

### Internal Dependencies
- `config.yaml` must exist with valid model names, chunking params before backend starts
- Prompt templates in `/prompts/*.txt` must be present for agent initialization
- Frontend build artifacts in `/static` required for production mode

### Integration Patterns
- **Frontend → Backend**: REST API over HTTP, JSON payloads, file uploads via multipart/form-data
- **Backend → OpenAI**: Official Python SDK, async clients, structured output for requirements
- **Backend → Chroma**: Embedded client (no HTTP), direct Python API calls
- **Backend → Filesystem**: Local disk for `/data/uploads`, garbage collection on delete

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| OpenAI API rate limits during demo | High (blocks generation) | Medium | Implement retry with exponential backoff; use GPT-4o-mini for drafting to reduce token usage |
| Free-tier memory limits on hosting | High (container OOM kills) | Medium | Limit upload to 5 docs <50MB; chunk processing in batches; monitor memory usage |
| PDF parsing failures (scanned images) | Medium (no extraction) | Low | Show clear error: "PDF appears to be scanned. Please upload text-based PDFs." |
| Word limit exceeded despite retries | Medium (section invalid) | Low | Allow manual editing; show warning; QC agent flags for user review |
| Sticky edits merge conflicts | Low (poor UX) | Low | Always prefer user edits; provide "Discard edits" option to reset to AI baseline |
| Deployment platform downtime | High (demo unavailable) | Low | Test on multiple platforms (Render + Railway); provide fallback URL |

---

**Phase 0 Complete**: All technical unknowns resolved. Proceeding to Phase 1 (Design & Contracts).
