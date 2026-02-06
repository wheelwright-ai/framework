# WAI Helpers Library
# Version: 3.1.0
# Purpose: Shared functions for WAI workspace and project discovery

function Get-ProjectAbbreviation {
    param([string]$ProjectPath)
    
    $stateFile = Join-Path $ProjectPath "WAI-Spoke\WAI-State.json"
    if (Test-Path $stateFile) {
        try {
            $state = Get-Content -Raw $stateFile | ConvertFrom-Json
            if ($state.wheel.abbrev) { return $state.wheel.abbrev }
            if ($state.wheel.name) { return $state.wheel.name }
            if ($state._project_foundation.identity.name) { return $state._project_foundation.identity.name }
        } catch { }
    }
    
    # Fallback: auto-abbreviate
    $name = Split-Path $ProjectPath -Leaf
    if ($name -match 'wheelwright-ai/framework|wheelwright') { return 'WAI' }
    if ($name -match '^\w{1,4}$') { return $name.ToUpper() }
    return ($name.Substring(0, [Math]::Min(4, $name.Length))).ToUpper()
}

function Get-ActiveProjects {
    param(
        [string]$HubRegistryPath = "$env:USERPROFILE\wheelwright-hub\hub\hub-registry.json",
        [int]$DaysActive = 7,
        [int]$MaxProjects = 6
    )
    
    if (-not (Test-Path $HubRegistryPath)) {
        return @()
    }
    
    try {
        $registry = Get-Content -Raw $HubRegistryPath | ConvertFrom-Json
        $cutoffDate = (Get-Date).AddDays(-$DaysActive)
        
        $active = @()
        foreach ($wheel in $registry.wheels) {
            $lastSession = $wheel.last_session_timestamp
            if ($lastSession) {
                try {
                    $lastDate = [datetime]::Parse($lastSession)
                    if ($lastDate -gt $cutoffDate) {
                        $active += @{
                            name = $wheel.name
                            path = $wheel.path
                            lastSession = $lastDate
                            abbrev = Get-ProjectAbbreviation $wheel.path
                        }
                    }
                } catch { }
            }
        }
        
        return ($active | Sort-Object -Property lastSession -Descending | Select-Object -First $MaxProjects)
    } catch {
        return @()
    }
}

function Get-WslDistro {
    param([string]$Preference = $env:WAI_WSL_DISTRO)
    
    if ($Preference) {
        $distros = wsl.exe -l -q 2>$null
        if ($distros -contains $Preference) { return $Preference }
    }
    
    # Default to Ubuntu
    return "Ubuntu"
}

function ConvertTo-WslPath {
    param(
        [string]$WindowsPath,
        [string]$Distro = "Ubuntu"
    )
    
    if ($WindowsPath -match '^Z:') {
        return $WindowsPath -replace '^Z:', '' -replace '\\', '/'
    }
    
    if ($WindowsPath -match '^\\\\wsl\$\\([^\\]+)\\(.+)$') {
        return "/$($matches[2])" -replace '\\', '/'
    }
    
    if ($WindowsPath -match '^\\\\wsl\.localhost\\([^\\]+)\\(.+)$') {
        return "/$($matches[2])" -replace '\\', '/'
    }
    
    # Windows path - convert via wsl
    try {
        $result = wsl.exe -d $Distro wslpath -a $WindowsPath 2>$null
        if ($result) { return $result }
    } catch { }
    
    return $WindowsPath
}

Export-ModuleMember -Function Get-ProjectAbbreviation, Get-ActiveProjects, Get-WslDistro, ConvertTo-WslPath
