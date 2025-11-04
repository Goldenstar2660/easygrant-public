# AI Prompts Quick Reference

## 🎯 Quick Locations

### Prompts That Analyze Funding Calls
- **File:** `backend/src/agents/requirements_extractor.py`
- **Lines:** 220-268
- **Model:** GPT-4o
- **Purpose:** Extract sections, word limits, eligibility from funding call PDF
- **Log Tag:** `[REQUIREMENTS EXTRACTION]`

### Prompts That Generate Proposal Text
- **File:** `backend/src/agents/section_generator.py`
- **Lines:** 125-199
- **Model:** GPT-4o-mini
- **Purpose:** Generate proposal sections using supporting documents
- **Log Tag:** `[SECTION GENERATOR]`

---

## 📊 What Gets Logged Now

### Full PDF Content
```
[REQUIREMENTS EXTRACTION] ========== FULL PARSED PDF TEXT ==========
[Shows complete text extracted from funding call]
```

### Complete Prompts Sent to AI
```
[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o PROMPT ==========
[Shows entire prompt with instructions and document content]

[SECTION GENERATOR] ========== COMPLETE GENERATION PROMPT ==========
[Shows prompt with context from supporting documents]
```

### AI Responses
```
[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o RESPONSE ==========
[Shows structured JSON with extracted sections]

[SECTION GENERATOR] ========== GPT-4o-mini RESPONSE ==========
[Shows generated proposal text]
```

### Document Chunks (RAG)
```
[INDEXING] ========== CHUNKS TO BE EMBEDDED ==========
[Shows text chunks from supporting documents]

[RETRIEVER] ========== RAW SEARCH RESULTS ==========
[Shows retrieved chunks with relevance scores]
```

---

## 🔧 How to View Logs

1. Start backend: `.\scripts\start-backend.ps1` (or `uvicorn backend.src.main:app --reload`)
2. **Look for startup message** showing logging is enabled:
   ```
   📊 LOGGING ENABLED FOR:
     • [REQUIREMENTS EXTRACTION] - Funding call analysis
     • [SECTION GENERATOR] - Proposal section generation
     • [RETRIEVER] - Semantic search results
     • [INDEXING] - Document parsing and chunking
   ```
3. Use the app to upload PDFs and generate sections
4. Watch the terminal - all prompts and content will be logged
5. Search for tags like `[REQUIREMENTS EXTRACTION]` or `[SECTION GENERATOR]`

**Note:** Logging is configured in `backend/src/main.py` - it's already set up and ready to use!

---

## 📝 How to Modify Prompts

### To Change Funding Call Analysis:
1. Open `backend/src/agents/requirements_extractor.py`
2. Find the prompt starting at line 220
3. Edit the instructions, examples, or format
4. Restart backend to test changes

### To Change Section Generation:
1. Open `backend/src/agents/section_generator.py`
2. Find the prompt starting at line 125
3. Edit the writing principles, tone, or structure
4. Restart backend to test changes

---

## 🎛️ Configuration Settings

**File:** `backend/config.yaml`

```yaml
llm:
  requirements_model: "gpt-4o"          # Model for funding call analysis
  requirements_temperature: 0.1         # 0.0-1.0 (lower = more consistent)
  
  drafting_model: "gpt-4o-mini"         # Model for section generation
  drafting_temperature: 0.7             # 0.0-1.0 (higher = more creative)

embeddings:
  chunk_size: 600                       # Tokens per chunk
  chunk_overlap: 90                     # Overlap between chunks
```

---

## 🐛 Common Issues

| Issue | What to Check in Logs | Fix |
|-------|----------------------|-----|
| Missing sections from funding call | `FULL PARSED PDF TEXT` - is text extracted? | Improve PDF quality or adjust prompt |
| Not using uploaded docs | `RAW SEARCH RESULTS` - are chunks found? | Lower `min_relevance_score` in `retriever.py` |
| Poor quality output | `COMPLETE GENERATION PROMPT` - is context good? | Adjust prompt or retrieval settings |
| Text too generic | Check citations in `RETRIEVED CITATIONS DETAILS` | Upload better source docs or tune search |

---

## 📚 Full Documentation

For detailed information, see:
- **Complete Guide:** `docs/guides/AI_PROMPTS_AND_LOGGING.md`
- **Architecture:** `specs/001-proposal-assistant/spec.md`
- **Testing:** `specs/001-proposal-assistant/TESTING_PHASE6.md`
