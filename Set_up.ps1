# Get the ID and name of the current user
$myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$myWindowsPrincipal = New-Object System.Security.Principal.WindowsPrincipal($myWindowsID)

# Check to see if we're currently running "as Administrator"
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

if (-not ($myWindowsPrincipal.IsInRole($adminRole))) {
    # We are not running as Administrator, so reopen the script as Administrator
    $newProcess = New-Object System.Diagnostics.ProcessStartInfo 'PowerShell';

    # Specify the PowerShell script to run
    # $newProcess.Arguments = "& '" + (Get-AuthenticatingUser).Path + "'" # Not sure if Get-AuthenticatingUser works here, need to check

    # This works:
    $newProcess.Arguments = "& '" + $MyInvocation.MyCommand.Path + "'"

    # Run the PowerShell process as Administrator
    $newProcess.Verb = 'runas';

    [System.Diagnostics.Process]::Start($newProcess);

    # Exit the current non-elevated process
    exit;
}

netsh wlan set hostednetwork mode=allow ssid="TestHotspot" key="password"

Restart-Service -Name "WlanSvc" -Force
Start-Sleep -Seconds 3  # Optional: Wait for the service to restart


netsh wlan start hostednetwork

# Find the virtual adapter (assumes it's named 'vEthernet (Mobile Hotspot)' or similar)
$adapter = Get-NetAdapter | Where-Object {$_.InterfaceDescription -like "Microsoft Hosted Network Virtual Adapter" -or $_.Name -like "*Hotspot*"}

if ($adapter) {
    netsh interface ip set address "$($adapter.Name)" static 192.168.137.1 255.255.255.0
} else {
    Write-Host "Hotspot adapter not found!"
}

# Create symbolic link to C:\Users\Public
$linkPath = "list_files"
$targetPath = "C:\Users\Public"

# Check if the item at $linkPath exists
if (Test-Path $linkPath) {
    # If it exists, check if it's already a symbolic link to the correct target
    $item = Get-Item $linkPath
    if ($item.LinkType -eq "SymbolicLink" -and $item.Target -eq $targetPath) {
        Write-Host "Symbolic link '$linkPath' to '$targetPath' already exists."
    } else {
        # If it's not the correct symbolic link (or not a symbolic link at all), remove it
        Write-Host "Removing existing item at '$linkPath' before creating symbolic link."
        Remove-Item $linkPath -Force
        # Now create the symbolic link
        cmd /c mklink /d $linkPath $targetPath
        Write-Host "Symbolic link '$linkPath' to '$targetPath' created."
    }
} else {
    # If the item doesn't exist, create the symbolic link
    cmd /c mklink /d $linkPath $targetPath
    Write-Host "Symbolic link '$linkPath' to '$targetPath' created."
}

# Try to run Python with different common commands
Write-Host "Starting Python server..."
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Try different Python commands in order of preference
$pythonCommands = @("python", "python.exe", "py", "python3")
$pythonFound = $false

foreach ($cmd in $pythonCommands) {
    try {
        Write-Host "Trying: $cmd"
        & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Found Python: $cmd"
            Write-Host "Starting server on http://192.168.137.1:80"
            Write-Host "Press Ctrl+C to stop the server"
            & $cmd .\uploader.py
            $pythonFound = $true
            break
        }
    } catch {
        Write-Host "$cmd not found, trying next..."
    }
}

if (-not $pythonFound) {
    Write-Host "ERROR: Python not found! Please install Python or add it to your PATH."
    Write-Host "You can download Python from: https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    Write-Host ""
    Write-Host "Alternatively, run the uploader manually:"
    Write-Host "cd '$scriptDir'"
    Write-Host "python uploader.py"
    pause
}