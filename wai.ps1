# Wheelwright CLI PowerShell Wrapper
# Usage: .\wai.ps1 <command> [options]
#        wai <command> [options]  (if added to profile)

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CliScript = Join-Path $ScriptDir "WAI-CLI"

# Call Python with the WAI-CLI wrapper
& python3 $CliScript @Arguments
