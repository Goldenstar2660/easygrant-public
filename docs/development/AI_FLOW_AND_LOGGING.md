# EasyGrant AI Flow & Logging Summary

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EasyGrant AI Pipeline                        │
└─────────────────────────────────────────────────────────────────────┘

PHASE 1: FUNDING CALL ANALYSIS
┌──────────────────┐
│ Upload Funding   │
│ Call PDF         │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Parse PDF → Extract Full Text                          │
│ File: backend/src/utils/parser.py                      │
│ Log: [REQUIREMENTS EXTRACTION] FULL PARSED PDF TEXT    │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Analyze with GPT-4o                                     │
│ File: backend/src/agents/requirements_extractor.py      │
│ Lines: 220-268 (prompt)                                 │
│ Log: [REQUIREMENTS EXTRACTION] COMPLETE GPT-4o PROMPT   │
│                                                          │
│ Extract:                                                 │
│ • Proposal sections (e.g., "Project Description")       │
│ • Word/char limits                                       │
│ • Eligibility requirements                              │
│ • Scoring criteria                                       │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Return Structured Blueprint                             │
│ Log: [REQUIREMENTS EXTRACTION] COMPLETE GPT-4o RESPONSE │
└─────────────────────────────────────────────────────────┘


PHASE 2: SUPPORT DOCUMENTS INDEXING
┌──────────────────┐
│ Upload Support   │
│ Documents (PDFs) │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Parse Each PDF → Extract Text by Page                  │
│ File: backend/src/utils/parser.py                      │
│ Log: [INDEXING] PARSING DOCUMENT FOR INDEXING          │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Chunk Text (600 tokens, 90 overlap)                    │
│ File: backend/src/utils/chunking.py                    │
│ Service: backend/src/services/indexing_service.py      │
│ Log: [INDEXING] CHUNKS TO BE EMBEDDED                  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Embed + Store in ChromaDB                              │
│ • OpenAI text-embedding-ada-002                        │
│ • Metadata: doc_id, title, page_number, chunk_index   │
└─────────────────────────────────────────────────────────┘


