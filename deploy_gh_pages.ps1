# Deployment script for GitHub Pages
# This script pushes the contents of the 'outputs' folder to the 'gh-pages' branch.

$RepoRoot = Get-Location
$OutputDir = Join-Path $RepoRoot "outputs"
$PagesDir = Join-Path $RepoRoot ".gh-pages-tmp"

if (-not (Test-Path $OutputDir)) {
    Write-Error "Output directory $OutputDir not found. Run the scraper first."
    exit 1
}

Write-Host "Preparing deployment to GitHub Pages..." -ForegroundColor Cyan

# Remove old temp dir if exists
if (Test-Path $PagesDir) {
    Remove-Item -Path $PagesDir -Force -Recurse -Confirm:$false -ErrorAction SilentlyContinue
}

# Clone the current repo's remote into a temp folder
$RemoteUrl = git remote get-url origin
git clone $RemoteUrl $PagesDir

pushd $PagesDir

# Switch to gh-pages branch or create it
$allBranches = git branch -a
if ($allBranches -match "remotes/origin/gh-pages" -or $allBranches -match "gh-pages") {
    git checkout gh-pages
} else {
    git checkout --orphan gh-pages
}

# Remove all files in the branch
git rm -rf .

# Copy all files from outputs
Get-ChildItem -Path "$OutputDir\*" -Exclude "*.png" | Copy-Item -Destination "." -Force

# Create .nojekyll to bypass Jekyll processing
New-Item -Path ".nojekyll" -ItemType File -Force | Out-Null

# Add and commit
git add .
git commit -m "Deploy latest alliance data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Push back to original repo's origin
Write-Host "Pushing to origin gh-pages..." -ForegroundColor Green
git push origin gh-pages --force

popd

# Cleanup
Remove-Item -Path $PagesDir -Force -Recurse -Confirm:$false

# Try to determine the GitHub Pages URL
$remoteUrl = git remote get-url origin
$url = "Your site URL"
if ($remoteUrl -match "github\.com[:/]([^/]+)/([^.]+)") {
    $user = $Matches[1]
    $repo = $Matches[2]
    $url = "https://$user.github.io/$repo/"
}

Write-Host "Deployment complete! Your site should be available at $url" -ForegroundColor Yellow
Write-Host "Note: It may take a few minutes for GitHub to process the update." -ForegroundColor Cyan
Write-Host "IMPORTANT: Ensure GitHub Pages is enabled in your repository settings (Settings -> Pages) and set to the 'gh-pages' branch." -ForegroundColor Gray
