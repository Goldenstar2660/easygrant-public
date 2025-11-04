# EasyGrant Backend Startup Script
# This script activates the virtual environment, loads the .env file, and starts the backend server

Write-Host "🚀 Starting EasyGrant Backend Server..." -ForegroundColor Green

# Navigate to project root
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "📄 Loading environment variables from .env..." -ForegroundColor Cyan
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#') -and $line.Contains('=')) {
            $parts = $line.Split('=', 2)
            $name = $parts[0].Trim()
            $value = $parts[1].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            if ($name -eq "OPENAI_API_KEY") {
                Write-Host "  ✓ Set OPENAI_API_KEY (hidden)" -ForegroundColor Gray
            } else {
                Write-Host "  ✓ Set $name" -ForegroundColor Gray
            }
        }
    }
} else {
    Write-Host "⚠️  .env file not found! Please create one from .env.example" -ForegroundColor Yellow
    exit 1
}

# Check if OPENAI_API_KEY is set
if (-not $env:OPENAI_API_KEY) {
    Write-Host "❌ OPENAI_API_KEY not set in .env file" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the backend server
& ".\.venv\Scripts\python.exe" -m uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
