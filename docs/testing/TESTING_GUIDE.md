# Quick Start: Testing Phase 5

## Prerequisites

1. **Backend Running**
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. **Frontend Running**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Environment Variables**
   - Create `backend/.env` with your OpenAI API key:
     ```
     OPENAI_API_KEY=your-key-here
     ```

## Test Workflow

### Step 1: Upload Documents

1. Open `http://localhost:5173` in your browser
2. Click **"Choose Funding Call"** and upload a grant funding call PDF
3. Wait for processing (~5-10 seconds)
4. Click **"Choose Supporting Documents"** and upload research PDFs, past proposals, etc.
5. Wait for indexing (~10-20 seconds depending on document size)

### Step 2: View Requirements

1. After funding call upload, the **ChecklistPanel** appears on the left
2. You should see:
   - Eligibility requirements (if any)
   - List of required sections (e.g., "Project Description", "Budget Narrative")
   - Optional sections (if any)
   - Word limits for each section
   - Scoring weights (if applicable)

### Step 3: Generate a Section

1. Find a section in the ChecklistPanel (e.g., "Project Description")
2. Click the **"Generate"** button
3. The section is selected and appears in the **EditorPanel** (center)
4. Watch the generation process (~10-30 seconds):
   - Button shows "Generating..."
   - Backend logs show: [RETRIEVER] → [SECTION GENERATOR] → [SECTIONS API]
5. When complete:
   - Generated text appears in EditorPanel
   - Inline citations appear as blue clickable spans: `[Document, p.N]`
   - Word count displays at top (color-coded: green/yellow/red)
   - Citations list in **SourcesPanel** (right)

### Step 4: Explore Citations

**Option A: Click Inline Citation**
1. In the EditorPanel rendered text, click any blue `[Document, p.N]` citation
2. Popup modal appears showing:
   - Document title
   - Page number
   - Relevance score
   - Text snippet from document
3. Corresponding citation card highlights in SourcesPanel

**Option B: Click Citation in SourcesPanel**
1. In the SourcesPanel, click any citation card
2. Same popup modal appears
3. Citation is highlighted in the panel

### Step 5: Edit Text

1. Scroll to the **"Edit:"** section in EditorPanel
2. Modify the text in the textarea
3. Word count updates in real-time
4. Color changes if you exceed limits:
   - **Green**: Under 90% of limit
   - **Yellow**: 90-100% of limit
   - **Red**: Over 100% of limit (with pulse animation)

### Step 6: Regenerate (Coming in Phase 6)

1. Click **"Regenerate"** button (currently available but basic)
2. New text generated (will merge locked paragraphs in Phase 6)
3. Citations updated

## Expected Output

### Console Logs (Backend)

```
[RETRIEVER] Building query for section: Project Description
[RETRIEVER] Searching ChromaDB with query: "Project Description requirements for 500 word section"
[RETRIEVER] Found 5 chunks with relevance >= 0.3
[RETRIEVER] Formatting 5 citations for prompt context

[SECTION GENERATOR] Generating section: Project Description
[SECTION GENERATOR] Building generation prompt with 5 citations
[SECTION GENERATOR] Prompt length: 2456 characters
[SECTION GENERATOR] Calling GPT-4o-mini for generation
[SECTION GENERATOR] Generated 487 words with 3 citations used

[SECTIONS API] POST /api/sections/generate received for session: abc-123, section: Project Description
[SECTIONS API] Retrieved 5 citations from knowledge base
[SECTIONS API] Generated 487 words with 3 citations
[SECTIONS API] Storing generated section in memory
[SECTIONS API] Generation complete for Project Description
```

### Console Logs (Frontend)

```
[App] Funding call uploaded, setting fundingCallUploaded to true
[ChecklistPanel] Requirements loaded successfully
[ChecklistPanel] Fetching requirements and summary...
[EditorPanel] Section selected: Project Description
[EditorPanel] Generating section: Project Description
[EditorPanel] Generated 487 words with 3 citations
```

### Sample Generated Text

```
The proposed project aims to improve access to clean water in remote northern communities.
Research shows that 34% of remote communities lack reliable water infrastructure [Community
Health Report 2023, p.12]. This initiative will install filtration systems and provide training
to local operators.

The project aligns with federal priorities for Indigenous infrastructure [Northern Infrastructure
Strategy, p.45]. Our team has successfully completed similar projects in 8 communities over the
past 5 years [Past Proposals Compilation, p.23].
```

