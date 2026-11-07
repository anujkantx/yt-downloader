# PowerShell One-Click Installer for Video Downloader
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "     Installing Video Downloader for Windows     " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$DistDir = Join-Path $ProjectRoot "dist\VideoDownloader"
$ExecutableSource = Join-Path $DistDir "VideoDownloader.exe"

# If not built yet, run build script
if (-not (Test-Path $ExecutableSource)) {
    Write-Host "`nDistribution files not found. Building first..." -ForegroundColor Yellow
    & (Join-Path $ScriptDir "build_windows.ps1")
}

# Target Program Directory (Per-user, standard Windows apps location like Chrome/VSCode/Spotify)
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\VideoDownloader"
Write-Host "`n[1/4] Installing application files to:" -ForegroundColor Yellow
Write-Host "      $InstallDir" -ForegroundColor White

if (Test-Path $InstallDir) {
    # If app is running, stop it
    Get-Process "VideoDownloader" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Milliseconds 500
    Remove-Item -Recurse -Force $InstallDir
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Copy-Item -Path "$DistDir\*" -Destination $InstallDir -Recurse -Force
Write-Host "Files installed successfully." -ForegroundColor Green

$InstalledExe = Join-Path $InstallDir "VideoDownloader.exe"

# Create Uninstaller Script inside install directory
$UninstallScript = Join-Path $InstallDir "uninstall.ps1"
$UninstallContent = @"
[CmdletBinding()]
param()
Get-Process "VideoDownloader" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500

# Remove Desktop Shortcut
`$DesktopShortcut = Join-Path `([Environment]::GetFolderPath('Desktop')) "Video Downloader.lnk"
if (Test-Path `$DesktopShortcut) { Remove-Item -Force `$DesktopShortcut }

# Remove Start Menu Shortcut
`$StartMenuShortcut = Join-Path `([Environment]::GetFolderPath('Programs')) "Video Downloader.lnk"
if (Test-Path `$StartMenuShortcut) { Remove-Item -Force `$StartMenuShortcut }

# Remove Registry Entry
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoDownloader" -Recurse -ErrorAction SilentlyContinue

Write-Host "Application uninstalled successfully." -ForegroundColor Green
"@
Set-Content -Path $UninstallScript -Value $UninstallContent -Encoding UTF8

# [2/4] Create Start Menu Shortcut
Write-Host "`n[2/4] Creating Start Menu shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$StartMenuDir = [Environment]::GetFolderPath('Programs')
$StartMenuShortcutPath = Join-Path $StartMenuDir "Video Downloader.lnk"
$StartShortcut = $WshShell.CreateShortcut($StartMenuShortcutPath)
$StartShortcut.TargetPath = $InstalledExe
$StartShortcut.WorkingDirectory = $InstallDir
$StartShortcut.IconLocation = "$InstalledExe,0"
$StartShortcut.Description = "Modern Windows Video Downloader"
$StartShortcut.Save()
Write-Host "Start Menu shortcut created: $StartMenuShortcutPath" -ForegroundColor Green

# [3/4] Create Desktop Shortcut
Write-Host "`n[3/4] Creating Desktop shortcut..." -ForegroundColor Yellow
$DesktopDir = [Environment]::GetFolderPath('Desktop')
$DesktopShortcutPath = Join-Path $DesktopDir "Video Downloader.lnk"
$DesktopShortcut = $WshShell.CreateShortcut($DesktopShortcutPath)
$DesktopShortcut.TargetPath = $InstalledExe
$DesktopShortcut.WorkingDirectory = $InstallDir
$DesktopShortcut.IconLocation = "$InstalledExe,0"
$DesktopShortcut.Description = "Modern Windows Video Downloader"
$DesktopShortcut.Save()
Write-Host "Desktop shortcut created: $DesktopShortcutPath" -ForegroundColor Green

# [4/4] Register in Windows "Installed Apps / Add or Remove Programs"
Write-Host "`n[4/4] Registering in Windows Installed Apps..." -ForegroundColor Yellow
$RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoDownloader"
if (-not (Test-Path $RegPath)) {
    New-Item -Path $RegPath -Force | Out-Null
}
New-ItemProperty -Path $RegPath -Name "DisplayName" -Value "Video Downloader" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value "$InstalledExe,0" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value "1.0.0" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "Publisher" -Value "VideoDownloader" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir -PropertyType String -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `"$UninstallScript`"" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "EstimatedSize" -Value 150000 -PropertyType DWord -Force | Out-Null
Write-Host "Registered in Windows Settings > Installed Apps." -ForegroundColor Green

Write-Host "`n=================================================" -ForegroundColor Green
Write-Host "         INSTALLATION COMPLETE!                  " -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host "You can now launch Video Downloader:"
Write-Host "  1. From your Desktop shortcut (`"Video Downloader`")" -ForegroundColor Cyan
Write-Host "  2. By pressing Start / Windows key and typing `"Video Downloader`"" -ForegroundColor Cyan
Write-Host "  3. From Windows Installed Apps settings" -ForegroundColor Cyan
