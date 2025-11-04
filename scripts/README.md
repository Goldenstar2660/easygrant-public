# 🛠️ EasyGrant Scripts

Utility scripts for development, testing, and deployment.

## 🚀 Development Scripts

### `start-backend.ps1`
Starts the FastAPI backend server with automatic environment variable loading.

```powershell
.\scripts\start-backend.ps1
```

**What it does:**
- Loads environment variables from `.env`
- Activates virtual environment
- Starts uvicorn server on http://localhost:8000

### `start-frontend.ps1`
Starts the Vite frontend development server.

```powershell
.\scripts\start-frontend.ps1
```

**What it does:**
- Checks/installs npm dependencies
- Creates `.env` from `.env.example` if needed
- Starts Vite dev server on http://localhost:5173

### `start-dev.ps1`
**[DEPRECATED - Use individual scripts]** Starts both backend and frontend in one command.

```powershell
.\scripts\start-dev.ps1
```

**Recommended:** Use separate terminals with `start-backend.ps1` and `start-frontend.ps1` instead.

## 🔍 Deployment Scripts

### `check-deployment.ps1`
Pre-deployment checklist to verify your app is ready to deploy.

```powershell
.\scripts\check-deployment.ps1
```

**Checks:**
- Git repository status
- Environment variables
- .gitignore security
- Build files
- Dependencies
- Uncommitted changes

**Run this before:** Pushing to GitHub or deploying to production.

## 🔧 Utility Scripts

### `explore_vectordb.py`
Utility to explore and inspect the Chroma vector database.

```powershell
python scripts\explore_vectordb.py
```

**Use for:** Debugging embedding storage and retrieval.

### `process_pdfs_to_vectordb.py`
Batch process PDF files into the vector database.

```powershell
python scripts\process_pdfs_to_vectordb.py
```

**Use for:** Pre-loading documents into the vector store.

### `main.py`
Legacy main entry point (use backend/src/main.py instead).

## 📋 Quick Reference

### Start Development
```powershell
# Terminal 1 - Backend
.\scripts\start-backend.ps1

# Terminal 2 - Frontend
.\scripts\start-frontend.ps1
```

### Pre-Deployment Check
```powershell
.\scripts\check-deployment.ps1
```

### Explore Vector DB
```powershell
python scripts\explore_vectordb.py
```

---

**See also:**
- [Getting Started Guide](../docs/guides/GETTING_STARTED.md)
- [Deployment Guide](../docs/guides/DEPLOYMENT_GUIDE.md)
