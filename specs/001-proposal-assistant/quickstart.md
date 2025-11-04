# Quickstart Guide: Smart Proposal Assistant

**Feature**: 001-proposal-assistant  
**Target Audience**: Developers setting up local environment or deploying to hosting platforms  
**Estimated Setup Time**: 15-20 minutes (local), 30-40 minutes (first deployment)

---

## Prerequisites

### Local Development
- **Python**: 3.11+ ([Download](https://www.python.org/downloads/))
- **Node.js**: 18+ ([Download](https://nodejs.org/))
- **Docker**: 24+ (optional, for containerized dev) ([Download](https://www.docker.com/))
- **Git**: For cloning repository
- **OpenAI API Key**: Required for embeddings and generation ([Get key](https://platform.openai.com/api-keys))

### Deployment
- **Render/Railway/Hugging Face Spaces Account**: Free tier sufficient
- **OpenAI API Key**: Added as environment variable in platform

---

## Local Setup (Development Mode)

### 1. Clone Repository

```bash
git clone https://github.com/Goldenstar2660/EasyGrant.git
cd EasyGrant
git checkout 001-proposal-assistant
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-...your-key-here
ENVIRONMENT=development
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p ../data/uploads ../data/temp ../vector

# Run backend (from backend/ directory)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should now be running at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### 4. Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend should now be running at `http://localhost:5173`. Open in your browser to access the UI.

### 5. Verify Setup

1. Open `http://localhost:5173` in your browser
2. You should see three-panel layout: Checklist (left) | Editor (center) | Sources (right)
3. Click "Upload Funding Call" - file picker should appear
4. Backend logs at `http://localhost:8000` should show CORS middleware active

---

## Docker Setup (Containerized Development)

### 1. Build Docker Image

```bash
# From repository root
docker build -t easygrant:dev .
```

### 2. Run Container with Volume Mounts

```bash
docker run -d \
  --name easygrant-dev \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-proj-...your-key \
  -v $(pwd)/data/uploads:/app/data/uploads \
  -v $(pwd)/vector:/app/vector \
  easygrant:dev
```

### 3. View Logs

```bash
docker logs -f easygrant-dev
```

### 4. Access Application

- Backend API: `http://localhost:8000`
- Frontend (served by FastAPI): `http://localhost:8000/` (static bundle)

### 5. Stop Container

```bash
docker stop easygrant-dev
docker rm easygrant-dev
```

---

## Deployment to Render (Recommended for Demo)

### 1. Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (`Goldenstar2660/EasyGrant`)
4. Select branch: `001-proposal-assistant`

### 2. Configure Service

**Settings**:
- **Name**: `easygrant-demo`
- **Runtime**: Docker
- **Dockerfile Path**: `./Dockerfile` (default)
- **Instance Type**: Free (512MB RAM)

**Environment Variables**:
```
OPENAI_API_KEY=sk-proj-...your-key
ENVIRONMENT=production
```

**Disk** (for persistent uploads & vector store):
- Click "Add Disk"
- **Name**: `uploads`
- **Mount Path**: `/app/data/uploads`
- **Size**: 1GB (free tier)
- Click "Add Disk" again
- **Name**: `vector`
- **Mount Path**: `/app/vector`
- **Size**: 1GB

### 3. Deploy

- Click "Create Web Service"
- Wait for build (5-10 minutes first time)
- Once live, Render provides public URL: `https://easygrant-demo.onrender.com`

### 4. Verify Deployment

1. Visit your Render URL
2. Upload a sample funding call PDF
3. Upload 1-2 supporting documents
4. Generate a section
5. Check that citations appear with inline `[Doc Title, p.N]` format
6. Export DOCX and verify it downloads

---

## Deployment to Railway

### 1. Install Railway CLI (Optional)

```bash
npm install -g @railway/cli
railway login
```

### 2. Deploy via Web Interface

1. Go to [Railway Dashboard](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `Goldenstar2660/EasyGrant`, branch `001-proposal-assistant`
4. Railway auto-detects Dockerfile

### 3. Configure Environment

**Variables**:
```
OPENAI_API_KEY=sk-proj-...your-key
ENVIRONMENT=production
```

**Volumes**:
- Add volume: `/app/data/uploads` (1GB)
- Add volume: `/app/vector` (1GB)

### 4. Access Application

- Railway provides URL: `https://easygrant-production.up.railway.app`

---

## Deployment to Hugging Face Spaces

### 1. Create Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. **Space name**: `easygrant-demo`
4. **License**: MIT
5. **SDK**: Docker
6. **Hardware**: Free CPU (basic)

### 2. Push Code

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/easygrant-demo
cd easygrant-demo

# Copy files from EasyGrant repo
cp -r path/to/EasyGrant/* .

# Ensure Dockerfile is at root
# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### 3. Configure Secrets

In Space settings → "Repository secrets":
```
OPENAI_API_KEY=sk-proj-...your-key
```

### 4. Access Application

- Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/easygrant-demo`

---

## Testing the Deployed Demo

### Full Workflow Test

1. **Open Public URL** in browser
2. **Upload Funding Call**:
   - Use sample PDF from `docs/samples/community_grant_rfp.pdf` (if provided)
   - Or any grant RFP PDF with clear sections and word limits
3. **Verify Checklist**:
   - Left panel should show extracted sections (e.g., "Community Need - 500 words")
   - If extraction failed, check backend logs for errors
4. **Upload Supporting Docs**:
   - Upload 2-3 PDFs (community plans, budgets, etc.)
   - Wait for "Indexing complete" confirmation
5. **Generate Section**:
   - Click first section in checklist
   - Click "Generate Draft"
   - Wait 20-30 seconds
   - Verify text appears with `[Document Title, p.N]` citations
   - Check word count indicator (e.g., "487 / 500 words")
6. **Edit Section**:
   - Manually add a sentence in the editor
   - Edited text should be highlighted or marked
7. **Regenerate (Keep Edits)**:
   - Click "Regenerate (keep edits)" button
   - Verify your manual sentence remains unchanged
   - Verify surrounding AI text updates with new context
8. **Export DOCX**:
   - Click "Export Proposal"
   - Select "Footnotes" citation format
   - Click "Download DOCX"
   - Open in Microsoft Word
   - Verify sections appear in order with footnotes

### Performance Benchmarks

Expected on free-tier hosting:
- Upload + extraction (10MB PDF): <15 seconds
- Supporting doc indexing (5 docs, 100 pages): <60 seconds
- Section generation (500 words): <30 seconds
- DOCX export: <5 seconds
- Data deletion: <5 seconds

If slower, check:
- OpenAI API rate limits (status at [status.openai.com](https://status.openai.com))
- Hosting platform resource usage (CPU/memory)
- Network latency (try from different location)

---

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Fix**: Ensure you activated virtual environment and ran `pip install -r requirements.txt`

**Error**: `OPENAI_API_KEY not found`
- **Fix**: Check `.env` file exists and contains valid key; restart backend after adding

### Frontend Shows CORS Error

**Issue**: `Access to fetch at 'http://localhost:8000/api/...' has been blocked by CORS`
- **Fix**: Ensure backend is running with CORS middleware enabled (check `src/api/main.py` has `CORSMiddleware` with `allow_origins=["http://localhost:5173"]`)

### Upload Fails with "File Too Large"

**Issue**: File >10MB for funding call or >50MB total for supporting docs
- **Fix**: Reduce file size or split large documents; check `FR-002` upload limits

### Requirements Extraction Returns Empty Checklist

**Issue**: PDF may be scanned (images only, no text)
- **Fix**: Use text-based PDFs; consider OCR preprocessing (out of MVP scope)

### Section Generation Shows "No Context Found"

**Issue**: Supporting docs don't contain relevant content for section
- **Fix**: Upload more diverse documents (strategic plans, budgets, demographics); check chunk retrieval relevance scores in logs

### Docker Build Fails

**Error**: `Error response from daemon: failed to build: ...`
- **Fix**: Ensure Docker has enough resources (RAM >4GB, Disk >10GB); check `Dockerfile` syntax; clear build cache with `docker system prune -a`

### Deployment Succeeds but App Shows 500 Error

**Issue**: Environment variable missing or invalid
- **Fix**: Check platform logs for errors; verify `OPENAI_API_KEY` is set correctly; check volume mounts are active

---

## Configuration

All operational parameters are in `config.yaml` (root directory):

```yaml
llm:
  reasoning_model: "gpt-4o"          # For requirements extraction & QC
  drafting_model: "gpt-4o-mini"      # For section generation

embeddings:
  model: "text-embedding-3-small"
  chunk_size: 600
  chunk_overlap: 90

retrieval:
  top_k: 5
  similarity_threshold: 0.7
```

**To modify**:
1. Edit `config.yaml`
2. Restart backend (local) or redeploy (production)
3. Changes apply to all new sessions (existing sessions use old config)

---

## Development Tips

### Hot Reload

- **Backend**: FastAPI auto-reloads on file changes when started with `--reload` flag
- **Frontend**: Vite HMR (Hot Module Replacement) updates on save, no manual refresh

### Debugging

**Backend**:
```python
# Add to any route for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Request data: {request_data}")
```

**Frontend**:
```javascript
// Add to component
console.log("State:", { sections, checklist, sources });
```

### Testing Locally

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests (if implemented)
cd frontend
npm run test
```

---

## Next Steps

After successful setup:
1. **Review** `specs/001-proposal-assistant/plan.md` for implementation plan
2. **Run** `/speckit.tasks` to generate task breakdown
3. **Implement** user stories in priority order (P1 → P2 → P3)
4. **Commit** at task boundaries for clean git history

---

## Support

- **Constitution**: See `.specify/memory/constitution.md` for guiding principles
- **Spec**: See `specs/001-proposal-assistant/spec.md` for requirements
- **Contracts**: See `specs/001-proposal-assistant/contracts/` for API docs
- **Issues**: File GitHub issues with `[001-proposal-assistant]` prefix

---

**Last Updated**: 2025-10-26  
**Tested On**: Python 3.11, Node 18, Docker 24, Render Free Tier
