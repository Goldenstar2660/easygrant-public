# Phase 6 Testing Guide - Quick Start

## Prerequisites

Before testing Phase 6, ensure:

1. ✅ **Backend is running**: 
   ```powershell
   cd C:\Users\hello\Documents\Projects\EasyGrant
   uvicorn backend.src.main:app --reload
   ```
   Verify: http://localhost:8000/health should return `{"status": "ok"}`

2. ✅ **Frontend is running**:
   ```powershell
   cd C:\Users\hello\Documents\Projects\EasyGrant\frontend
   npm run dev
   ```
   Verify: Should open browser to http://localhost:5173

3. ✅ **Phases 1-5 working**:
   - Can upload funding call PDF
   - Requirements extracted to checklist
   - Can generate sections with citations
   - Sources panel shows retrieved chunks

---

## 5-Minute Smoke Test

This quick test validates core Phase 6 functionality:

### Step 1: Generate a Section (30 seconds)

1. Open http://localhost:5173
2. Upload a funding call PDF (or use existing session)
3. Wait for requirements extraction
4. Click "Generate" on any section (e.g., "Project Description")
5. Wait for generation to complete

**✓ Expected**: Section appears with text, citations, and word count

### Step 2: View Paragraph Controls (15 seconds)

1. Scroll down below the textarea
2. Look for "🔒 Paragraph Controls" section
3. Verify you see a list of paragraphs with:
   - ¶1, ¶2, ¶3, etc. labels
   - Text preview (first 80 characters)
   - "🔓 Lock" buttons

**✓ Expected**: All paragraphs listed, no locked paragraphs initially

### Step 3: Lock a Paragraph (30 seconds)

1. Click "🔓 Lock" on the **second paragraph** (¶2)
2. Observe changes:
   - Button changes to "🔒 Locked"
   - Paragraph background turns yellow
   - Regenerate button shows "(🔒 1)"

**✓ Expected**: Visual feedback confirms lock

### Step 4: Regenerate with Lock (2 minutes)

1. Note the original text of paragraph 2 (copy it somewhere)
2. Click "🔄 Regenerate (🔒 1)" button
3. Wait for "⏳ Regenerating..." to complete
4. Compare new text:
   - Paragraph 2 should be **identical** to original
   - Other paragraphs should be **different**

**✓ Expected**: Locked paragraph unchanged, others regenerated

### Step 5: Verify Persistence (30 seconds)

1. Switch to a different section in the checklist
2. Switch back to the section you just regenerated
3. Check that paragraph 2 is still locked (yellow background)
4. Check that lock count still shows on regenerate button

**✓ Expected**: Lock persists across navigation

---

## If Smoke Test Fails

### Issue: Paragraph Controls Don't Appear

**Check**:
- Is there generated text? (Controls only show if text exists)
- Are there paragraphs? (Text must have `\n\n` separators)
- Check browser console for errors

**Fix**: Regenerate the section to ensure proper paragraph structure

### Issue: Lock Button Doesn't Work

**Check**:
- Browser console for PATCH request errors
- Backend logs for endpoint errors
- Network tab: Look for `/api/sections/{session_id}/{section_name}` PATCH

**Fix**: 
- Restart backend server
- Check backend logs: `uvicorn backend.src.main:app --reload`

### Issue: Regenerate Doesn't Preserve Locks

**Check**:
- Backend logs for "Regenerating with X locked paragraphs"
- Verify `locked_paragraphs_data` exists in backend
- Check merge logic in `paragraph_lock.py`

**Fix**:
- Verify `merge_paragraphs_with_locks()` function exists
- Check that POST regenerate endpoint calls merge function

### Issue: UI Looks Broken

**Check**:
- CSS file loaded? (Check Network tab)
- React component state? (Use React DevTools)
- Browser console for CSS errors

**Fix**:
- Hard refresh: Ctrl+Shift+R
- Clear browser cache
- Rebuild frontend: `npm run build`

---

## Full Test Suite

For comprehensive testing, see `TESTING_PHASE6.md` which includes:

