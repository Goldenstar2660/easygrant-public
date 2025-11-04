# Troubleshooting: AI Not Using Supporting Documents

## Problem Description

When generating proposal sections, the AI is outputting generic content (e.g., about "Oakwood") instead of using the actual supporting documents you uploaded (e.g., Pond Inlet information).

---

## Root Causes & Solutions

### Cause 1: Documents Not Indexed ❌

**Symptoms:**
- AI generates generic content
- No citations from your documents
- Logs show "No results found" from retriever

**How to Check:**
Use the new debug endpoint to check if documents are indexed:

```bash
# Check collection stats
curl http://localhost:8000/api/debug/collection-stats/YOUR_SESSION_ID
```

Expected response if working:
```json
{
  "session_id": "abc123",
  "collection_exists": true,
  "collection_count": 42,  // Should be > 0
  "uploaded_files": [...],
  "funding_call_uploaded": true,
  "total_file_count": 3
}
```

**Solution:**
- Make sure you uploaded supporting documents successfully
- Check the upload response - it should show `"indexed": true` and a `chunk_count` > 0
- Look for `[INDEXING]` logs to confirm documents were processed

---

### Cause 2: Session ID Mismatch ❌

**Symptoms:**
- Documents uploaded but retriever finds nothing
- Collection count shows 0 even after upload
- Different session IDs in logs

**How to Check:**
Look in your backend logs for:
```
[SUPPORTING UPLOAD] Session updated - Session ID: abc123
[RETRIEVER] Searching for session: xyz456  // MISMATCH!
```

**Solution:**
- Ensure frontend passes the same session ID for upload AND generation
- Check the session ID in browser localStorage or API calls
- Don't create multiple sessions accidentally

---

### Cause 3: Query Not Matching Content ❌

**Symptoms:**
- Documents are indexed (collection_count > 0)
- But retriever returns no results or low relevance scores
- Wrong documents being retrieved

**How to Check:**
Use the test retrieval endpoint:

```bash
curl -X POST http://localhost:8000/api/debug/test-retrieval \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "query_text": "Pond Inlet community demographics",
    "n_results": 10
  }'
```

This will show you:
- What documents match your query
- Relevance scores
- Text previews of retrieved chunks

**Solution:**
- If relevance scores are low (< 0.3), lower the threshold in `retriever.py`
- Try different query text that matches your document content
- Check if PDF text extraction worked correctly (look for `[INDEXING]` logs)

---

### Cause 4: Relevance Threshold Too High ❌

**Symptoms:**
- Search finds documents but filters them out
- Logs show "Skipping low-relevance result"
- Relevance scores between 0.1-0.3

**Current Setting:**
```python
# In backend/src/agents/retriever.py
retriever = Retriever(top_k=5, min_relevance_score=0.3)
```

**Solution:**
Lower the threshold temporarily to see if documents are being found:

```python
retriever = Retriever(top_k=5, min_relevance_score=0.1)  # Lower threshold
```

Or increase the number of results:

```python
retriever = Retriever(top_k=10, min_relevance_score=0.2)
```

---

### Cause 5: PDF Text Extraction Failed ❌

**Symptoms:**
- Files uploaded successfully
- But chunks are empty or garbled
- Logs show parsing errors

**How to Check:**
Look for `[INDEXING]` logs showing parsed content:
```
[INDEXING] ========== PARSING DOCUMENT FOR INDEXING ==========
[INDEXING] --- Page 1 (0 chars) ---  // EMPTY! Problem!
```

**Solution:**
- Check if PDF is scanned (needs OCR)
- Try a different PDF or DOCX format
- Verify PDF isn't password-protected or corrupted

---

## Diagnostic Steps

### Step 1: Check Logs

Start backend and look for these log sequences when uploading and generating:

**During Upload:**
```
[SUPPORTING UPLOAD] Received request - Session ID: abc123
[INDEXING] ========== PARSING DOCUMENT FOR INDEXING ==========
[INDEXING] Document: Pond_Inlet_Report.pdf
[INDEXING] Total pages parsed: 25
[INDEXING] --- Page 1 (2834 chars) ---  // Should have content!
[INDEXING] ========== CHUNKS TO BE EMBEDDED ==========
[INDEXING] Total chunks created: 42  // Should be > 0!
```

