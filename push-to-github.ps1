# PowerShell script to push to GitHub
# Make sure Git is installed before running this script

Write-Host "Starting Git setup and push to GitHub..." -ForegroundColor Green

# Check if git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Then restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Git found! Proceeding with setup..." -ForegroundColor Green

# Initialize git repository if not already initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Cyan
    git init
} else {
    Write-Host "Git repository already initialized." -ForegroundColor Cyan
}

# Add all files
Write-Host "Adding files to git..." -ForegroundColor Cyan
git add .

# Check if there are changes to commit
$status = git status --porcelain
if (-not $status) {
    Write-Host "No changes to commit." -ForegroundColor Yellow
} else {
    Write-Host "Committing changes..." -ForegroundColor Cyan
    git commit -m "Initial commit: London Food Finds UK directory website with sitemap"
}

# Add remote if not already added
$remote = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Adding remote repository..." -ForegroundColor Cyan
    git remote add origin https://github.com/julanraveendran/Londonfoodfindsuk.git
} else {
    Write-Host "Remote already configured: $remote" -ForegroundColor Cyan
}

# Set branch to main
Write-Host "Setting branch to main..." -ForegroundColor Cyan
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "You may be prompted for your GitHub credentials." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSuccess! Code has been pushed to GitHub." -ForegroundColor Green
    Write-Host "View your repository at: https://github.com/julanraveendran/Londonfoodfindsuk" -ForegroundColor Green
} else {
    Write-Host "`nPush failed. Please check the error messages above." -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Authentication required (use GitHub Personal Access Token)" -ForegroundColor Yellow
    Write-Host "  - Network issues" -ForegroundColor Yellow
}