### Sample Citations in SourcesPanel

```
#1  [85% relevant]
Community Health Report 2023
Page 12
"A 2023 survey found that 34% of remote northern communities reported
unreliable access to clean drinking water, with infrastructure aging
beyond operational lifespan..."

#2  [72% relevant]
Northern Infrastructure Strategy
Page 45
"Priority investments include water treatment facilities, renewable
energy systems, and digital connectivity for remote and Indigenous
communities across the northern territories..."

#3  [68% relevant]
Past Proposals Compilation
Page 23
"Our organization has delivered 8 successful water infrastructure projects
since 2018, serving communities ranging from 200 to 1,500 residents..."
```

## Troubleshooting

### No Funding Call Document Uploaded
- **Error**: "No funding call uploaded. Please upload a funding call PDF first."
- **Fix**: Upload the funding call PDF in UploadPanel first

### No Supporting Documents
- **Error**: "No documents found in knowledge base"
- **Fix**: Upload supporting documents (research, past proposals, etc.)

### Generation Fails
- **Check**: Backend logs for errors
- **Common issues**:
  * ChromaDB collection not found → Upload documents
  * OpenAI API key missing → Set in `.env`
  * Session expired → Re-upload funding call

### Citations Not Clickable
- **Check**: Are citations in `[Document, p.N]` format?
- **Check**: Browser console for JavaScript errors
- **Fix**: Refresh page and try again

### Word Count Wrong Color
- **Check**: Does section have a `word_limit`?
- **Expected**:
  * Green if word_count < 90% of limit
  * Yellow if 90% ≤ word_count ≤ 100%
  * Red if word_count > 100%

### SourcesPanel Empty
- **Check**: Did generation complete successfully?
- **Check**: Are `citations` returned in API response?
- **Fix**: Look for backend errors in [RETRIEVER] logs

## API Endpoints Reference

### Generate Section
```http
POST /api/sections/generate
Content-Type: application/json

{
  "session_id": "your-session-id",
  "section_name": "Project Description",
  "section_requirements": "Describe project objectives",
  "word_limit": 500,
  "char_limit": null,
  "format_type": "narrative"
}
```

**Response**:
```json
{
  "session_id": "your-session-id",
  "section_name": "Project Description",
  "text": "Generated text with inline citations [Doc, p.1]...",
  "word_count": 487,
  "citations": [
    {
      "document_title": "Doc",
      "page_number": 1,
      "chunk_text": "Original text snippet...",
      "relevance_score": 0.85
    }
  ],
  "warning": null,
  "locked_paragraphs": []
}
```

### Get Generated Section
```http
GET /api/sections/{session_id}/{section_name}
```

**Response**: Same as above

## File Structure

```
EasyGrant/
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── retriever.py              ← NEW (Phase 5)
│   │   │   └── section_generator.py      ← NEW (Phase 5)
│   │   ├── api/routes/
│   │   │   ├── sections.py               ← NEW (Phase 5)
│   │   │   └── requirements.py
│   │   └── services/
│   │       └── llm_client.py             ← MODIFIED
│   └── .env                              ← REQUIRED (OpenAI API key)
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── EditorPanel.jsx           ← NEW (Phase 5)
│       │   ├── EditorPanel.css           ← NEW (Phase 5)
│       │   ├── SourcesPanel.jsx          ← NEW (Phase 5)
│       │   ├── SourcesPanel.css          ← NEW (Phase 5)
│       │   └── ChecklistPanel.jsx        ← MODIFIED
│       ├── App.jsx                       ← MODIFIED (3-panel layout)
│       └── App.css                       ← MODIFIED
└── vector/                               ← ChromaDB storage
```

## Next Steps After Testing

1. **If bugs found**: Report in GitHub issues or fix immediately
2. **If working**: Proceed to Phase 6 (Edit + Regenerate)
3. **Performance issues**: Optimize retrieval (adjust top_k, relevance threshold)
4. **Citation quality**: Improve prompts in section_generator.py

---

**Ready to test? Start with Step 1 above! 🚀**
