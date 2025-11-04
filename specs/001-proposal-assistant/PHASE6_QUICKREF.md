# Phase 6 Implementation - Quick Reference

## What Was Implemented

Phase 6 adds **paragraph-level locking** to allow users to preserve specific paragraphs when regenerating sections. This provides a simple but effective way to iteratively refine AI-generated content.

---

## Architecture

### Backend Flow

```
User clicks "Lock" 
  ↓
Frontend PATCH /api/sections/{session_id}/{section_name}
  ↓
Backend splits text into paragraphs
  ↓
Stores locked indices and text in _generated_sections
  ↓
Returns updated section data

User clicks "Regenerate"
  ↓
Frontend POST /api/sections/{session_id}/{section_name}/regenerate
  ↓
Backend retrieves context via RAG
  ↓
Generates new section with GPT-4o-mini
  ↓
Merges new paragraphs with locked paragraphs using merge_paragraphs_with_locks()
  ↓
Returns merged section
```

### Frontend State

```jsx
const [lockedParagraphs, setLockedParagraphs] = useState([]);  // Array of indices
const [selectedParagraph, setSelectedParagraph] = useState(null);  // Current selection
const [isRegenerating, setIsRegenerating] = useState(false);  // Loading state
```

---

## API Endpoints

### PATCH `/api/sections/{session_id}/{section_name}`

**Purpose**: Save edited text and lock/unlock paragraphs

**Request Body**:
```json
{
  "text": "Full section text...",
  "locked_paragraph_indices": [0, 2, 4]
}
```

**Response**: `GeneratedSectionResponse` with updated `locked_paragraphs` array

### POST `/api/sections/{session_id}/{section_name}/regenerate`

**Purpose**: Regenerate section while preserving locked paragraphs

**Request Body**:
```json
{
  "section_requirements": "Write a narrative section...",
  "word_limit": 500,
  "char_limit": null,
  "format_type": "narrative"
}
```

**Response**: `GeneratedSectionResponse` with merged text

---

## Key Functions

### Backend (`paragraph_lock.py`)

```python
split_into_paragraphs(text: str) -> List[str]
# Splits on \n\n, filters empty strings

merge_paragraphs_with_locks(
    new_text: str,
    locked_paragraphs: List[Tuple[int, str]]
) -> str
# Replaces unlocked paragraphs with new AI text

count_words(text: str) -> int
# Accurate word counting
```

### Frontend (`EditorPanel.jsx`)

```jsx
splitIntoParagraphs(text)
// Splits text into paragraph array

handleLockParagraph(index)
// Toggles lock state and saves to backend

handleRegenerate()
// Calls regenerate endpoint, updates state

extractCitationsFromText()
// Finds citations in merged text
```

---

## Data Storage

### In-Memory Backend Storage

```python
_generated_sections = {
    "session-id-123": {
        "Project Description": {
            "section_id": "uuid...",
            "text": "Merged text...",
            "locked_paragraphs": [1, 3],  # Indices only
            "locked_paragraphs_data": [   # Full data
                {"index": 1, "text": "Locked para 1..."},
                {"index": 3, "text": "Locked para 3..."}
            ],
            "citations": [...],
            "word_count": 485,
            # ...
        }
    }
}
```

**Note**: `locked_paragraphs` is sent to frontend, `locked_paragraphs_data` is used for merging.

---

## UI Components

### Paragraph Controls Section

```
🔒 Paragraph Controls
────────────────────────────────────────
Lock paragraphs to preserve them during 
regeneration. Locked paragraphs will have 
a yellow background.

┌─────────────────────────────────────┐
│ ¶1  The project aims to empower...  │ 🔓 Lock    │
│ ¶2  We will establish community... │ 🔒 Locked │
│ ¶3  The budget allocation is...    │ 🔓 Lock    │
└─────────────────────────────────────┘
```

**States**:
- Default: White background, "🔓 Lock" button
- Locked: Yellow background (`#fffbf0`), "🔒 Locked" button
- Selected: Blue background (`#e3f2fd`), blue border

### Regenerate Button

```
🔄 Regenerate (🔒 2)
```

**Tooltip**: "Regenerate (keeps 2 locked paragraphs)"

**States**:
- Enabled: When text exists and not generating
- Disabled: During generation/regeneration
- Loading: "⏳ Regenerating..."

---

## CSS Classes

