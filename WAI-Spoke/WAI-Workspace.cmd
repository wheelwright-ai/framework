@echo off
setlocal EnableDelayedExpansion

pushd "%~dp0" >nul 2>&1
set "PROJECT_DIR=%CD%"
for %%A in ("%PROJECT_DIR%\..") do set "ROOT_DIR=%%~fA"
set "LOG_FILE=%TEMP%\WAI-Workspace.log"
echo [%DATE% %TIME%] Launching WAI-Workspace from !PROJECT_DIR! > "%LOG_FILE%"
echo [%DATE% %TIME%] Root dir: !ROOT_DIR! >> "%LOG_FILE%"

set "STATE_FILE=%PROJECT_DIR%\WAI-State.json"
set "ABBR="
set "HUB_DIR="
set "WAI_PATHS_PRIMARY="
set "WAI_WIN_ROOT="
set "WAI_WIN_SPOKE="
set "WAI_WIN_HUB="
set "WAI_WSL_ROOT="
set "WAI_WSL_SPOKE="
set "WAI_WSL_HUB="

if exist "%STATE_FILE%" (
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $abbr=$j.wheel.abbrev; if ([string]::IsNullOrWhiteSpace($abbr)) { $abbr=Read-Host 'Enter project abbreviation (e.g., CRM)'; if (-not [string]::IsNullOrWhiteSpace($abbr)) { if (-not $j.wheel) { $j | Add-Member -NotePropertyName wheel -NotePropertyValue @{} }; $j.wheel.abbrev=$abbr; $j | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $p } }; $abbr } catch { '' }"`) do set "ABBR=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.ide_cmd } catch { '' }"`) do set "WAI_IDE_CMD=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.run_cmd } catch { '' }"`) do set "WAI_RUN_CMD=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.cli_cmd } catch { '' }"`) do set "WAI_CLI_CMD=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.hub_cmd } catch { '' }"`) do set "WAI_HUB_CMD=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.primary } catch { '' }"`) do set "WAI_PATHS_PRIMARY=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.windows.root } catch { '' }"`) do set "WAI_WIN_ROOT=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.windows.spoke } catch { '' }"`) do set "WAI_WIN_SPOKE=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.windows.hub } catch { '' }"`) do set "WAI_WIN_HUB=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.wsl.root } catch { '' }"`) do set "WAI_WSL_ROOT=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.wsl.spoke } catch { '' }"`) do set "WAI_WSL_SPOKE=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheel.workspace.paths.wsl.hub } catch { '' }"`) do set "WAI_WSL_HUB=%%A"
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $j.wheelwright.hub_path } catch { '' }"`) do set "HUB_DIR=%%A"
)

if not defined ABBR (
  for %%A in ("%PROJECT_DIR%") do set "ABBR=%%~nA"
)
echo [%DATE% %TIME%] ABBR=!ABBR! >> "%LOG_FILE%"

if not defined HUB_DIR set "HUB_DIR=%PROJECT_DIR%"

if not defined WAI_IDE_CMD set "WAI_IDE_CMD="
if not defined WAI_RUN_CMD set "WAI_RUN_CMD="
if not defined WAI_CLI_CMD set "WAI_CLI_CMD="
if not defined WAI_HUB_CMD set "WAI_HUB_CMD="

if defined WAI_PATHS_PRIMARY (
  if /i "!WAI_PATHS_PRIMARY!"=="windows" set "WAI_USE_WSL=0"
  if /i "!WAI_PATHS_PRIMARY!"=="wsl" set "WAI_USE_WSL=1"
)

if not defined WAI_USE_WSL (
  if /i "%PROJECT_DIR:~0,2%"=="Z:" set "WAI_USE_WSL=1"
)

