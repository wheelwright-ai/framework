@echo off
REM Wheelwright CLI Batch Wrapper for Windows
REM Usage: wai <command> [options]

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Call Python with the WAI-CLI wrapper
python3 "%SCRIPT_DIR%WAI-CLI" %*

endlocal
