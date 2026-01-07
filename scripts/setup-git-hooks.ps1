# PowerShell script to install Git hooks and pre-commit
# Run this after cloning the repository

Write-Host "🔧 Setting up Git hooks and pre-commit..." -ForegroundColor Cyan

# Check if pre-commit is installed
$preCommitInstalled = Get-Command pre-commit -ErrorAction SilentlyContinue

if (-not $preCommitInstalled) {
    Write-Host "📦 Installing pre-commit..." -ForegroundColor Yellow
    pip install pre-commit

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install pre-commit" -ForegroundColor Red
        exit 1
    }
}

# Install pre-commit hooks
Write-Host "🎣 Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install --install-hooks
pre-commit install --hook-type pre-push

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install pre-commit hooks" -ForegroundColor Red
    exit 1
}

# Note: pre-commit framework creates its own hooks in .git/hooks/
# The custom PowerShell hooks in .github/hooks/ are for reference only

# Test pre-commit installation
Write-Host "`n🧪 Testing pre-commit installation..." -ForegroundColor Yellow
pre-commit run --all-files

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Git hooks setup complete!" -ForegroundColor Green
    Write-Host "`nℹ️  Hooks installed:" -ForegroundColor Cyan
    Write-Host "  • pre-commit: Runs linters and formatters before each commit" -ForegroundColor White
    Write-Host "  • pre-push: Runs full test suite before pushing" -ForegroundColor White
    Write-Host "`n💡 To skip hooks temporarily, use: git commit --no-verify" -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️  Some pre-commit checks failed. Fix the issues and run:" -ForegroundColor Yellow
    Write-Host "  pre-commit run --all-files" -ForegroundColor White
}
