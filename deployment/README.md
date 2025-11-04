# EasyGrant Deployment Configuration

This folder contains all deployment-related configuration files for EasyGrant.

## Files

### `Dockerfile`
Multi-stage Docker container configuration for building and running the FastAPI backend.

**Key features:**
- Python 3.11 slim base image
- System dependencies for PDF processing (gcc, g++)
- Backend application with all dependencies
- Health check endpoint
- Optimized for <512MB RAM (free tier compatible)

**Build:**
```bash
docker build -f deployment/Dockerfile -t easygrant .
```

**Run:**
```bash
docker run -p 8000:8000 --env-file .env easygrant
```

### `render.yaml`
Render.com Blueprint configuration for one-click deployment.

**Features:**
- Free tier compatible (<512MB RAM, 1GB storage)
- Auto-deploy from main branch
- Health check monitoring
- Persistent disk mount for uploads and vector database
- Environment variable configuration

**Deploy:**
1. Push to GitHub
2. Connect repository to Render
3. Render will auto-detect and deploy using this blueprint
4. Set `OPENAI_API_KEY` in Render dashboard

## Deployment Instructions

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production (Render)
1. Fork/clone this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Set environment variables in Render dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key
6. Deploy!

### Docker (Self-hosted)
```bash
# Build
docker build -f deployment/Dockerfile -t easygrant .

# Run
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/vector:/app/vector \
  easygrant
```

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional (see `backend/config.yaml` for defaults):
- `LLM_REQUIREMENTS_MODEL` - Model for requirements extraction (default: gpt-4o)
- `LLM_DRAFTING_MODEL` - Model for section drafting (default: gpt-4o-mini)
- `EMBEDDINGS_MODEL` - Embedding model (default: text-embedding-3-small)
- `PORT` - Server port (default: 8000)

## Notes

- `.dockerignore` is in the repository root (required by Docker context)
- Backend configuration is in `backend/config.yaml`
- Frontend must be deployed separately (Vercel, Netlify, etc.) or served via CDN
