$ErrorActionPreference = 'Stop'
$solidCraftApp = 'C:\Program Files\SolidCraft\solidcraft.exe'
if (-not (Test-Path -LiteralPath $solidCraftApp)) {
    throw "SolidCraft was not found at $solidCraftApp"
}
$listener = Get-NetTCPConnection -LocalPort 7878 -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host 'Port 7878 is already listening. Verify that it belongs to the SolidCraft instance you want to use.'
    return
}
# The user invokes this script specifically to open the interactive CAD window.
Start-Process -FilePath $solidCraftApp -ArgumentList @('--control', '7878') -WorkingDirectory $PSScriptRoot -WindowStyle Normal
Write-Host 'SolidCraft started with control port 7878. Keep it open, then restart Codex to load the MCP connection.'
