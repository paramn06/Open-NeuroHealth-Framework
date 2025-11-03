<# 
  prep_copyright_zip.ps1
  Cleans unnecessary files and creates a clean ZIP for copyright filing.
#>

$ErrorActionPreference = "SilentlyContinue"

$ZipName = "Open_NeuroHealth_Framework_v1.zip"
$ZipPath = Join-Path (Split-Path -Parent (Get-Location)) $ZipName
$Include = @("app", "modules", "tools", "data\exports", "README.txt", "LICENSE.txt", "COPYRIGHT.txt")
$DeletePatterns = @(
  "**\__pycache__", "**\*.pyc", ".pytest_cache", ".mypy_cache",
  ".vscode", ".idea", ".git", "data\logs", "venv", "env", ".venv",
  ".DS_Store", "Thumbs.db", "build", "dist", "*.egg-info"
)

Write-Host "=== PREVIEW FILES TO DELETE ===" -ForegroundColor Cyan
foreach ($pat in $DeletePatterns) {
  Get-ChildItem -Path $pat -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
}
Write-Host "`nPress ENTER to proceed or Ctrl+C to abort" -ForegroundColor Yellow
[void][System.Console]::ReadLine()

Write-Host "=== DELETING UNNECESSARY FILES ===" -ForegroundColor Cyan
foreach ($pat in $DeletePatterns) {
  Remove-Item $pat -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== CREATING CLEAN ZIP ===" -ForegroundColor Cyan
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

$Existing = @()
foreach ($p in $Include) { if (Test-Path $p) { $Existing += $p } }

Compress-Archive -Path $Existing -DestinationPath $ZipPath
Write-Host "✅ Created ZIP → $ZipPath"
