
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


python.exe .\uploader.py