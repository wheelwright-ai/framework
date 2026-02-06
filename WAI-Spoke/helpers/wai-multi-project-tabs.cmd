@echo off
REM wai-multi-project-tabs.cmd - Launch tabs for top 6 active projects
REM Version: 3.1.0
REM Purpose: Quick access to all active projects
REM Location: WAI-Spoke/helpers/wai-multi-project-tabs.cmd

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "HELPERS_DIR=!SCRIPT_DIR!"
if not "!HELPERS_DIR:~-1!"=="\" set "HELPERS_DIR=!HELPERS_DIR!\"

set "LOG_FILE=%USERPROFILE%\wai-multi-project-tabs.log"
echo [%DATE% %TIME%] Starting multi-project tabs launcher >> "!LOG_FILE!"

REM Discover active projects via PowerShell and hub-registry
set "HUB_REGISTRY=%USERPROFILE%\wheelwright-hub\hub\hub-registry.json"

if not exist "!HUB_REGISTRY!" (
  echo [%DATE% %TIME%] Hub registry not found at !HUB_REGISTRY! >> "!LOG_FILE!"
  echo Hub registry not found. Create hub first: WAI hub create
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Hub registry found: !HUB_REGISTRY! >> "!LOG_FILE!"

REM Call PowerShell to discover projects
set "PS_OUT=%TEMP%\wai_projects.txt"
set "PS_ERR=%TEMP%\wai_projects_err.txt"
if exist "!PS_OUT!" del /q "!PS_OUT!" >nul 2>&1
if exist "!PS_ERR!" del /q "!PS_ERR!" >nul 2>&1

set "PS_CMD=^
  $hub = Get-Content -Raw '%HUB_REGISTRY%' ^| ConvertFrom-Json; ^
  $cutoff = (Get-Date).AddDays(-7); ^
  $active = @(); ^
  foreach ($w in $hub.wheels) { if ($w.last_session_timestamp) { try { $d = [datetime]::Parse($w.last_session_timestamp); if ($d -gt $cutoff) { $active += $w } } catch {} } } ^
  $active ^| Sort-Object @{Expression={[datetime]::Parse($_.last_session_timestamp)}} -Desc ^| Select-Object -First 6 ^| ForEach-Object { $abbr = $_.abbrev; if (-not $abbr) { $abbr = $_.name }; if (-not $abbr) { $abbr = Split-Path $_.path -Leaf }; '{0}|{1}' -f $abbr, $_.path }
"

REM Execute PowerShell to get projects
powershell -NoProfile -Command "!PS_CMD!" > "!PS_OUT!" 2> "!PS_ERR!"

if exist "!PS_ERR!" (
  set /p PS_ERROR=<"!PS_ERR!"
  if not "!PS_ERROR!"=="" (
    echo [%DATE% %TIME%] PowerShell error: !PS_ERROR! >> "!LOG_FILE!"
  )
)

if exist "!PS_OUT!" (
  for /f "usebackq delims=" %%A in ("!PS_OUT!") do (
    set "PROJECTS=!PROJECTS! %%A"
  )
)

if not defined PROJECTS (
  echo [%DATE% %TIME%] No active projects found in registry >> "!LOG_FILE!"
  echo No active projects found in the last 7 days.
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Found projects: !PROJECTS! >> "!LOG_FILE!"

REM Find Windows Terminal
set "WT_EXE="
for /f "delims=" %%A in ('where wt.exe 2^>nul') do set "WT_EXE=%%A"
if not defined WT_EXE if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" set "WT_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"

if not defined WT_EXE (
  echo Windows Terminal not found. Install Windows Terminal to use this script.
  exit /b 1
)

echo [%DATE% %TIME%] Found projects: !PROJECTS! >> "!LOG_FILE!"

REM Build WT command with all projects as tabs
set "WT_CMD="
set "FIRST=1"
for %%P in (!PROJECTS!) do (
  set "PROJ_LINE=%%P"
  for /f "tokens=1,2 delims=^|" %%K in ("!PROJ_LINE!") do (
    set "ABBR=%%K"
    set "PATH_VAL=%%L"
    
    echo [%DATE% %TIME%] Tab: !ABBR! at !PATH_VAL! >> "!LOG_FILE!"
    
    if "!FIRST!"=="1" (
      set "WT_CMD=new-tab --title "!ABBR!" -d "!PATH_VAL!" --suppressApplicationTitle wsl.exe --cd "!PATH_VAL!" -- bash"
      set "FIRST=0"
    ) else (
      set "WT_CMD=!WT_CMD! ; new-tab --title "!ABBR!" -d "!PATH_VAL!" --suppressApplicationTitle wsl.exe --cd "!PATH_VAL!" -- bash"
    )
  )
)

REM Launch WT with all tabs
echo [%DATE% %TIME%] Launching WT with tabs >> "!LOG_FILE!"
pushd "%USERPROFILE%" >nul 2>&1
call "!WT_EXE!" -w new !WT_CMD!
popd >nul 2>&1

echo [%DATE% %TIME%] Tabs launched; exiting >> "!LOG_FILE!"
timeout /t 1 /nobreak
exit /b 0
