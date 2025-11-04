# Phase 6: Paragraph Locking & Regeneration - Testing Procedure

**Feature**: Simple Edit + Regenerate with Paragraph Locking  
**Date**: 2025-10-26  
**Status**: ✅ Implementation Complete

---

## Overview

Phase 6 implements paragraph-level locking that allows users to preserve specific paragraphs during section regeneration. This is a simpler alternative to complex sentence-level diff/merge engines while still providing 80% of the value.

---

## Components Implemented

### Backend

1. **`backend/src/utils/paragraph_lock.py`** - NEW
   - Utilities for splitting text into paragraphs
   - Finding paragraphs at cursor positions
   - Merging locked paragraphs with new text
   - Word counting

2. **`backend/src/api/routes/sections.py`** - UPDATED
   - Added `UpdateSectionRequest` model
   - Added `RegenerateSectionRequest` model
   - Added PATCH `/{session_id}/{section_name}` endpoint
   - Added POST `/{session_id}/{section_name}/regenerate` endpoint
   - Imports paragraph_lock utilities

3. **`backend/src/models/section.py`** - EXISTING
   - Already had `LockedParagraph` model
   - Already had paragraph lock/unlock methods
   - Already had merge logic

### Frontend

1. **`frontend/src/components/EditorPanel.jsx`** - UPDATED
   - Added `lockedParagraphs` state
   - Added `selectedParagraph` state
   - Added `isRegenerating` state
   - Added `splitIntoParagraphs()` function
   - Added `handleParagraphClick()` function
   - Added `handleLockParagraph()` function
   - Added `handleRegenerate()` function (separate from generate)
   - Added paragraph controls UI with lock buttons
   - Updated regenerate button with lock count indicator

2. **`frontend/src/components/EditorPanel.css`** - UPDATED
   - Added styles for `.paragraph-controls`
   - Added styles for `.paragraph-list`
   - Added styles for `.paragraph-item` (normal, selected, locked states)
   - Added styles for `.lock-button`
   - Added styles for `.lock-count`

---

## Testing Procedure

### Pre-requisites

1. **Backend running**: `uvicorn backend.src.main:app --reload`
2. **Frontend running**: `npm run dev` (in frontend directory)
3. **Session with funding call uploaded and requirements extracted**
4. **At least one section generated** (e.g., "Project Description")

---

### Test 1: Basic Paragraph Locking

**Objective**: Verify that paragraphs can be locked and unlocked

**Steps**:
1. Navigate to a generated section in the Editor Panel
2. Scroll to the "🔒 Paragraph Controls" section below the textarea
3. Observe that all paragraphs are listed with:
   - Paragraph number (¶1, ¶2, etc.)
   - Text preview (first 80 characters)
   - "🔓 Lock" button
4. Click "🔓 Lock" on the first paragraph
5. Verify:
   - Button changes to "🔒 Locked"
   - Paragraph item gets yellow background
   - Regenerate button shows "(🔒 1)" badge

**Expected Result**:
- ✅ Paragraph is visually marked as locked
- ✅ Lock count appears on regenerate button
- ✅ Backend PATCH request succeeds (check browser console)

**Cleanup**: Unlock the paragraph by clicking "🔒 Locked" again

---

### Test 2: Multiple Paragraph Locking

**Objective**: Verify that multiple paragraphs can be locked simultaneously

**Steps**:
1. In a section with at least 3 paragraphs
2. Lock paragraphs 1 and 3 (leave paragraph 2 unlocked)
3. Verify regenerate button shows "(🔒 2)"
4. Check that both locked paragraphs have yellow background
5. Unlock paragraph 1
6. Verify regenerate button shows "(🔒 1)"

**Expected Result**:
- ✅ Multiple paragraphs can be locked
- ✅ Lock count updates correctly
- ✅ Individual paragraphs can be unlocked

---

### Test 3: Regeneration with Locked Paragraphs

