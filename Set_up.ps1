# Get the ID and name of the current user
$myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$myWindowsPrincipal = New-Object System.Security.Principal.WindowsPrincipal($myWindowsID)

# Check to see if we're currently running "as Administrator"
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

if (-not ($myWindowsPrincipal.IsInRole($adminRole))) {
    # We are not running as Administrator, so reopen the script as Administrator
    $newProcess = New-Object System.Diagnostics.ProcessStartInfo 'PowerShell';

    # Specify the PowerShell script to run
    $newProcess.Arguments = "& '" + (Get-AuthenticatingUser).Path + "'" # Not sure if Get-AuthenticatingUser works here, need to check

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
# Check if the symbolic link already exists
if (-not (Test-Path "list_files" -PathType SymbolicLink)) {
    # Create the symbolic link
    cmd /c mklink /d list_files "C:\Users\Public"
} else {
    Write-Host "Symbolic link 'list_files' already exists."
}

python.exe .\uploader.py