# AI Prompts and Logging Guide

## Overview

This document explains where the AI prompts are located in the codebase, what inputs they receive from PDF documents, and how to access detailed logging to analyze and debug the AI's behavior.

---

## Key AI Prompts Locations

### 1. **Requirements Extraction Prompt** (Funding Call Analysis)

**Location:** `backend/src/agents/requirements_extractor.py` (Lines 220-268)

**Purpose:** Analyzes the funding call PDF to extract:
- Required proposal sections (e.g., "Project Description", "Budget Narrative")
- Word/character limits for each section
- Eligibility requirements
- Scoring criteria
- Application deadline

**Input:** Full text extracted from the funding call PDF

**Model Used:** GPT-4o (configured in `backend/config.yaml` as `requirements_model`)

**Key Prompt Section:**
```python
prompt = f"""You are an expert grant proposal assistant analyzing a funding call document. Your task is to extract the WRITTEN PROPOSAL SECTIONS that applicants must complete.

**CRITICAL INSTRUCTIONS:**
- Extract ONLY sections that require written narrative, descriptions, or text responses
- DO NOT extract supporting documents, attachments, or administrative forms
- Look for sections in tables of contents, proposal format sections, and application instructions
...
```

**How to View:**
- Read the file at lines 220-268
- When running, check logs with tag `[REQUIREMENTS EXTRACTION]`
- Full prompt is logged under `========== COMPLETE GPT-4o PROMPT ==========`

---

### 2. **Section Generation Prompt** (Using Supporting Documents)

**Location:** `backend/src/agents/section_generator.py` (Lines 125-199)

**Purpose:** Generates proposal section text using RAG (Retrieval-Augmented Generation):
- Takes requirements for a specific section
- Uses relevant chunks from uploaded supporting documents (retrieved via vector search)
- Generates compelling, evidence-based content with inline citations

**Input:** 
- Section requirements (from funding call analysis)
- Retrieved context from supporting documents (via semantic search)
- Word/character limits
- Format requirements

**Model Used:** GPT-4o-mini (configured as `drafting_model`)

**Key Prompt Section:**
```python
prompt = f"""You are an expert grant proposal writer...

**SECTION REQUIREMENTS:**
{requirements_str}

**CONTEXT FROM SOURCE DOCUMENTS:**
{context_str}

**CORE WRITING PRINCIPLES:**
1. Specificity Over Generality
2. Evidence-Based Claims
3. Demonstrate Clear Need and Alignment
...
```

**How to View:**
- Read the file at lines 125-199
- Check logs with tag `[SECTION GENERATOR]`
- Full prompt logged under `========== COMPLETE GENERATION PROMPT ==========`

---

## PDF Content Extraction & Processing

### How PDFs are Parsed

**Parser Location:** `backend/src/utils/parser.py`

The system supports both PDF and DOCX files:

1. **PDF Parsing** (using PyMuPDF/fitz):
   - Extracts text page-by-page
   - Preserves page numbers for citations
   - Returns list of page objects with text and metadata

2. **DOCX Parsing** (using python-docx):
   - Extracts paragraphs
   - Estimates page numbers based on character count (3000 chars ≈ 1 page)

**Example Usage:**
```python
from backend.src.utils.parser import extract_text_from_file

full_text, page_data = extract_text_from_file("path/to/document.pdf")
# full_text: Complete concatenated text
# page_data: List of {page_number, text, metadata} dicts
```

### How Documents are Chunked for RAG

**Chunker Location:** `backend/src/utils/chunking.py`

**Settings:** (from `backend/config.yaml`)
- Chunk size: 600 tokens
- Chunk overlap: 90 tokens
- Encoding: `cl100k_base` (GPT-4/GPT-3.5 tokenizer)

**Process:**
1. Parse document into pages
2. Split each page's text into chunks using token-based splitter
3. Preserve metadata: document_id, document_title, page_number, chunk_index
4. Embed chunks using OpenAI embeddings
5. Store in ChromaDB vector database

**Indexing Service:** `backend/src/services/indexing_service.py`

---

## Detailed Logging System

### Logging Locations & Tags