**During Generation:**
```
[RETRIEVER] ========== SEARCH QUERY DETAILS ==========
[RETRIEVER] Session name: Project Description
[RETRIEVER] Combined query: Project Description ...
[VECTOR STORE] Collection has 42 documents  // Should match chunks!
[RETRIEVER] ========== RAW SEARCH RESULTS ==========
[RETRIEVER] Total results from vector DB: 5
[RETRIEVER] Result 1:
[RETRIEVER]   - Document: Pond_Inlet_Report.pdf  // Should be your doc!
[RETRIEVER]   - Relevance: 0.7659  // Should be > 0.3!
```

### Step 2: Use Debug Endpoints

**Test if documents are indexed:**
```bash
GET http://localhost:8000/api/debug/collection-stats/YOUR_SESSION_ID
```

**Test if search works:**
```bash
POST http://localhost:8000/api/debug/test-retrieval
{
  "session_id": "YOUR_SESSION_ID",
  "query_text": "community demographics population",
  "n_results": 10
}
```

### Step 3: Check Frontend Session ID

Open browser console and check:
```javascript
// What session ID is being used?
localStorage.getItem('easygrant_session_id')

// Or check the API call:
// Network tab -> sections/generate -> Request Payload -> session_id
```

### Step 4: Verify Upload Success

When you upload documents, check the response:
```json
{
  "uploaded_count": 2,
  "total_chunks": 85,  // Should be > 0!
  "files": [
    {
      "filename": "Pond_Inlet.pdf",
      "uploaded": true,
      "indexed": true,  // Should be true!
      "chunk_count": 42  // Should be > 0!
    }
  ]
}
```

---

## Quick Fixes

### Fix 1: Lower Relevance Threshold

Edit `backend/src/agents/retriever.py` line ~18:

```python
# Change from:
self.min_relevance_score = min_relevance_score or 0.3

# To:
self.min_relevance_score = min_relevance_score or 0.1  # More permissive
```

### Fix 2: Increase Retrieved Documents

Edit `backend/src/api/routes/sections.py` line ~30:

```python
# Change from:
retriever = Retriever(top_k=5, min_relevance_score=0.3)

# To:
retriever = Retriever(top_k=10, min_relevance_score=0.2)  # Get more results
```

### Fix 3: Add More Context to Search Query

Edit `backend/src/agents/retriever.py` around line 50, modify the query building:

```python
# Add more context to the search
query_parts = [
    f"{section_name}",
    "community",  # Add keywords that match your docs
    "project",
    "demographics"
]
```

---

## Files Modified to Help Debug

1. ✅ `backend/src/services/vector_store.py` - Added `query()` method with logging
2. ✅ `backend/src/api/routes/debug.py` - NEW! Debug endpoints
3. ✅ `backend/src/main.py` - Registered debug router

---

## Testing the Fix

1. **Restart the backend**
   ```bash
   # Kill current backend (Ctrl+C)
   uvicorn backend.src.main:app --reload
   ```

2. **Check debug endpoint is available**
   ```bash
   curl http://localhost:8000/docs
   # Look for /api/debug endpoints
   ```

3. **Upload a test document**
   - Use the UI to upload a PDF about "Pond Inlet"
   - Check the response shows `indexed: true`

4. **Test retrieval directly**
   ```bash
   curl -X POST http://localhost:8000/api/debug/test-retrieval \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "YOUR_SESSION_ID",
       "query_text": "Pond Inlet",
       "n_results": 10
     }'
   ```

5. **Check if it returns your documents**
   - Should show results with relevance > 0
   - Text preview should match your PDF content

6. **Generate a section**
   - Try generating "Project Description"
   - Check logs for `[RETRIEVER]` results
   - Should now use your Pond Inlet content!

---

## Next Steps

1. **Start backend with logging**
2. **Check `/api/debug/collection-stats/{session_id}`** to see if docs are indexed
3. **Use `/api/debug/test-retrieval`** to test search
4. **Review logs** for any errors or mismatches
5. **Adjust relevance threshold** if needed
6. **Share log output** if issue persists

The logging system will now show you exactly what's happening at each step!
