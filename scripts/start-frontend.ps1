# EasyGrant Frontend Startup Script
# This script installs dependencies (if needed) and starts the Vite dev server

Write-Host "🎨 Starting EasyGrant Frontend..." -ForegroundColor Green

# Navigate to frontend directory
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $ProjectRoot "frontend"
Set-Location $FrontendDir

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

# Check if .env exists, if not create from .env.example
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "📄 Creating .env from .env.example..." -ForegroundColor Cyan
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🌐 Starting Vite dev server..." -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the dev server
npm run dev