if "!WAI_USE_WSL!"=="0" (
  if defined WAI_WIN_ROOT set "ROOT_DIR=!WAI_WIN_ROOT!"
  if defined WAI_WIN_SPOKE set "PROJECT_DIR=!WAI_WIN_SPOKE!"
  if defined WAI_WIN_HUB set "HUB_DIR=!WAI_WIN_HUB!"
)
if "!WAI_USE_WSL!"=="1" (
  set "WAI_WSL_DISTRO_INPUT="
  if defined WAI_WSL_DISTRO set "WAI_WSL_DISTRO_INPUT=!WAI_WSL_DISTRO!"
  if defined WAI_WSL_DISTRO_INPUT (
    for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$d=$env:WAI_WSL_DISTRO; if ($d) { $d.Trim() }"`) do set "WAI_WSL_DISTRO_INPUT=%%A"
  )
  if defined WAI_WSL_DISTRO_INPUT (
    set "WAI_WSL_DISTRO=!WAI_WSL_DISTRO_INPUT!"
  ) else (
    for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "[Console]::OutputEncoding=[Text.UTF8Encoding]::UTF8; $picked=''; foreach ($line in ^& wsl.exe -l -q) { $t=$line.Trim(); if ($t) { $picked=$t; break } }; $picked"`) do set "WAI_WSL_DISTRO=%%A"
  )
  set "WAI_WSL_DISTRO_CHECK="
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "[Console]::OutputEncoding=[Text.UTF8Encoding]::UTF8; $picked=''; foreach ($line in ^& wsl.exe -l -q) { $t=$line.Trim(); if ($t) { $picked=$t; break } }; $picked"`) do set "WAI_WSL_DISTRO_CHECK=%%A"
  if not defined WAI_WSL_DISTRO_INPUT (
    if defined WAI_WSL_DISTRO (
      if not exist "\\wsl$\\!WAI_WSL_DISTRO!\\." (
        if defined WAI_WSL_DISTRO_CHECK (
          for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$d='!WAI_WSL_DISTRO_CHECK!'; if ($d) { $d.Trim() }"`) do set "WAI_WSL_DISTRO=%%A"
          echo [%DATE% %TIME%] WSL distro fallback to "!WAI_WSL_DISTRO!" >> "%LOG_FILE%"
        )
      )
    )
  )
  if defined WAI_WSL_DISTRO_INPUT if not defined WAI_WSL_DISTRO (
    echo [%DATE% %TIME%] WSL distro "%WAI_WSL_DISTRO_INPUT%" not found in list; resetting >> "%LOG_FILE%"
  )
  if not defined WAI_WSL_DISTRO (
    echo [%DATE% %TIME%] WSL not available; falling back to cmd.exe >> "%LOG_FILE%"
    set "WAI_USE_WSL=0"
  ) else (
    wsl.exe -d "!WAI_WSL_DISTRO!" -- true >nul 2>&1
    if errorlevel 1 (
      echo [%DATE% %TIME%] WSL distro "%WAI_WSL_DISTRO%" not found; falling back to cmd.exe >> "%LOG_FILE%"
      set "WAI_USE_WSL=0"
    )
  )
)
if "!WAI_USE_WSL!"=="1" (
  if defined WAI_WSL_SPOKE (
    set "WSL_PATH=!WAI_WSL_SPOKE!"
  ) else if /i "!PROJECT_DIR:~0,3!"=="Z:\" (
    set "WSL_PATH=!PROJECT_DIR:Z:\=!"
    set "WSL_PATH=!WSL_PATH:\=/!"
    set "WSL_PATH=/!WSL_PATH!"
  ) else (
    set "WSL_PATH=!PROJECT_DIR!"
  )

  if defined WAI_WSL_ROOT (
    set "WSL_ROOT=!WAI_WSL_ROOT!"
  ) else if /i "!ROOT_DIR:~0,3!"=="Z:\" (
    set "WSL_ROOT=!ROOT_DIR:Z:\=!"
    set "WSL_ROOT=!WSL_ROOT:\=/!"
    set "WSL_ROOT=/!WSL_ROOT!"
  ) else (
    set "WSL_ROOT=!ROOT_DIR!"
  )

  if defined WAI_WSL_HUB (
    set "WSL_HUB=!WAI_WSL_HUB!"
  ) else if /i "!HUB_DIR:~0,3!"=="Z:\" (
    set "WSL_HUB=!HUB_DIR:Z:\=!"
    set "WSL_HUB=!WSL_HUB:\=/!"
    set "WSL_HUB=/!WSL_HUB!"
  ) else (
    set "WSL_HUB=!HUB_DIR!"
  )
)

