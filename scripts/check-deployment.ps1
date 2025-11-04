# EasyGrant Pre-Deployment Checklist
# Run this before deploying to production

Write-Host "🔍 EasyGrant Pre-Deployment Checklist" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

$allGood = $true

# Check 1: Git initialized
Write-Host "1. Checking Git repository..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "   ✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "   ❌ Git not initialized. Run: git init" -ForegroundColor Red
    $allGood = $false
}

# Check 2: .env file exists
Write-Host "2. Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
    
    # Check if OPENAI_API_KEY is set
    $envContent = Get-Content .env -Raw
    if ($envContent -match 'OPENAI_API_KEY=\S+') {
        Write-Host "   ✅ OPENAI_API_KEY is set" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  OPENAI_API_KEY not set in .env" -ForegroundColor Yellow
        $allGood = $false
    }
} else {
    Write-Host "   ⚠️  .env file not found (optional for deployment)" -ForegroundColor Yellow
}

# Check 3: .gitignore includes .env
Write-Host "3. Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content .gitignore -Raw
    if ($gitignoreContent -match '\.env') {
        Write-Host "   ✅ .env is in .gitignore (secure)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ .env NOT in .gitignore - SECURITY RISK!" -ForegroundColor Red
        $allGood = $false
    }
} else {
    Write-Host "   ❌ .gitignore not found" -ForegroundColor Red
    $allGood = $false
}

# Check 4: Dockerfile exists
Write-Host "4. Checking Dockerfile..." -ForegroundColor Yellow
if (Test-Path "Dockerfile") {
    Write-Host "   ✅ Dockerfile exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ Dockerfile not found" -ForegroundColor Red
    $allGood = $false
}

# Check 5: render.yaml exists
Write-Host "5. Checking render.yaml..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    Write-Host "   ✅ render.yaml exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  render.yaml not found" -ForegroundColor Yellow
}

# Check 6: Frontend build works
Write-Host "6. Checking frontend build..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "   ✅ Frontend package.json exists" -ForegroundColor Green
    
    # Check if dist folder exists (previous build)
    if (Test-Path "frontend/dist") {
        Write-Host "   ✅ Frontend dist folder exists (previously built)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Frontend not built yet. Run: cd frontend; npm run build" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Frontend package.json not found" -ForegroundColor Red
    $allGood = $false
}

# Check 7: Backend requirements.txt exists
Write-Host "7. Checking backend requirements..." -ForegroundColor Yellow
if (Test-Path "backend/requirements.txt") {
    Write-Host "   ✅ backend/requirements.txt exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ backend/requirements.txt not found" -ForegroundColor Red
    $allGood = $false
}

# Check 8: Git status
Write-Host "8. Checking Git status..." -ForegroundColor Yellow
if (Test-Path ".git") {
    $gitStatus = git status --porcelain 2>$null
    if ($gitStatus) {
        Write-Host "   ⚠️  You have uncommitted changes" -ForegroundColor Yellow
        Write-Host "   Run: git add . && git commit -m 'Ready for deployment'" -ForegroundColor Gray
    } else {
        Write-Host "   ✅ No uncommitted changes" -ForegroundColor Green
    }
}

# Check 9: README exists
Write-Host "9. Checking README..." -ForegroundColor Yellow
if (Test-Path "README.md") {
    Write-Host "   ✅ README.md exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  README.md not found (optional)" -ForegroundColor Yellow
}

# Check 10: Virtual environment
Write-Host "10. Checking Python virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "   ✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  No virtual environment (not needed for deployment)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Gray

if ($allGood) {
    Write-Host ""
    Write-Host "🎉 All critical checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Push to GitHub:" -ForegroundColor White
    Write-Host "     git push origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Deploy to Render (backend):" -ForegroundColor White
    Write-Host "     https://render.com → New Web Service" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Deploy to Vercel (frontend):" -ForegroundColor White
    Write-Host "     https://vercel.com → New Project" -ForegroundColor Gray
    Write-Host ""
    Write-Host "See DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "⚠️  Some checks failed. Fix the issues above before deploying." -ForegroundColor Yellow
    Write-Host ""
}