All logs now include detailed information about what content is being extracted from PDFs and what prompts are being sent to AI models.

#### 1. **Requirements Extraction Logs**

**Tag:** `[REQUIREMENTS EXTRACTION]`

**What's Logged:**
- ✅ Full parsed text from funding call PDF
- ✅ Page-by-page breakdown
- ✅ Word limits detected via regex
- ✅ Complete GPT-4o prompt (with full document text)
- ✅ GPT-4o response (structured JSON with extracted sections)
- ✅ Validation results

**Example Log Output:**
```
[REQUIREMENTS EXTRACTION] ========== FULL PARSED PDF TEXT ==========
[REQUIREMENTS EXTRACTION] File: /path/to/funding_call.pdf
[REQUIREMENTS EXTRACTION] Full text (45230 chars):
[Full document text here...]
[REQUIREMENTS EXTRACTION] ========== END FULL PARSED TEXT ==========

[REQUIREMENTS EXTRACTION] ========== PAGE-BY-PAGE BREAKDOWN ==========
[REQUIREMENTS EXTRACTION] --- Page 1 (3421 chars) ---
[Page 1 text...]
[REQUIREMENTS EXTRACTION] ========== END PAGE BREAKDOWN ==========

[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o PROMPT ==========
[REQUIREMENTS EXTRACTION] Model: gpt-4o
[REQUIREMENTS EXTRACTION] Temperature: 0.1
[REQUIREMENTS EXTRACTION] Prompt:
[Full prompt with instructions and document...]
[REQUIREMENTS EXTRACTION] ========== END GPT-4o PROMPT ==========

[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o RESPONSE ==========
[REQUIREMENTS EXTRACTION] Response JSON:
{
  "sections": [...],
  "eligibility": [...],
  ...
}
[REQUIREMENTS EXTRACTION] ========== END GPT-4o RESPONSE ==========
```

---

#### 2. **Document Indexing Logs** (Supporting Documents)

**Tag:** `[INDEXING]`

**What's Logged:**
- ✅ Full parsed content from uploaded supporting documents
- ✅ Page-by-page text extraction
- ✅ Chunks created for embedding (first 10 shown)
- ✅ Chunk metadata (page numbers, lengths)

**Example Log Output:**
```
[INDEXING] ========== PARSING DOCUMENT FOR INDEXING ==========
[INDEXING] Session: abc123
[INDEXING] File: /path/to/support_doc.pdf
[INDEXING] Document Title: Annual Report 2023
[INDEXING] Total pages parsed: 25
[INDEXING] --- Page 1 (2834 chars) ---
[Page 1 text...]
[INDEXING] ========== END PARSED DOCUMENT ==========

[INDEXING] ========== CHUNKS TO BE EMBEDDED ==========
[INDEXING] Document: Annual Report 2023
[INDEXING] Total chunks created: 42
[INDEXING] Chunk 1/42:
[INDEXING]   - Page: 1
[INDEXING]   - Length: 523 chars
[INDEXING]   - Text: [First 300 chars of chunk...]
[INDEXING] ========== END CHUNKS ==========
```

---

#### 3. **Retrieval Logs** (Semantic Search)

**Tag:** `[RETRIEVER]`

**What's Logged:**
- ✅ Search query details (section name, requirements, word limit)
- ✅ Raw search results from vector database
- ✅ Relevance scores (distance → relevance conversion)
- ✅ Document previews for each result
- ✅ Filtering decisions (which results passed threshold)

**Example Log Output:**
```
[RETRIEVER] ========== SEARCH QUERY DETAILS ==========
[RETRIEVER] Section name: Project Description
[RETRIEVER] Section requirements: Describe your project's goals and objectives
[RETRIEVER] Word limit: 500
[RETRIEVER] Combined query: Project Description Describe your project's goals and objectives...
[RETRIEVER] Max results: 5
[RETRIEVER] Min relevance threshold: 0.3
[RETRIEVER] ========== END QUERY DETAILS ==========

[RETRIEVER] ========== RAW SEARCH RESULTS ==========
[RETRIEVER] Total results from vector DB: 5
[RETRIEVER] Result 1:
[RETRIEVER]   - Document: Annual Report 2023
[RETRIEVER]   - Page: 5
[RETRIEVER]   - Distance: 0.2341, Relevance: 0.7659
[RETRIEVER]   - Text preview: Our organization has been serving...
[RETRIEVER] ========== END RAW RESULTS ==========
```