**Objective**: Verify that locked paragraphs are preserved during regeneration

**Steps**:
1. Generate a section (any section with word limit)
2. Note the original text of paragraph 2
3. Lock paragraph 2 (click "🔓 Lock" on ¶2)
4. Click the "🔄 Regenerate" button
5. Wait for regeneration to complete
6. Compare the new text:
   - Check if paragraph 2 is **identical** to original
   - Check if paragraphs 1, 3, 4, etc. are **different** (regenerated)

**Expected Result**:
- ✅ Locked paragraph 2 remains unchanged
- ✅ Unlocked paragraphs are regenerated
- ✅ Citations may be updated in unlocked paragraphs
- ✅ Word count updates based on merged text
- ✅ No errors in console

**Edge Case**: If new AI text has fewer paragraphs than locked indices, locked paragraphs should still appear at their original positions.

---

### Test 4: Lock Persistence Across Section Switches

**Objective**: Verify that locks are saved and restored when switching sections

**Steps**:
1. Generate section "Project Description"
2. Lock paragraph 1
3. Verify lock indicator appears
4. Switch to another section (e.g., "Proposed community involvement")
5. Switch back to "Project Description"
6. Verify paragraph 1 is still locked (yellow background, "🔒 Locked" button)

**Expected Result**:
- ✅ Locked paragraphs persist across navigation
- ✅ Lock state is loaded from backend GET endpoint
- ✅ Lock count appears immediately when section loads

---

### Test 5: Editing Text Doesn't Break Locks

**Objective**: Verify that editing the textarea maintains paragraph structure

**Steps**:
1. Generate a section with 3 paragraphs
2. Lock paragraph 2
3. Edit the textarea: Change a word in paragraph 1
4. Click away or wait a moment
5. Regenerate the section
6. Verify paragraph 2 still contains the original locked text

**Expected Result**:
- ✅ Manual edits are preserved
- ✅ Locked paragraph text is saved with edits
- ✅ Regeneration uses the edited+locked version

**Note**: The current implementation saves locks when the lock button is clicked. If you edit text and then regenerate without re-locking, the old locked text will be used. This is expected behavior for MVP.

---

### Test 6: Regenerate Button States

**Objective**: Verify button states during operations

**Steps**:
1. With a generated section open:
   - Verify "🔄 Regenerate" button is enabled
2. Lock 2 paragraphs
   - Verify button text includes "(🔒 2)"
3. Hover over the regenerate button
   - Verify tooltip says "Regenerate (keeps 2 locked paragraphs)"
4. Click "🔄 Regenerate"
   - Verify button changes to "⏳ Regenerating..."
   - Verify button is disabled during regeneration
5. Wait for completion
   - Verify button returns to "🔄 Regenerate"
   - Verify lock count still shows if paragraphs remain locked

**Expected Result**:
- ✅ Button states are clear and informative
- ✅ User can't click regenerate while already regenerating
- ✅ Tooltip provides helpful context

---

### Test 7: Empty Section Handling

**Objective**: Verify that paragraph controls don't crash with no text

**Steps**:
1. Navigate to a section that hasn't been generated yet
2. Verify "Paragraph Controls" section doesn't appear
3. Click "✨ Generate"
4. After generation, verify "Paragraph Controls" appears
5. Try to lock a paragraph
6. Clear all text from textarea (select all, delete)
7. Verify paragraph controls update or hide appropriately

**Expected Result**:
- ✅ No errors when section is empty
- ✅ Paragraph controls appear/disappear based on content
- ✅ No crash when text is cleared

---

### Test 8: API Error Handling

**Objective**: Verify graceful degradation on backend errors

**Steps**:
1. Stop the backend server
2. Try to lock a paragraph
3. Check browser console for error message
4. Restart backend
5. Try to regenerate
6. Verify operation succeeds

**Expected Result**:
- ✅ Frontend doesn't crash on failed PATCH
- ✅ Console shows error message
- ✅ User can still interact with UI
- ✅ Operation succeeds when backend is back online

