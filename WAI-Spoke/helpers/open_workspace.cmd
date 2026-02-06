@echo off
REM WAI-Workspace.cmd - Launch IDE/RUN/CLI tabs
REM Version: 3.1.0
REM Location: WAI-Spoke/helpers/

setlocal EnableDelayedExpansion

REM Resolve paths from helpers/ location
set "HELPERS_DIR=%~dp0"
if "%HELPERS_DIR:~-1%"=="\" set "HELPERS_DIR=%HELPERS_DIR:~0,-1%"
set "SPOKE_DIR=%HELPERS_DIR:~0,-8%"
set "PROJECT_DIR=%SPOKE_DIR:~0,-10%"

set "LOG_FILE=%HELPERS_DIR%\WAI-Workspace.log"
echo [%DATE% %TIME%] WAI-Workspace start from helpers >> "!LOG_FILE!"
echo HELPERS_DIR=!HELPERS_DIR! >> "!LOG_FILE!"
echo SPOKE_DIR=!SPOKE_DIR! >> "!LOG_FILE!"
echo PROJECT_DIR=!PROJECT_DIR! >> "!LOG_FILE!"

REM Extract abbreviation from WAI-State.json
set "ABBR="
set "STATE_FILE=!SPOKE_DIR!\WAI-State.json"
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
  for %%A in ("!PROJECT_DIR:~0,-1!") do set "ABBR=%%~nA"
)

echo [%DATE% %TIME%] ABBR=!ABBR! >> "!LOG_FILE!"

REM Find Windows Terminal
set "WT_EXE="
for /f "delims=" %%A in ('where wt.exe 2^>nul') do set "WT_EXE=%%A"
if not defined WT_EXE if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" set "WT_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"

echo [%DATE% %TIME%] WT_EXE=!WT_EXE! >> "!LOG_FILE!"

if not defined WT_EXE (
  echo [%DATE% %TIME%] WT not found. Using cmd fallback >> "!LOG_FILE!"
  start "!ABBR! - IDE" cmd.exe /k "cd /d !PROJECT_DIR!"
  start "!ABBR! - RUN" cmd.exe /k "cd /d !PROJECT_DIR!"
  start "!ABBR! - CLI" cmd.exe /k "cd /d !PROJECT_DIR! && WAI status"
  timeout /t 2 /nobreak
  exit /b 0
)

REM Launch WSL tabs via WT
set "WSL_DISTRO=Ubuntu"
if defined WAI_WSL_DISTRO set "WSL_DISTRO=!WAI_WSL_DISTRO!"

echo [%DATE% %TIME%] Launching WT with WSL tabs >> "!LOG_FILE!"
pushd "%USERPROFILE%" >nul 2>&1
call "!WT_EXE!" -w new ^
  new-tab --title "!ABBR! - IDE" --tabColor "#4A90E2" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -i ^
  ; new-tab --title "!ABBR! - RUN" --tabColor "#E74C3C" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -i ^
  ; new-tab --title "!ABBR! - CLI" --tabColor "#2ECC71" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -i
popd >nul 2>&1

echo [%DATE% %TIME%] Tabs launched >> "!LOG_FILE!"
timeout /t 1 /nobreak
exit /b 0
