@echo off
REM wai-multi-project-tabs.cmd - Launch tabs for top 6 active projects
REM Version: 3.1.0
REM Location: WAI-Spoke/ root (not in helpers/)

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_ROOT=%SCRIPT_DIR:~0,-10%"

set "LOG_FILE=%PROJECT_ROOT%\wai-multi-project-tabs.log"
echo [%DATE% %TIME%] Starting multi-project launcher >> "!LOG_FILE!"

REM Hub registry location
set "HUB_REGISTRY=%USERPROFILE%\wheelwright-hub\hub\hub-registry.json"

if not exist "!HUB_REGISTRY!" (
  echo Hub registry not found at !HUB_REGISTRY! >> "!LOG_FILE!"
  echo Hub registry not found. Create hub first: WAI hub create
  echo.
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Found hub registry >> "!LOG_FILE!"

REM PowerShell to discover and format projects
set "PS_OUT=%TEMP%\wai_projects.txt"
del /q "!PS_OUT!" 2>nul
(
  powershell -NoProfile -Command ^
    "$h = Get-Content -Raw '%HUB_REGISTRY%' ^| ConvertFrom-Json; " ^
    "$c = (Get-Date).AddDays(-7); " ^
    "$a = @(); " ^
    "foreach ($w in $h.wheels) { if ($w.last_session_timestamp) { try { if ([datetime]::Parse($w.last_session_timestamp) -gt $c) { $a += $w } } catch {} } } " ^
    "$a ^| Sort-Object @{E={[datetime]::Parse($_.last_session_timestamp)}} -Desc ^| Select -First 6 ^| ForEach { " ^
    "  $abbr = $_.abbrev; " ^
    "  if (-not $abbr) { $abbr = $_.name }; " ^
    "  if (-not $abbr) { $abbr = (Split-Path $_.path -Leaf).Substring(0, 4) }; " ^
    "  '{0}|{1}' -f $abbr, $_.path " ^
    "}"
) > "!PS_OUT!" 2>nul

if not exist "!PS_OUT!" (
  echo [%DATE% %TIME%] PowerShell failed >> "!LOG_FILE!"
  echo PowerShell discovery failed. Check !LOG_FILE!
  pause
  exit /b 1
)

set "PROJECT_COUNT=0"
for /f "usebackq delims=" %%L in ("!PS_OUT!") do (
  set /a PROJECT_COUNT+=1
  set "PROJ_!PROJECT_COUNT!=%%L"
)

if "!PROJECT_COUNT!"=="0" (
  echo [%DATE% %TIME%] No active projects found >> "!LOG_FILE!"
  echo No active projects found in the last 7 days.
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Found !PROJECT_COUNT! projects >> "!LOG_FILE!"

REM Find WT
set "WT_EXE="
for /f "delims=" %%A in ('where wt.exe 2^>nul') do set "WT_EXE=%%A"
if not defined WT_EXE (
  echo Windows Terminal not found. Install it first.
  pause
  exit /b 1
)

REM Build WT launch command
set "WT_ARGS=-w new"
for /L %%I in (1,1,!PROJECT_COUNT!) do (
  set "LINE=!PROJ_%%I!"
  for /f "tokens=1,2 delims=^|" %%A in ("!LINE!") do (
    set "ABBR=%%A"
    set "PATH_PROJ=%%B"
    
    echo [%DATE% %TIME%] Tab %%I: !ABBR! ^(!PATH_PROJ!^) >> "!LOG_FILE!"
    
    if %%I gtr 1 set "WT_ARGS=!WT_ARGS! ;"
    set "WT_ARGS=!WT_ARGS! new-tab --title "!ABBR!" -d "!PATH_PROJ!" wsl.exe --cd "!PATH_PROJ!" -- bash"
  )
)

REM Launch
echo [%DATE% %TIME%] Launching WT with !PROJECT_COUNT! tabs >> "!LOG_FILE!"
call "!WT_EXE!" !WT_ARGS!

echo [%DATE% %TIME%] Launcher complete >> "!LOG_FILE!"
timeout /t 1 /nobreak
exit /b 0