| Class | Purpose |
|-------|---------|
| `.paragraph-controls` | Container for lock UI |
| `.paragraph-list` | Scrollable list of paragraphs |
| `.paragraph-item` | Individual paragraph row |
| `.paragraph-item.locked` | Locked state (yellow) |
| `.paragraph-item.selected` | Selected state (blue) |
| `.lock-button` | Lock/unlock button |
| `.lock-button.locked` | Locked state (orange) |
| `.lock-count` | Badge on regenerate button |

---

## Integration Points

### With Phase 5 (Generation)

- Uses same `retriever.retrieve_for_section()` for RAG
- Uses same `section_generator.generate_section()` for drafting
- Adds merge step after generation

### With Phase 7 (Export)

- Locked paragraphs should be included in DOCX export
- Export uses final merged text (locked + regenerated)

### With Phase 8 (Demo)

- Demo data can pre-lock specific paragraphs
- Shows off iterative refinement workflow

---

## Testing Checklist

- [ ] Lock single paragraph → regenerate → verify preserved
- [ ] Lock multiple paragraphs → verify all preserved
- [ ] Unlock paragraph → verify it regenerates
- [ ] Switch sections → verify locks persist
- [ ] Edit text → lock → regenerate → verify edited version used
- [ ] Regenerate button shows lock count
- [ ] Tooltip shows number of locked paragraphs
- [ ] Word count accurate after merge
- [ ] No console errors

---

## Common Issues & Solutions

### Issue: Locks don't persist after refresh

**Cause**: In-memory storage only  
**Solution**: Phase 6 uses in-memory storage. This is acceptable for MVP. For production, add database persistence.

### Issue: Paragraph indices misalign after manual edit

**Cause**: User deleted/added paragraphs manually  
**Solution**: Use "Lock" button after any manual edits to resync indices.

### Issue: Regenerate merges incorrectly

**Cause**: Locked paragraph data missing  
**Solution**: Verify `locked_paragraphs_data` exists in backend storage. Check PATCH endpoint saves full text.

### Issue: UI doesn't update after lock

**Cause**: State not refreshing  
**Solution**: Ensure `setLockedParagraphs()` is called after PATCH succeeds.

---

## Future Enhancements (Post-MVP)

1. **Sentence-level locking**: More granular control
2. **Visual diff**: Show what changed in regeneration
3. **Undo/redo**: Multi-step history
4. **Auto-save locks**: Save on textarea blur
5. **Drag-to-reorder**: Reorganize paragraph order
6. **Lock by selection**: Select text in textarea to lock
7. **Compare versions**: Side-by-side before/after
8. **Persistent storage**: Database instead of in-memory

---

## Code Locations

### Backend
- `backend/src/utils/paragraph_lock.py` - NEW
- `backend/src/api/routes/sections.py` - Lines 68-80, 238-449 UPDATED
- `backend/src/models/section.py` - Lines 11-27, 97-248 EXISTING

### Frontend
- `frontend/src/components/EditorPanel.jsx` - Lines 1-400 UPDATED
- `frontend/src/components/EditorPanel.css` - Lines 150-290 UPDATED

### Documentation
- `specs/001-proposal-assistant/tasks.md` - Phase 6 section UPDATED
- `specs/001-proposal-assistant/TESTING_PHASE6.md` - NEW

---

## Dependencies

**Backend**:
- No new dependencies (uses existing FastAPI, Pydantic)

**Frontend**:
- No new dependencies (uses existing React hooks)

**Compatible with**:
- Phase 5 (generation with citations)
- Phase 7 (DOCX export)
- Phase 8 (demo mode)

---

## Performance Notes

- **Paragraph splitting**: O(n) where n is text length
- **Lock lookup**: O(m) where m is number of locked paragraphs (typically < 10)
- **Merge operation**: O(p) where p is number of paragraphs (typically < 20)
- **Network**: 2 requests (PATCH to lock, POST to regenerate)

All operations are fast enough for interactive use (<100ms typically).

---

## Security Considerations

- **Input validation**: Paragraph indices validated against actual paragraph count
- **XSS prevention**: Text is escaped in React (automatic)
- **Session validation**: All endpoints check session exists
- **No injection risk**: No SQL, uses in-memory storage

---

## Accessibility

- **Keyboard navigation**: Tab through lock buttons
- **Screen readers**: Buttons have descriptive labels
- **Color contrast**: Yellow/orange locks meet WCAG AA
- **Focus states**: Clear visual feedback on button focus

---

**Questions?** See `TESTING_PHASE6.md` for detailed testing procedures.