echo [%DATE% %TIME%] IDE_CMD=!WAI_IDE_CMD! >> "%LOG_FILE%"
echo [%DATE% %TIME%] RUN_CMD=!WAI_RUN_CMD! >> "%LOG_FILE%"
echo [%DATE% %TIME%] CLI_CMD=!WAI_CLI_CMD! >> "%LOG_FILE%"
echo [%DATE% %TIME%] HUB_CMD=!WAI_HUB_CMD! >> "%LOG_FILE%"
echo [%DATE% %TIME%] PATHS_PRIMARY=!WAI_PATHS_PRIMARY! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WIN_ROOT=!WAI_WIN_ROOT! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WIN_SPOKE=!WAI_WIN_SPOKE! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WIN_HUB=!WAI_WIN_HUB! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_ROOT_STATE=!WAI_WSL_ROOT! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_SPOKE_STATE=!WAI_WSL_SPOKE! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_HUB_STATE=!WAI_WSL_HUB! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WAI_USE_WSL=!WAI_USE_WSL! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WAI_WSL_DISTRO_INPUT=!WAI_WSL_DISTRO_INPUT! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_DISTRO=!WAI_WSL_DISTRO! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_ROOT=!WSL_ROOT! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_PATH=!WSL_PATH! >> "%LOG_FILE%"
echo [%DATE% %TIME%] WSL_HUB=!WSL_HUB! >> "%LOG_FILE%"

if "!WAI_USE_WSL!"=="1" goto :launch

if defined HUB_DIR (
  set "WAI_HUB_CMD="
)

:launch
set "WT_EXE="
for /f "delims=" %%A in ('where wt.exe 2^>nul') do set "WT_EXE=%%A"
if not defined WT_EXE if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" set "WT_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"
echo [%DATE% %TIME%] WT_EXE=%WT_EXE% >> "%LOG_FILE%"
set "WT_START_DIR=%USERPROFILE%"

if not defined WT_EXE (
  echo Windows Terminal not found. Opening three command windows...
  echo [%DATE% %TIME%] WT not found. Falling back to cmd.exe >> "%LOG_FILE%"
    start "🧠 %ABBR%-IDE" cmd.exe /k "pushd \"%ROOT_DIR%\""
    start "🚀 %ABBR%-RUN" cmd.exe /k "pushd \"%ROOT_DIR%\""
    if exist "%ROOT_DIR%\\WAI-CLI" (
      start "🧭 %ABBR%-CLI" cmd.exe /k "pushd \"%ROOT_DIR%\" && \"%ROOT_DIR%\\WAI-CLI\""
    ) else (
      start "🧭 %ABBR%-CLI" cmd.exe /k "pushd \"%ROOT_DIR%\" && WAI-CLI"
    )
  if "%WAI_DEBUG%"=="1" pause
  goto :eof
)

