# CaptivePortal File Upload System

A simple file upload system that creates a WiFi hotspot and allows connected devices to upload files through a web interface.

## Components

- `Set_up.ps1` - PowerShell script that configures and starts the WiFi hotspot
- `index.html` - Web interface for file uploads with styled directory browsing
- `style.css` - CSS styling for the web interface
- `uploader.py` - Python HTTP server that handles file uploads and directory browsing
- `list_files/` - Symbolic link to `C:\Users\Public` for file browsing

## Features

- **File Upload**: Upload files from any connected device through a web interface
- **Directory Browsing**: Browse and navigate through the PC's Public folder with custom styling
- **WiFi Hotspot**: Creates a local WiFi network for easy device connection
- **Cross-platform Access**: Works with phones, tablets, and other devices

## Setup and Usage

### 🖥️ **Option 1: GUI Application (Recommended)**

#### Quick Start
1. **Double-click `run_app.bat`** to launch the GUI application
2. **Or run**: `python captive_portal_app.py`
3. **Configure settings** in the GUI (network name, password, upload folder)
4. **Click "Start All"** to begin
5. **Connect devices** to the WiFi network shown
6. **Access** the web interface at the URL displayed

#### Features
- ✅ **Easy-to-use interface** with status indicators
- ✅ **Real-time logging** of all activities  
- ✅ **One-click start/stop** for hotspot and server
- ✅ **Customizable settings** (SSID, password, upload directory)
- ✅ **Built-in browser launcher** to test the interface
- ✅ **Administrator privilege detection** and warnings

#### Building Executable
```batch
# Build standalone Windows application
.\build_app.bat
```
This creates `dist\CaptivePortal.exe` - a portable executable that includes all dependencies.

### 📜 **Option 2: PowerShell Script (Original Method)**

#### Run the Setup Script
```powershell
# Run as Administrator
.\Set_up.ps1
```
This will:
- Create a WiFi hotspot named "TestHotspot" with password "password"
- Configure the network adapter with IP 192.168.137.1
- Create a symbolic link from `list_files` to `C:\Users\Public`
- Start the Python upload server on port 80

### 2. Connect to the Hotspot
- Connect any device to the "TestHotspot" WiFi network
- Use the password: "password"

### 3. Access the Web Interface
- Open `http://192.168.137.1` in a web browser
- Use the web interface to:
  - Upload files to the PC
  - Browse files in the Public folder
  - Navigate through subdirectories

## Network Details

- **SSID**: TestHotspot
- **Password**: password
- **Server IP**: 192.168.137.1
- **Port**: 80
- **File Browse URL**: `http://192.168.137.1/list_files`

## File Locations

- **Uploaded files**: Saved in the same directory as the server script
- **Browsable files**: Located in `C:\Users\Public` (accessible via `/list_files`)

## Requirements

- Windows OS with WiFi capability
- Python 3.x
- Administrative privileges (for network configuration and symbolic link creation)

## Troubleshooting

### Directory Links Not Working
- Ensure the `list_files` symbolic link exists and points to `C:\Users\Public`
- Check that the Python server is running with proper permissions
- Verify the server is accessible at `http://192.168.137.1/list_files`

### Phone Cannot Connect
- Verify the WiFi hotspot is active
- Check that the correct password is being used
- Ensure Windows firewall allows connections on port 80

### Upload Issues
- Confirm the server has write permissions in the current directory
- Check available disk space
- Verify the file size is not too large for the connection

## Security Notes

⚠️ **Important**: This is a basic implementation intended for local use only.

- The server accepts all file types and stores them in the current directory
- No authentication is required for uploads or file browsing
- Directory traversal protection is implemented but should be tested
- Use with caution and implement additional security measures for production use
- Only use on trusted networks

## Code Structure

The main server (`uploader.py`) handles:
- POST requests for file uploads
- GET requests for the main page and static files
- Custom directory listing with styled HTML output
- URL routing for `/list_files` paths
- Security checks to prevent directory traversal

The custom directory listing generates styled HTML that matches your CSS, providing a better user experience than the default Python HTTP server directory listing.
