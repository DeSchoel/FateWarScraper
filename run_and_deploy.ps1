# Helper script to run scan and deploy
# Best used with Windows Task Scheduler

Write-Host "Starting scheduled scan..." -ForegroundColor Cyan

# Check if venv exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
}

# Run scraper (Gold tracking is disabled)
python -m fatewarscraper

# Check if scan was successful (index.html updated)
if ($LASTEXITCODE -eq 0) {
    Write-Host "Scan successful. Deploying to GitHub Pages..." -ForegroundColor Green
    .\deploy_gh_pages.ps1
} else {
    Write-Host "Scan failed. Skipping deployment." -ForegroundColor Red
    exit 1
}