---

### Test 9: Word Count After Regeneration

**Objective**: Verify word count updates correctly with locked paragraphs

**Steps**:
1. Generate a section with 500 word limit
2. Note original word count (e.g., 485 words)
3. Lock paragraph 1 (which might be 150 words)
4. Regenerate
5. Check new word count
6. Manually count words in locked vs. unlocked paragraphs
7. Verify total matches displayed word count

**Expected Result**:
- ✅ Word count is accurate for merged text
- ✅ Warning shows if merged text exceeds limit
- ✅ Locked paragraph word count is included in total

---

### Test 10: Integration Test - Full Workflow

**Objective**: Test complete paragraph locking workflow end-to-end

**Steps**:
1. Upload funding call and supporting documents
2. Extract requirements
3. Generate "Project Description" section
4. Review generated text (e.g., 4 paragraphs, 450 words)
5. Edit paragraph 2 manually (change a sentence)
6. Lock paragraph 2 and paragraph 4
7. Click "🔄 Regenerate"
8. Verify:
   - Paragraphs 1 and 3 have new content
   - Paragraph 2 has your manual edit
   - Paragraph 4 is unchanged from original
   - Citations are updated where relevant
   - Word count is updated
9. Switch to another section
10. Come back to "Project Description"
11. Verify locks are still active
12. Unlock paragraph 4
13. Regenerate again
14. Verify paragraph 4 now regenerates but paragraph 2 still locked

**Expected Result**:
- ✅ Complete workflow functions smoothly
- ✅ User can iteratively refine content
- ✅ Locks persist and are respected
- ✅ No data loss or corruption

---

## Known Limitations (By Design)

1. **Paragraph Splitting**: Uses double-newline (`\n\n`) as separator. Single newlines within paragraphs are preserved.

2. **Lock Granularity**: Paragraph-level only, not sentence-level. This is intentional for MVP simplicity.

3. **Manual Edit Sync**: If you edit the textarea and don't re-lock, the old locked text version will be used during regeneration. User should re-lock after manual edits.

4. **Index Stability**: If you delete paragraphs manually in the textarea, indices may become misaligned. Best practice is to lock first, then regenerate (don't delete content manually).

5. **No Undo**: Regeneration is immediate and irreversible (except via browser back button, which won't work for this SPA). User should be careful before regenerating.

---

## Success Criteria

Phase 6 is considered **successfully implemented** if:

- ✅ All 10 tests pass
- ✅ Locked paragraphs survive regeneration unchanged
- ✅ Unlocked paragraphs are regenerated with new content
- ✅ UI clearly shows which paragraphs are locked
- ✅ Lock state persists in backend and across navigation
- ✅ No console errors during normal operation
- ✅ Word counts are accurate after merging
- ✅ Regenerate button shows lock count indicator

---

## Debugging Tips

### If locks don't persist:
- Check browser console for PATCH request errors
- Verify `_generated_sections` storage in backend logs
- Check that `locked_paragraphs` array is returned in GET endpoint

### If regeneration ignores locks:
- Check backend logs for "Regenerating with X locked paragraphs"
- Verify `merge_paragraphs_with_locks()` is being called
- Check that `locked_paragraphs_data` exists in section storage

### If paragraph list is empty:
- Verify text contains `\n\n` separators
- Check `splitIntoParagraphs()` function
- Ensure generated text is not empty

### If UI is broken:
- Check EditorPanel.css is loaded
- Verify React component state updates
- Check browser console for JS errors

---

## Next Steps

After Phase 6 testing is complete:

1. **Phase 7**: Export DOCX with preserved locked paragraphs
2. **Phase 8**: Demo mode with pre-locked sample sections
3. **Phase 10**: End-to-end testing with real funding calls

---

**Testing Completed By**: _____________  
**Date**: _____________  
**Status**: [ ] PASS [ ] FAIL  
**Issues Found**: _____________
