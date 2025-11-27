<#
upload_templates.ps1

Run this locally to create a branch, commit the `hosting_panel/templates` folder,
and push it to your remote. You must run this from the repository root
(C:\Users\Admin\Documents) and have git installed and authenticated.

Usage:
  Open PowerShell in C:\Users\Admin\Documents and run:
    .\hosting_panel\upload_templates.ps1 -Branch "add/templates" -Remote "origin"

If your default branch is not `main`, set -TargetBranch accordingly.
#>
param(
    [string]$Branch = "add/templates",
    [string]$Remote = "origin",
    [string]$TargetBranch = "main"
)

function ExitWith($code, $msg) {
    Write-Host $msg -ForegroundColor Red
    exit $code
}

# Verify we are in repo root
$cwd = Get-Location
if (-not (Test-Path -Path (Join-Path $cwd.Path "hosting_panel\templates"))) {
    ExitWith 1 "Error: Can't find hosting_panel\templates in $($cwd.Path). Run this script from the repo root."
}

# Ensure git exists
try {
    git --version > $null 2>&1
} catch {
    ExitWith 2 "Error: git is not installed or not in PATH. Install git and try again."
}

# Show status
Write-Host "Using repo root: $($cwd.Path)"
Write-Host "Current branch: $(git rev-parse --abbrev-ref HEAD)"

# Create and switch to new branch
Write-Host "Creating branch '$Branch'..."
git checkout -b $Branch
if ($LASTEXITCODE -ne 0) {
    ExitWith 3 "Failed to create branch. You may already have a branch named $Branch. Try removing or pick another name with -Branch."
}

# Stage templates
Write-Host "Staging hosting_panel/templates ..."
git add hosting_panel/templates
if ($LASTEXITCODE -ne 0) {
    ExitWith 4 "Failed to stage templates."
}

# Commit
$message = "Add templates (login/register/dashboard/pricing)"
Write-Host "Committing: $message"
git commit -m "$message"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nothing to commit or commit failed. If nothing to commit, the files may already be tracked." -ForegroundColor Yellow
}

# Push
Write-Host "Pushing branch to remote '$Remote'..."
git push -u $Remote $Branch
if ($LASTEXITCODE -ne 0) {
    ExitWith 5 "Failed to push branch. Check your git remote and authentication (PAT or SSH)."
}

Write-Host "Success! Branch '$Branch' pushed to '$Remote'." -ForegroundColor Green
Write-Host "Open a Pull Request from '$Branch' into '$TargetBranch' on GitHub to merge the templates."
Write-Host "If you need help with authentication (PAT/SSH), tell me and I will show steps."