- ✅ Test 1: Basic Paragraph Locking
- ✅ Test 2: Multiple Paragraph Locking  
- ✅ Test 3: Regeneration with Locked Paragraphs
- ✅ Test 4: Lock Persistence Across Section Switches
- ✅ Test 5: Editing Text Doesn't Break Locks
- ✅ Test 6: Regenerate Button States
- ✅ Test 7: Empty Section Handling
- ✅ Test 8: API Error Handling
- ✅ Test 9: Word Count After Regeneration
- ✅ Test 10: Integration Test - Full Workflow

Each test includes:
- Objective
- Step-by-step instructions
- Expected results
- Cleanup steps

---

## Manual API Testing (Optional)

If you want to test the backend endpoints directly:

### Test PATCH Endpoint

```powershell
# Lock paragraphs 0 and 2
Invoke-WebRequest -Uri "http://localhost:8000/api/sections/your-session-id/Project%20Description" `
  -Method PATCH `
  -ContentType "application/json" `
  -Body '{"text": "Para 1\n\nPara 2\n\nPara 3", "locked_paragraph_indices": [0, 2]}'
```

**Expected**: Response includes `"locked_paragraphs": [0, 2]`

### Test POST Regenerate Endpoint

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/sections/your-session-id/Project%20Description/regenerate" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"section_requirements": "Write about the project", "word_limit": 500, "format_type": "narrative"}'
```

**Expected**: Response includes merged text with locked paragraphs preserved

---

## Performance Benchmarks

Expected performance for Phase 6 operations:

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Lock paragraph | <200ms | PATCH request to backend |
| Unlock paragraph | <200ms | PATCH request to backend |
| Regenerate (no locks) | 10-30s | Depends on GPT-4o-mini response time |
| Regenerate (with locks) | 10-30s | Merge adds <50ms overhead |
| Load section with locks | <500ms | GET request includes lock data |
| Render paragraph list | <100ms | Client-side React render |

If operations are slower, check:
- Network latency
- OpenAI API response time
- Backend CPU usage
- ChromaDB query performance

---

## Success Criteria Summary

Phase 6 is **PASSING** if:

1. ✅ Paragraphs can be locked via UI
2. ✅ Locked paragraphs have yellow background
3. ✅ Regenerate button shows lock count
4. ✅ Regeneration preserves locked paragraphs
5. ✅ Unlocked paragraphs are regenerated
6. ✅ Locks persist across navigation
7. ✅ Word count updates correctly
8. ✅ No console errors during normal use
9. ✅ PATCH and POST endpoints return 200
10. ✅ Backend logs show merge operation

---

## Next Steps After Testing

Once Phase 6 passes all tests:

1. **Document any bugs** in GitHub Issues
2. **Update tasks.md** to mark complete
3. **Proceed to Phase 7**: DOCX export with locked paragraphs
4. **Consider improvements**:
   - Auto-save locks on textarea blur
   - Visual diff showing what changed
   - Highlight locked paragraphs in textarea (not just in list)

---

## Getting Help

If you encounter issues not covered here:

1. Check `TESTING_PHASE6.md` for detailed test procedures
2. Check `PHASE6_QUICKREF.md` for architecture details
3. Check backend logs: Look for `[SECTIONS API]` messages
4. Check browser console: Look for `[EditorPanel]` messages
5. Use React DevTools to inspect component state

---

## Test Results Template

```
Phase 6 Testing - 5-Minute Smoke Test
=====================================
Date: _______________
Tester: _______________

[ ] Step 1: Generate a Section - PASS / FAIL
[ ] Step 2: View Paragraph Controls - PASS / FAIL  
[ ] Step 3: Lock a Paragraph - PASS / FAIL
[ ] Step 4: Regenerate with Lock - PASS / FAIL
[ ] Step 5: Verify Persistence - PASS / FAIL

Overall: PASS / FAIL

Issues Found:
_____________________________________
_____________________________________
_____________________________________

Notes:
_____________________________________
_____________________________________
_____________________________________
```

---

**Ready to test?** Start with the 5-Minute Smoke Test above! 🚀
