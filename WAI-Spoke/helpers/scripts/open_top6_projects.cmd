@echo off
REM wai-multi-project-tabs.cmd - Launch tabs for top 6 active projects
REM Version: 3.1.0
REM Location: WAI-Spoke/helpers/

setlocal EnableDelayedExpansion

set "HELPERS_DIR=%~dp0"
if "%HELPERS_DIR:~-1%"=="\" set "HELPERS_DIR=%HELPERS_DIR:~0,-1%"
set "SPOKE_ROOT=%HELPERS_DIR:~0,-8%"
set "PROJECT_ROOT=%SPOKE_ROOT:~0,-10%"

REM Load hub path from WAI-State.json
set "STATE_FILE=%SPOKE_ROOT%\WAI-State.json"
set "HUB_PATH="
if exist "!STATE_FILE!" (
  for /f "usebackq tokens=* delims=" %%A in (`powershell -NoProfile -Command "$j = Get-Content -Raw '!STATE_FILE!' | ConvertFrom-Json; $j.wheelwright.hub_path"`) do (
    set "HUB_PATH=%%A"
  )
)

REM Logs in helpers/output/
set "LOG_FILE=%HELPERS_DIR%\output\wai-multi-project-tabs.log"
echo [%DATE% %TIME%] Starting multi-project launcher >> "!LOG_FILE!"

REM Hub registry - use configured path or default
if defined HUB_PATH (
  REM Convert WSL path to Windows path
  for /f "usebackq tokens=* delims=" %%A in (`powershell -NoProfile -Command "wsl wslpath -w '!HUB_PATH!' 2>$null"`) do (
    set "HUB_PATH_WIN=%%A"
  )
  if defined HUB_PATH_WIN (
    set "HUB_REGISTRY=!HUB_PATH_WIN!\hub\hub-registry.json"
  ) else (
    set "HUB_REGISTRY=%USERPROFILE%\wheelwright-hub\hub\hub-registry.json"
  )
) else (
  set "HUB_REGISTRY=%USERPROFILE%\wheelwright-hub\hub\hub-registry.json"
)

echo [%DATE% %TIME%] HUB_PATH=!HUB_PATH! HUB_REGISTRY=!HUB_REGISTRY! >> "!LOG_FILE!"

if not exist "!HUB_REGISTRY!" (
  echo Hub registry not found at !HUB_REGISTRY! >> "!LOG_FILE!"
  echo Hub registry not found. Create hub first: WAI hub create
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Hub registry found >> "!LOG_FILE!"

REM PowerShell discovery
set "PS_OUT=%HELPERS_DIR%\output\wai_projects.txt"
set "PS_ERR=%HELPERS_DIR%\output\wai_projects_err.txt"
del /q "!PS_OUT!" 2>nul
del /q "!PS_ERR!" 2>nul

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
  "}" > "!PS_OUT!" 2> "!PS_ERR!"

if exist "!PS_ERR!" (
  for /f "usebackq delims=" %%E in ("!PS_ERR!") do (
    echo [%DATE% %TIME%] PS Error: %%E >> "!LOG_FILE!"
  )
)

if not exist "!PS_OUT!" (
  echo PowerShell failed. Check !LOG_FILE!
  type "!LOG_FILE!"
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
  echo Windows Terminal not found.
  pause
  exit /b 1
)

REM Build WT launch
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

echo [%DATE% %TIME%] Launching WT >> "!LOG_FILE!"
call "!WT_EXE!" !WT_ARGS!
timeout /t 1 /nobreak
exit /b 0
