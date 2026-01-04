# Quick Setup Script for pyMediaManager GitHub Deployment

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  pyMediaManager v0.0.1 - GitHub Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if ($ghInstalled) {
    Write-Host "✓ GitHub CLI detected" -ForegroundColor Green
    Write-Host ""
    Write-Host "Creating repository with GitHub CLI..." -ForegroundColor Yellow
    
    # Create repository
    gh repo create mosh666/pyMM --public `
        --description "Portable Python-based media management application with modern Fluent Design UI" `
        --confirm
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Repository created successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pushing local repository to GitHub..." -ForegroundColor Yellow
        
        # Push to GitHub
        git push -u origin main
        git push origin v0.0.1
        
        Write-Host "✓ Repository published to GitHub!" -ForegroundColor Green
        Write-Host ""
        Write-Host "View your repository at: https://github.com/mosh666/pyMM" -ForegroundColor Cyan
        Write-Host "Release workflow should trigger automatically for v0.0.1 tag" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠ GitHub CLI not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please choose an option:" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 1: Install GitHub CLI (Recommended)" -ForegroundColor White
    Write-Host "  Run: winget install GitHub.cli" -ForegroundColor Gray
    Write-Host "  Then run this script again" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Option 2: Manual Setup via Web Browser" -ForegroundColor White
    Write-Host "  1. Open: https://github.com/new" -ForegroundColor Gray
    Write-Host "  2. Repository name: pyMM" -ForegroundColor Gray
    Write-Host "  3. Description: Portable Python-based media management application" -ForegroundColor Gray
    Write-Host "  4. Visibility: Public" -ForegroundColor Gray
    Write-Host "  5. DO NOT initialize with README, .gitignore, or license" -ForegroundColor Gray
    Write-Host "  6. Click 'Create repository'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Then run these commands:" -ForegroundColor Gray
    Write-Host "    cd D:\pyMM" -ForegroundColor DarkGray
    Write-Host "    git remote add origin https://github.com/mosh666/pyMM.git" -ForegroundColor DarkGray
    Write-Host "    git push -u origin main" -ForegroundColor DarkGray
    Write-Host "    git push origin v0.0.1" -ForegroundColor DarkGray
    Write-Host ""
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Next Steps After Publishing:" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "1. Check GitHub Actions: https://github.com/mosh666/pyMM/actions" -ForegroundColor White
Write-Host "2. Verify CI workflow passed" -ForegroundColor White
Write-Host "3. Check release was created: https://github.com/mosh666/pyMM/releases" -ForegroundColor White
Write-Host "4. Download and test portable ZIP" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see: DEPLOY.md" -ForegroundColor Gray
Write-Host ""