if "!WAI_USE_WSL!"=="1" (
  set "WT_WSL_PROFILE="
  if defined WAI_WSL_DISTRO set "WT_WSL_PROFILE=-p !WAI_WSL_DISTRO!"
  set "UNC_SPOKE="
  set "UNC_ROOT="
  set "UNC_HUB="
  if defined WAI_WSL_DISTRO (
    if defined WSL_PATH (
      set "UNC_SPOKE=!WSL_PATH:/=\!"
      set "UNC_SPOKE=\\wsl$\\!WAI_WSL_DISTRO!!UNC_SPOKE!"
    )
    if defined WSL_ROOT (
      set "UNC_ROOT=!WSL_ROOT:/=\!"
      set "UNC_ROOT=\\wsl$\\!WAI_WSL_DISTRO!!UNC_ROOT!"
    )
    if defined WSL_HUB (
      set "UNC_HUB=!WSL_HUB:/=\!"
      set "UNC_HUB=\\wsl$\\!WAI_WSL_DISTRO!!UNC_HUB!"
    )
  )
  set "WT_DIR_SPOKE="
  set "WT_DIR_ROOT="
  set "WT_DIR_HUB="
  if defined UNC_SPOKE set WT_DIR_SPOKE=-d "!UNC_SPOKE!"
  if defined UNC_ROOT set WT_DIR_ROOT=-d "!UNC_ROOT!"
  if defined UNC_HUB (
    if exist "!UNC_HUB!" (set WT_DIR_HUB=-d "!UNC_HUB!") else (set "WT_DIR_HUB=!WT_DIR_SPOKE!")
  ) else (
    set "WT_DIR_HUB=!WT_DIR_SPOKE!"
  )
  if not defined WT_DIR_SPOKE if defined WSL_PATH set WT_DIR_SPOKE=-d "!WSL_PATH!"
  if not defined WT_DIR_ROOT if defined WSL_ROOT set WT_DIR_ROOT=-d "!WSL_ROOT!"
  if not defined WT_DIR_HUB if defined WSL_HUB set WT_DIR_HUB=-d "!WSL_HUB!"
  echo [%DATE% %TIME%] UNC_SPOKE=!UNC_SPOKE! >> "%LOG_FILE%"
  echo [%DATE% %TIME%] UNC_ROOT=!UNC_ROOT! >> "%LOG_FILE%"
  echo [%DATE% %TIME%] UNC_HUB=!UNC_HUB! >> "%LOG_FILE%"
  echo [%DATE% %TIME%] WT_DIR_SPOKE=!WT_DIR_SPOKE! >> "%LOG_FILE%"
  echo [%DATE% %TIME%] WT_DIR_ROOT=!WT_DIR_ROOT! >> "%LOG_FILE%"
  echo [%DATE% %TIME%] WT_DIR_HUB=!WT_DIR_HUB! >> "%LOG_FILE%"
  start "" /D "%WT_START_DIR%" "%WT_EXE%" -w new --title "%ABBR% - IDE" --suppressApplicationTitle --tabColor "#4A90E2" wsl.exe -d "!WAI_WSL_DISTRO!" --cd "!WSL_ROOT!"
  timeout /t 1 /nobreak >nul
  start "" /D "%WT_START_DIR%" "%WT_EXE%" -w 0 new-tab --title "%ABBR% - RUN" --suppressApplicationTitle --tabColor "#E74C3C" wsl.exe -d "!WAI_WSL_DISTRO!" --cd "!WSL_ROOT!"
  start "" /D "%WT_START_DIR%" "%WT_EXE%" -w 0 new-tab --title "%ABBR% - CLI" --suppressApplicationTitle --tabColor "#2ECC71" wsl.exe -d "!WAI_WSL_DISTRO!" --cd "!WSL_ROOT!" --exec bash -lc "./WAI-CLI && exec bash"
) else (
  set "CLI_BIN=WAI-CLI"
  if exist "%ROOT_DIR%\\WAI-CLI" set "CLI_BIN=%ROOT_DIR%\\WAI-CLI"
  start "" "%WT_EXE%" -w 0 ^
    new-tab --title "%ABBR% - IDE" --tabColor "#4A90E2" -d "%ROOT_DIR%" cmd.exe ^
    ; new-tab --title "%ABBR% - RUN" --tabColor "#E74C3C" -d "%ROOT_DIR%" cmd.exe ^
    ; new-tab --title "%ABBR% - CLI" --tabColor "#2ECC71" -d "%ROOT_DIR%" cmd.exe /k "%CLI_BIN%"
)
echo [%DATE% %TIME%] WT launch attempted. >> "%LOG_FILE%"
if "%WAI_DEBUG%"=="1" pause
