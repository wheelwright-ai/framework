@echo off
REM WAI-Workspace.cmd - Refactored for helpers directory
REM Version: 3.1.0
REM Purpose: Launch workspace tabs and exit
REM
REM Location: WAI-Spoke/helpers/WAI-Workspace.cmd
REM (Also available at WAI-Spoke/ root for backward compatibility)

setlocal EnableDelayedExpansion

REM Get the script directory (handles both root and helpers/ locations)
set "SCRIPT_DIR=%~dp0"
if /i "!SCRIPT_DIR:~-9!"=="helpers\" (
  set "SCRIPT_DIR=!SCRIPT_DIR:~0,-9!"
)
set "PROJECT_DIR=!SCRIPT_DIR!"
set "HELPERS_DIR=!PROJECT_DIR!helpers\"

REM Create log
set "LOG_FILE=!PROJECT_DIR!WAI-Workspace.log"
echo [%DATE% %TIME%] WAI-Workspace start from !SCRIPT_DIR! > "!LOG_FILE!"

REM Extract project abbreviation from WAI-State.json
set "ABBR="
set "STATE_FILE=!PROJECT_DIR!WAI-State.json"
if exist "!STATE_FILE!" (
  for /f "usebackq delims=" %%A in (`findstr /i "\"abbrev\"" "!STATE_FILE!"`) do (
    for /f "tokens=1,2 delims=:" %%K in ("%%A") do (
      set "ABBR=%%L"
    )
  )
  set "ABBR=!ABBR:\"=!"
  set "ABBR=!ABBR: =!"
  set "ABBR=!ABBR:,=!"
)
if "!ABBR!"=="" (
  for %%A in ("!PROJECT_DIR!") do set "ABBR=%%~nA"
)

echo [%DATE% %TIME%] ABBR=!ABBR! >> "!LOG_FILE!"

REM Find Windows Terminal
set "WT_EXE="
for /f "delims=" %%A in ('where wt.exe 2^>nul') do set "WT_EXE=%%A"
if not defined WT_EXE if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" set "WT_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"

echo [%DATE% %TIME%] WT_EXE=!WT_EXE! >> "!LOG_FILE!"

if not defined WT_EXE (
  echo [%DATE% %TIME%] WT not found; using cmd.exe fallback >> "!LOG_FILE!"
  start "!ABBR! - IDE" cmd.exe /k "cd /d !PROJECT_DIR!"
  start "!ABBR! - RUN" cmd.exe /k "cd /d !PROJECT_DIR!"
  start "!ABBR! - CLI" cmd.exe /k "cd /d !PROJECT_DIR! && WAI status"
  timeout /t 2 /nobreak
  exit /b 0
)

REM Launch WSL tabs via Windows Terminal
set "WSL_DISTRO=Ubuntu"
if defined WAI_WSL_DISTRO set "WSL_DISTRO=!WAI_WSL_DISTRO!"

echo [%DATE% %TIME%] Launching WSL tabs for !ABBR! >> "!LOG_FILE!"

pushd "%USERPROFILE%" >nul 2>&1
call "!WT_EXE!" -w new ^
  new-tab --title "!ABBR! - IDE" --tabColor "#4A90E2" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -lc "cd !PROJECT_DIR! && bash" ^
  ; new-tab --title "!ABBR! - RUN" --tabColor "#E74C3C" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -lc "cd !PROJECT_DIR! && bash" ^
  ; new-tab --title "!ABBR! - CLI" --tabColor "#2ECC71" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -lc "cd !PROJECT_DIR! && WAI status && bash"
popd >nul 2>&1

echo [%DATE% %TIME%] Tabs launched; exiting >> "!LOG_FILE!"
timeout /t 1 /nobreak
exit /b 0