---

#### 4. **Section Generation Logs**

**Tag:** `[SECTION GENERATOR]`

**What's Logged:**
- ✅ Retrieved citations details (document, page, relevance, text preview)
- ✅ Complete generation prompt (with all context)
- ✅ Model and temperature settings
- ✅ GPT-4o-mini response (generated text)
- ✅ Word count and citation usage

**Example Log Output:**
```
[SECTION GENERATOR] ========== RETRIEVED CITATIONS DETAILS ==========
[SECTION GENERATOR] Citation 1:
[SECTION GENERATOR]   - Document: Annual Report 2023
[SECTION GENERATOR]   - Page: 5
[SECTION GENERATOR]   - Relevance: 0.7659
[SECTION GENERATOR]   - Text: Our organization has served 5,000 families...
[SECTION GENERATOR] ========== END CITATIONS DETAILS ==========

[SECTION GENERATOR] ========== COMPLETE GENERATION PROMPT ==========
[SECTION GENERATOR] Model: gpt-4o-mini
[SECTION GENERATOR] Temperature: 0.7
[SECTION GENERATOR] Prompt (8423 chars):
You are an expert grant proposal writer...
[Full prompt with context and instructions...]
[SECTION GENERATOR] ========== END GENERATION PROMPT ==========

[SECTION GENERATOR] ========== GPT-4o-mini RESPONSE ==========
[SECTION GENERATOR] Generated text (523 chars):
[Full generated section text...]
[SECTION GENERATOR] ========== END RESPONSE ==========
```

---

## How to Access Logs

### Prerequisites

**Logging is now configured!** The backend has been set up with Python's logging system that will display all the detailed logs described in this document.

### Running the Application

1. **Start the backend** (logs will appear in terminal):
   ```powershell
   cd C:\Users\hello\Documents\Projects\EasyGrant
   .\scripts\start-backend.ps1
   ```
   
   Or manually:
   ```powershell
   uvicorn backend.src.main:app --reload
   ```

2. **Look for startup confirmation** - You should see:
   ```
   ================================================================================
   EasyGrant Smart Proposal Assistant - Starting Up
   Detailed logging enabled for AI prompts and PDF parsing
   ================================================================================
   ...
   ================================================================================
   FastAPI application started successfully
   📊 LOGGING ENABLED FOR:
     • [REQUIREMENTS EXTRACTION] - Funding call analysis
     • [SECTION GENERATOR] - Proposal section generation
     • [RETRIEVER] - Semantic search results
     • [INDEXING] - Document parsing and chunking
   ================================================================================
   ```

3. **Upload a funding call PDF** via the web interface

4. **Upload supporting documents** 

5. **Generate proposal sections**

6. **Watch terminal output** - all detailed logs will appear with the tags described above

### If You Don't See Logs

If the terminal shows no detailed logs when you use the app, check:

1. **Is logging configured?** - Check that `backend/src/main.py` has the logging setup (it should now!)
2. **Is the backend running?** - Make sure uvicorn is actively running
3. **Did you trigger an action?** - Logs only appear when you upload PDFs or generate sections
4. **Check log level** - It should be set to `logging.INFO` in `main.py`

### Configuring Log Levels

Python's logging is configured in `backend/src/main.py`. To adjust verbosity:

```python
import logging

# For maximum detail (shows all INFO level logs)
logging.basicConfig(level=logging.INFO)

# For debugging (shows DEBUG level logs too)
logging.basicConfig(level=logging.DEBUG)

# For production (shows only WARNING and ERROR)
logging.basicConfig(level=logging.WARNING)
```

### Saving Logs to File

