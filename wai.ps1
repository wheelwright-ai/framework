#!/usr/bin/env pwsh
# Wheelwright CLI - PowerShell wrapper

$FrameworkRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = 'C:\Python313\python.exe'

& $PythonExe -m wai.cli.main @args
