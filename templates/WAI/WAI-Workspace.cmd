@echo off
setlocal EnableDelayedExpansion

set "WAI_WORKSPACE_VERSION=2026.01.05"

set "LOG_FALLBACK=%TEMP%\WAI-Workspace.log"
echo [%DATE% %TIME%] WAI-Workspace start > "%LOG_FALLBACK%"

pushd "%~dp0" >nul 2>&1
set "PROJECT_DIR=%CD%"
for %%A in ("%PROJECT_DIR%\..") do set "ROOT_DIR=%%~fA"
set "LOG_FILE=%PROJECT_DIR%\WAI-Workspace.log"
echo [%DATE% %TIME%] WAI-Workspace running >> "%LOG_FALLBACK%"
echo [%DATE% %TIME%] WAI-Workspace running > "%LOG_FILE%"
echo [%DATE% %TIME%] ENV: WAI_WSL_DISTRO=%WAI_WSL_DISTRO% WAI_WORKSPACE_TEST=%WAI_WORKSPACE_TEST% WAI_FORCE_WSL=%WAI_FORCE_WSL% >> "%LOG_FILE%"
set "WT_DISABLE_FILE=%PROJECT_DIR%\\.wai-wt-disabled"
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
  for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$p='%STATE_FILE%'; try { $j=Get-Content -Raw $p | ConvertFrom-Json; $vals=@{ ABBR=$j.wheel.abbrev; WAI_IDE_CMD=$j.wheel.workspace.ide_cmd; WAI_RUN_CMD=$j.wheel.workspace.run_cmd; WAI_CLI_CMD=$j.wheel.workspace.cli_cmd; WAI_HUB_CMD=$j.wheel.workspace.hub_cmd; WAI_PATHS_PRIMARY=$j.wheel.workspace.paths.primary; WAI_WIN_ROOT=$j.wheel.workspace.paths.windows.root; WAI_WIN_SPOKE=$j.wheel.workspace.paths.windows.spoke; WAI_WIN_HUB=$j.wheel.workspace.paths.windows.hub; WAI_WSL_ROOT=$j.wheel.workspace.paths.wsl.root; WAI_WSL_SPOKE=$j.wheel.workspace.paths.wsl.spoke; WAI_WSL_HUB=$j.wheel.workspace.paths.wsl.hub; HUB_DIR=$j.wheelwright.hub_path }; $vals.GetEnumerator() | ForEach-Object { $v=$_.Value; if ($null -eq $v) { $v='' } else { $v=[string]$v }; '{0}={1}' -f $_.Key, $v } } catch { }"`) do (
    for /f "tokens=1* delims==" %%K in ("%%A") do set "%%K=%%L"
  )
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
    for /f "tokens=* delims= " %%A in ("!WAI_WSL_DISTRO_INPUT!") do set "WAI_WSL_DISTRO_INPUT=%%A"
  )
  if defined WAI_WSL_DISTRO_INPUT (
    set "WAI_WSL_DISTRO=!WAI_WSL_DISTRO_INPUT!"
  )
  if defined WAI_WSL_DISTRO (
    wsl.exe -d "!WAI_WSL_DISTRO!" -- true >nul 2>&1
    if errorlevel 1 (
      echo [%DATE% %TIME%] Invalid WSL distro "%WAI_WSL_DISTRO%"; using default >> "%LOG_FILE%"
      set "WAI_WSL_DISTRO="
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
    start "%ABBR%-IDE" cmd.exe /k "pushd \"%ROOT_DIR%\""
    start "%ABBR%-RUN" cmd.exe /k "pushd \"%ROOT_DIR%\""
    if exist "%ROOT_DIR%\\WAI-CLI" (
      start "%ABBR%-CLI" cmd.exe /k "pushd \"%ROOT_DIR%\" && \"%ROOT_DIR%\\WAI-CLI\""
    ) else (
      start "%ABBR%-CLI" cmd.exe /k "pushd \"%ROOT_DIR%\" && WAI-CLI"
    )
  if "%WAI_DEBUG%"=="1" pause
  goto :eof
)

if "!WAI_USE_WSL!"=="1" (
  set "WSL_DISTRO_ARG="
  if defined WAI_WSL_DISTRO set "WSL_DISTRO_ARG=-d \"!WAI_WSL_DISTRO!\""
  if not defined WAI_USE_WT set "WAI_USE_WT=1"
  if "%WAI_FORCE_WT%"=="1" if exist "!WT_DISABLE_FILE!" del /q "!WT_DISABLE_FILE!" >nul 2>&1
  if exist "!WT_DISABLE_FILE!" set "WAI_USE_WT=0"
  if "%WAI_FORCE_WT%"=="1" set "WAI_USE_WT=1"
  echo [%DATE% %TIME%] WAI_USE_WT=!WAI_USE_WT! >> "%LOG_FILE%"
  echo [%DATE% %TIME%] Entered WSL block >> "%LOG_FILE%"
  if "%WAI_WORKSPACE_TEST%"=="1" (
    echo [%DATE% %TIME%] Running workspace self-test >> "%LOG_FILE%"
    echo [%DATE% %TIME%] WAI_WORKSPACE_TEST=1 >> "%LOG_FILE%"
    wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash -lc "pwd" >> "%LOG_FILE%" 2>&1
    wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_PATH!" -- bash -lc "pwd" >> "%LOG_FILE%" 2>&1
    wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash -lc "ls -l ./WAI-CLI" >> "%LOG_FILE%" 2>&1
    wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash -lc "bash ./WAI-Spoke/wai-cli-launch.sh" >> "%LOG_FILE%" 2>&1
    goto :eof
  )
  if "!WAI_USE_WT!"=="1" (
    set "WT_FAILED=0"
    echo [%DATE% %TIME%] WT cmd: %WT_EXE% -w new new-tab --title "%ABBR% - IDE" --tabColor "#4A90E2" --suppressApplicationTitle wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-shell.sh "%ABBR% - IDE" ; new-tab --title "%ABBR% - RUN" --tabColor "#E74C3C" --suppressApplicationTitle wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-shell.sh "%ABBR% - RUN" ; new-tab --title "%ABBR% - CLI" --tabColor "#2ECC71" --suppressApplicationTitle wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-cli-launch.sh "%ABBR% - CLI" >> "%LOG_FILE%"
    call "%WT_EXE%" -w new ^
      new-tab --title "%ABBR% - IDE" --tabColor "#4A90E2" --suppressApplicationTitle wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-shell.sh "%ABBR% - IDE" ^
      ; new-tab --title "%ABBR% - RUN" --tabColor "#E74C3C" --suppressApplicationTitle wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-shell.sh "%ABBR% - RUN" ^
      ; new-tab --title "%ABBR% - CLI" --tabColor "#2ECC71" --suppressApplicationTitle wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-cli-launch.sh "%ABBR% - CLI"
    echo [%DATE% %TIME%] WT exit=%ERRORLEVEL% >> "%LOG_FILE%"
    if errorlevel 1 set "WT_FAILED=1"
    if "%WAI_FORCE_WSL%"=="1" set "WT_FAILED=1"
  ) else (
    set "WT_FAILED=1"
  )
  if "!WT_FAILED!"=="1" (
    echo [%DATE% %TIME%] WT skipped/failed; opening standalone WSL windows. >> "%LOG_FILE%"
    if "%WAI_FORCE_WT%"=="1" (
      echo [%DATE% %TIME%] WT failed but WAI_FORCE_WT=1 set; not disabling WT. >> "%LOG_FILE%"
    ) else (
      echo [%DATE% %TIME%] WT disabled for next run; remove "!WT_DISABLE_FILE!" to retry. >> "%LOG_FILE%"
      echo WT disabled due to failure > "!WT_DISABLE_FILE!"
    )
    start "" "%ComSpec%" /k wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-shell.sh
    start "" "%ComSpec%" /k wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-shell.sh
    start "" "%ComSpec%" /k wsl.exe !WSL_DISTRO_ARG! --cd "!WSL_ROOT!" -- bash ./WAI-Spoke/wai-cli-launch.sh
  )
  if "%WAI_CLOSE_CMD%"=="1" exit /b 0
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