To save logs to a file for later analysis:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('easygrant_debug.log'),
        logging.StreamHandler()  # Also print to console
    ]
)
```

Or use shell redirection:
```powershell
uvicorn backend.src.main:app --reload 2>&1 | Tee-Object -FilePath "logs.txt"
```

---

## Common Debugging Scenarios

### Scenario 1: "The AI isn't extracting all sections from my funding call"

**What to check:**
1. Look for `[REQUIREMENTS EXTRACTION] ========== FULL PARSED PDF TEXT ==========`
   - Is the full text being extracted correctly?
   - Are sections visible in the parsed text?
   
2. Look for `[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o PROMPT ==========`
   - Does the prompt include the sections you expect?
   
3. Look for `[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o RESPONSE ==========`
   - What sections did GPT-4o extract?
   - Compare with the original document

**Possible fixes:**
- If text is truncated (>80,000 chars), important sections might be cut off
- Adjust the prompt in `requirements_extractor.py` to be more specific about section patterns
- Check if sections are labeled as "attachments" vs "written sections"

---

### Scenario 2: "Generated sections don't use my uploaded documents"

**What to check:**
1. Look for `[INDEXING] ========== PARSING DOCUMENT FOR INDEXING ==========`
   - Is the document being parsed correctly?
   - Are chunks being created?

2. Look for `[RETRIEVER] ========== RAW SEARCH RESULTS ==========`
   - Are relevant chunks being found?
   - What are the relevance scores?
   - Is the query matching your document content?

3. Look for `[SECTION GENERATOR] ========== RETRIEVED CITATIONS DETAILS ==========`
   - What citations are being passed to the generator?
   
**Possible fixes:**
- Lower the `min_relevance_score` in `retriever.py` (currently 0.3)
- Increase `top_k` to retrieve more results
- Improve document quality (clearer text, better OCR if scanned)
- Adjust chunk size in `config.yaml` if text is too fragmented

---

### Scenario 3: "The prompt isn't giving good results"

**What to check:**
1. Look for the complete prompt in logs (`========== COMPLETE ... PROMPT ==========`)
2. Copy the prompt to a text file
3. Test it manually in ChatGPT or OpenAI Playground with the same model

**Possible fixes:**
- Modify the prompt in `section_generator.py` (lines 125-199)
- Adjust the temperature setting in `config.yaml`
- Add more specific instructions or examples
- Change the system message or tone requirements

---

## Model Configuration

All model settings are in `backend/config.yaml`:

```yaml
llm:
  requirements_model: "gpt-4o"          # For funding call analysis
  requirements_temperature: 0.1         # Low = more deterministic
  
  drafting_model: "gpt-4o-mini"         # For section generation
  drafting_temperature: 0.7             # Higher = more creative
  
  quality_model: "gpt-4o"               # For quality checks (future)
  quality_temperature: 0.0              # Very deterministic
```

---

## Summary of Changes Made

### Files Modified to Add Logging:

1. ✅ `backend/src/agents/requirements_extractor.py`
   - Added full PDF text logging
   - Added page-by-page breakdown logging
   - Added complete GPT-4o prompt logging
   - Added complete GPT-4o response logging

2. ✅ `backend/src/agents/section_generator.py`
   - Added citation details logging
   - Added complete generation prompt logging
   - Added GPT-4o-mini response logging

3. ✅ `backend/src/agents/retriever.py`
   - Added search query details logging
   - Added raw search results logging with relevance scores

4. ✅ `backend/src/services/indexing_service.py`
   - Added parsed document content logging
   - Added chunk creation logging

### No Changes Required:
- `backend/src/utils/parser.py` - Already functional, logging added at service level
- `backend/src/utils/chunking.py` - Token counting, logging at service level
- `backend/src/services/llm_client.py` - Client wrapper, logging in calling code

---

## Next Steps

1. **Run the application** and observe logs
2. **Analyze prompts** - if results aren't good, modify the prompts in the identified locations
3. **Adjust retrieval settings** - if citations are poor, tune `top_k` and `min_relevance_score`
4. **Fine-tune chunking** - if context is fragmented, adjust chunk_size in config
5. **Experiment with temperatures** - higher = creative, lower = deterministic

For questions or issues, refer to this guide and the detailed logs!
