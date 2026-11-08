# PowerShell build script for Video Downloader Windows executable
[CmdletBinding()]
param(
    [switch]$SkipTests = $false,
    [switch]$OneFile = $false
)

$ErrorActionPreference = "Stop"

# Determine project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
Set-Location $ProjectRoot

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Building Video Downloader for Windows" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot"

# 1. Virtual Environment Setup
$VenvDir = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"
$PyInstallerExe = Join-Path $VenvDir "Scripts\pyinstaller.exe"
$PytestExe = Join-Path $VenvDir "Scripts\pytest.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "`n[1/5] Creating virtual environment at .venv..." -ForegroundColor Yellow
    python -m venv $VenvDir
} else {
    Write-Host "`n[1/5] Virtual environment found at .venv" -ForegroundColor Green
}

# 2. Dependency Installation
Write-Host "`n[2/5] Ensuring dependencies are installed..." -ForegroundColor Yellow
& $PipExe install --quiet --upgrade pip
& $PipExe install --quiet -r (Join-Path $ProjectRoot "requirements-dev.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies."
    exit 1
}
Write-Host "Dependencies verified." -ForegroundColor Green

# 3. Running Unit Tests
if (-not $SkipTests) {
    Write-Host "`n[3/5] Running automated tests with pytest..." -ForegroundColor Yellow
    & $PytestExe -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed! Build aborted."
        exit 1
    }
    Write-Host "All tests passed successfully." -ForegroundColor Green
} else {
    Write-Host "`n[3/5] Skipping tests as requested." -ForegroundColor DarkYellow
}

# 4. Generate Application Icons if missing
$IconPath = Join-Path $ProjectRoot "assets\icons\app_icon.ico"
if (-not (Test-Path $IconPath)) {
    Write-Host "Generating application icons..." -ForegroundColor Yellow
    & $PythonExe -c "from PIL import Image, ImageDraw; import os; os.makedirs('assets/icons', exist_ok=True); img = Image.new('RGBA', (256, 256), (0,0,0,0)); draw = ImageDraw.Draw(img); draw.rounded_rectangle([16,16,240,240], radius=48, fill=(79,70,229,255)); img.save('assets/icons/app_icon.ico', format='ICO')"
}

# 5. Ensure FFmpeg binary is present for bundling
$FfmpegExe = Join-Path $ProjectRoot "assets\bin\ffmpeg.exe"
if (-not (Test-Path $FfmpegExe)) {
    Write-Host "`nFFmpeg not found in assets\bin. Downloading automatically..." -ForegroundColor Yellow
    & $PythonExe -m app.services.ffmpeg_service --download-assets
}

# 5. Executable Build via PyInstaller
Write-Host "`n[4/5] Compiling application using PyInstaller..." -ForegroundColor Yellow
$SpecFile = Join-Path $ScriptDir "VideoDownloader.spec"

# Clean prior build artifacts
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }

& $PyInstallerExe --clean --noconfirm $SpecFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed!"
    exit 1
}

# 6. Build Inno Setup Installer (if ISCC is available)
$IsccCandidates = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)
$IsccExe = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($IsccExe) {
    Write-Host "`n[5/5] Compiling single-file website setup installer (ISCC)..." -ForegroundColor Yellow
    $IssScript = Join-Path $ScriptDir "installer.iss"
    $InstallerOutDir = Join-Path $ProjectRoot "dist_installer"
    if (-not (Test-Path $InstallerOutDir)) { New-Item -ItemType Directory -Path $InstallerOutDir -Force | Out-Null }
    & $IsccExe $IssScript
    $SetupExe = Join-Path $InstallerOutDir "VideoDownloader-Setup.exe"
    if (Test-Path $SetupExe) {
        Write-Host "Single-file web installer generated: $SetupExe" -ForegroundColor Green
    }
}

# 7. Verification and Reporting
$OutputFolder = Join-Path $DistDir "VideoDownloader"
$Executable = Join-Path $OutputFolder "VideoDownloader.exe"
$SetupExe = Join-Path $ProjectRoot "dist_installer\VideoDownloader-Setup.exe"

if (Test-Path $Executable) {
    Write-Host "`n=================================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    Write-Host "Standalone Folder: $OutputFolder" -ForegroundColor Cyan
    Write-Host "Executable:        $Executable" -ForegroundColor Cyan
    if (Test-Path $SetupExe) {
        Write-Host "Website Setup:     $SetupExe" -ForegroundColor Yellow
        Write-Host "                   (This is the single file you upload to your website!)" -ForegroundColor Yellow
    }
} else {
    Write-Error "Executable not found at expected path: $Executable"
    exit 1
}