PHASE 3: SECTION GENERATION
┌──────────────────┐
│ User Requests    │
│ Section (e.g.,   │
│ "Project Desc")  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Semantic Search in Vector DB                           │
│ File: backend/src/agents/retriever.py                  │
│ Log: [RETRIEVER] SEARCH QUERY DETAILS                  │
│ Log: [RETRIEVER] RAW SEARCH RESULTS                    │
│                                                          │
│ Query: Section name + requirements                      │
│ Returns: Top-k chunks (default 5) with relevance scores│
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Filter by Relevance (min 0.3)                          │
│ Format as Citations with Metadata                       │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Generate Section with GPT-4o-mini                       │
│ File: backend/src/agents/section_generator.py          │
│ Lines: 125-199 (prompt)                                 │
│ Log: [SECTION GENERATOR] RETRIEVED CITATIONS DETAILS   │
│ Log: [SECTION GENERATOR] COMPLETE GENERATION PROMPT    │
│                                                          │
│ Input:                                                   │
│ • Section requirements (from funding call)              │
│ • Retrieved context (from support docs)                │
│ • Writing principles & guidelines                       │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Return Generated Text with Inline Citations            │
│ Log: [SECTION GENERATOR] GPT-4o-mini RESPONSE          │
│                                                          │
│ Example: "Our organization has served 5,000 families   │
│ since 2020 [Annual Report 2023, p.12]."                │
└─────────────────────────────────────────────────────────┘
```

---

## Key Files & Their Roles

| File | Purpose | Key Lines | AI Model |
|------|---------|-----------|----------|
| `backend/src/agents/requirements_extractor.py` | Parse funding call, extract sections | 220-268 (prompt) | GPT-4o |
| `backend/src/agents/section_generator.py` | Generate proposal sections | 125-199 (prompt) | GPT-4o-mini |
| `backend/src/agents/retriever.py` | Semantic search for context | 35-105 (search logic) | OpenAI Embeddings |
| `backend/src/utils/parser.py` | PDF/DOCX text extraction | Full file | PyMuPDF/python-docx |
| `backend/src/utils/chunking.py` | Token-based text splitting | Full file | tiktoken |
| `backend/src/services/indexing_service.py` | Orchestrate parse→chunk→embed→store | Full file | - |
| `backend/src/services/llm_client.py` | OpenAI API wrapper | Full file | - |

---

## Logging Tags Reference

| Tag | What It Shows | Where to Find |
|-----|---------------|---------------|
| `[REQUIREMENTS EXTRACTION]` | Funding call parsing & analysis | `requirements_extractor.py` |
| `[SECTION GENERATOR]` | Proposal text generation | `section_generator.py` |
| `[RETRIEVER]` | Semantic search & results | `retriever.py` |
| `[INDEXING]` | Document chunking & embedding | `indexing_service.py` |

---

## Important Log Sections

### 📄 See What Was Read from PDF
```
[REQUIREMENTS EXTRACTION] ========== FULL PARSED PDF TEXT ==========
[INDEXING] ========== PARSING DOCUMENT FOR INDEXING ==========
```

### 🤖 See What Prompt Was Sent to AI
```
[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o PROMPT ==========
[SECTION GENERATOR] ========== COMPLETE GENERATION PROMPT ==========
```

### 💬 See What AI Responded
```
[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o RESPONSE ==========
[SECTION GENERATOR] ========== GPT-4o-mini RESPONSE ==========
```

### 🔍 See What Context Was Retrieved
```
[RETRIEVER] ========== RAW SEARCH RESULTS ==========
[SECTION GENERATOR] ========== RETRIEVED CITATIONS DETAILS ==========
```

---

## Models Used

| Task | Model | Temperature | Why |
|------|-------|-------------|-----|
| Funding call analysis | GPT-4o | 0.1 | Need precision for structured extraction |
| Section generation | GPT-4o-mini | 0.7 | Balance creativity and cost |
| Quality review (future) | GPT-4o | 0.0 | Maximum consistency |
| Embeddings | text-embedding-ada-002 | N/A | Semantic search |

---

## Quick Start: See Your Data

1. **Start backend:**
   ```powershell
   cd C:\Users\hello\Documents\Projects\EasyGrant
   .\scripts\start-backend.ps1
   ```

2. **Upload a funding call PDF** through the web UI

3. **Watch terminal output** - you'll see:
   - `========== FULL PARSED PDF TEXT ==========`
   - `========== COMPLETE GPT-4o PROMPT ==========`
   - `========== COMPLETE GPT-4o RESPONSE ==========`

4. **Upload supporting documents**

5. **Watch terminal** for:
   - `========== PARSING DOCUMENT FOR INDEXING ==========`
   - `========== CHUNKS TO BE EMBEDDED ==========`

6. **Generate a section**

7. **Watch terminal** for:
   - `========== RAW SEARCH RESULTS ==========`
   - `========== RETRIEVED CITATIONS DETAILS ==========`
   - `========== COMPLETE GENERATION PROMPT ==========`
   - `========== GPT-4o-mini RESPONSE ==========`

---

## Files Modified for Enhanced Logging

✅ `backend/src/agents/requirements_extractor.py` - Added 4 detailed log sections
✅ `backend/src/agents/section_generator.py` - Added 3 detailed log sections  
✅ `backend/src/agents/retriever.py` - Added 2 detailed log sections
✅ `backend/src/services/indexing_service.py` - Added 2 detailed log sections

📚 Documentation created:
- `docs/guides/AI_PROMPTS_AND_LOGGING.md` (comprehensive guide)
- `PROMPTS_QUICK_REFERENCE.md` (quick lookup)
- `AI_FLOW_AND_LOGGING.md` (this file - visual overview)
