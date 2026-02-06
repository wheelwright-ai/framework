@echo off
REM open_workspace_impl.cmd - Implementation
REM Location: WAI-Spoke/helpers/resources/

setlocal EnableDelayedExpansion

REM Resolve paths
set "RESOURCES_DIR=%~dp0"
if "%RESOURCES_DIR:~-1%"=="\" set "RESOURCES_DIR=%RESOURCES_DIR:~0,-1%"
set "HELPERS_DIR=%RESOURCES_DIR:~0,-10%"
set "SPOKE_DIR=%HELPERS_DIR:~0,-8%"
set "PROJECT_DIR=%SPOKE_DIR:~0,-10%"

set "LOG_FILE=%HELPERS_DIR%\output\open_workspace.log"
echo [%DATE% %TIME%] open_workspace start >> "!LOG_FILE!"

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

if not defined WT_EXE (
  echo [%DATE% %TIME%] WT not found >> "!LOG_FILE!"
  start "!ABBR! - IDE" cmd.exe /k "cd /d !PROJECT_DIR!"
  start "!ABBR! - RUN" cmd.exe /k "cd /d !PROJECT_DIR!"
  start "!ABBR! - CLI" cmd.exe /k "cd /d !PROJECT_DIR! && WAI status"
  exit /b 0
)

REM Launch WSL tabs
set "WSL_DISTRO=Ubuntu"
if defined WAI_WSL_DISTRO set "WSL_DISTRO=!WAI_WSL_DISTRO!"

echo [%DATE% %TIME%] Launching WT >> "!LOG_FILE!"
pushd "%USERPROFILE%" >nul 2>&1
call "!WT_EXE!" -w new ^
  new-tab --title "!ABBR! - IDE" --tabColor "#4A90E2" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -i ^
  ; new-tab --title "!ABBR! - RUN" --tabColor "#E74C3C" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -i ^
  ; new-tab --title "!ABBR! - CLI" --tabColor "#2ECC71" -d "%USERPROFILE%" wsl.exe -d !WSL_DISTRO! --cd "!PROJECT_DIR!" -- bash -i
popd >nul 2>&1

echo [%DATE% %TIME%] Complete >> "!LOG_FILE!"
exit /b 0
