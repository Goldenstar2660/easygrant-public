# 🚀 EasyGrant - Quick Start Guide

Welcome back! This guide will help you get the EasyGrant development environment running on your new computer.

## ✅ Prerequisites

- ✅ Python 3.11+ (already installed: Python 3.11.5)
- ✅ Node.js 18+ (you'll need to install this)
- ✅ OpenAI API key (already in `.env` file)

## 🎯 Quick Start (2 Options)

### Option 1: Automated Startup Scripts (Recommended)

#### Terminal 1 - Backend:
```powershell
.\scripts\start-backend.ps1
```

#### Terminal 2 - Frontend:
```powershell
.\scripts\start-frontend.ps1
```

### Option 2: Manual Startup

#### Terminal 1 - Backend:
```powershell
# Navigate to project root
cd "C:\Users\Derek Chen\Desktop\Derek\Projects\EasyGrant"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.+?)\s*$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Start backend
python -m uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend:
```powershell
# Navigate to frontend directory
cd "C:\Users\Derek Chen\Desktop\Derek\Projects\EasyGrant\frontend"

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

## 🌐 Access Points

Once both servers are running:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Development Environment Setup

The Python environment is already configured:
- ✅ Virtual environment created: `.venv`
- ✅ Dependencies installed from `backend/requirements.txt`
- ✅ OpenAI API key configured in `.env`

## 📝 Environment Variables

Your `.env` file is already configured with:
```
OPENAI_API_KEY=sk-proj-... (already set)
```

To modify API keys or other settings, edit the `.env` file in the project root.

## 🐛 Troubleshooting

### Backend won't start

**Issue**: `OPENAI_API_KEY not found`
```powershell
# Make sure .env file exists and contains your API key
Get-Content .env | Select-String "OPENAI_API_KEY"
```

**Issue**: `ModuleNotFoundError`
```powershell
# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### Frontend won't start

**Issue**: `Cannot find module`
```powershell
# Reinstall node modules
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

**Issue**: Port already in use
```powershell
# Kill process using port 5173
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process
```

## 📂 Project Structure

```
EasyGrant/
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI application
│   │   ├── agents/          # Requirements extractor, retriever, section generator
│   │   ├── api/routes/      # API endpoints
│   │   ├── models/          # Data models
│   │   ├── services/        # LLM client, embeddings, vector store
│   │   └── utils/           # Helpers
│   ├── requirements.txt
│   └── config.yaml
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/      # UI components
│   │   └── services/        # API client
│   ├── package.json
│   └── vite.config.js
├── .env                     # Environment variables (DO NOT COMMIT)
├── .venv/                   # Python virtual environment
├── start-backend.ps1        # Backend startup script
└── start-frontend.ps1       # Frontend startup script
```

## 🔧 Common Tasks

### Run tests
```powershell
# Backend tests
cd backend
pytest

# Or run specific test file
pytest tests/test_phase4_requirements.py
```

### Check code quality
```powershell
# Linting
ruff check .

# Format code
ruff format .
```

### Reset environment
```powershell
# Backend
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Frontend
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

## 📚 Additional Resources

- **Testing Guide**: `TESTING_FRONTEND.md`
- **API Contracts**: `specs/001-proposal-assistant/contracts/openapi.yaml`
- **Full Quickstart**: `specs/001-proposal-assistant/quickstart.md`
- **Test Checklist**: `TEST_CHECKLIST.md`

## ✨ Next Steps

1. Verify backend is running: http://localhost:8000/health
2. Verify frontend is running: http://localhost:5173
3. Start developing! 🎉

---

**Note**: The backend is currently running successfully in your terminal. The frontend will need Node.js installed before you can start it.
