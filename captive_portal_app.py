import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import webbrowser
import os
import sys
import socket
import time
import ctypes

class CaptivePortalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CaptivePortal - File Transfer Hub")
        self.root.geometry("700x600")
        self.root.minsize(500, 400)  # Set minimum size for better usability
        self.root.resizable(True, True)
        
        # Variables
        self.server_process = None
        self.hotspot_active = False
        self.server_running = False
        
        # Set icon if available
        try:
            # Try to set an icon if you have one
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('vista')  # Use modern Windows theme
        
        # Create main canvas and scrollbar
        canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure canvas scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
          # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind keyboard navigation
        def _on_key(event):
            if event.keysym == "Up":
                canvas.yview_scroll(-1, "units")
            elif event.keysym == "Down":
                canvas.yview_scroll(1, "units")
            elif event.keysym == "Prior":  # Page Up
                canvas.yview_scroll(-1, "pages")
            elif event.keysym == "Next":   # Page Down
                canvas.yview_scroll(1, "pages")
            elif event.keysym == "Home":
                canvas.yview_moveto(0)
            elif event.keysym == "End":
                canvas.yview_moveto(1)
        
        canvas.bind_all("<Key>", _on_key)
        canvas.focus_set()  # Make canvas focusable for keyboard events
        
        # Main container with padding
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
          # Title with admin status
        admin_status = " (Administrator)" if self.is_admin() else " (Limited Mode)"
        title_text = "📶 CaptivePortal File Transfer Hub" + admin_status
        title_color = "#27ae60" if self.is_admin() else "#e74c3c"
        
        title_label = tk.Label(main_frame, text=title_text, 
                              font=("Arial", 18, "bold"), fg=title_color)
        title_label.pack(pady=(0, 20))
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 Status", padding=15)
        status_frame.pack(fill="x", pady=(0, 15))
        
        # Status indicators with better formatting
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill="x")
        
        ttk.Label(status_grid, text="Hotspot:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.hotspot_status = tk.Label(status_grid, text="❌ Inactive", 
                                      font=("Arial", 10), fg="red")
        self.hotspot_status.grid(row=0, column=1, sticky="w")
        
        ttk.Label(status_grid, text="Server:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.server_status = tk.Label(status_grid, text="❌ Stopped", 
                                     font=("Arial", 10), fg="red")
        self.server_status.grid(row=1, column=1, sticky="w")
        
        ttk.Label(status_grid, text="Access URL:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 10))
        self.ip_status = tk.Label(status_grid, text="Not available", 
                                 font=("Arial", 10), fg="gray", cursor="hand2")
        self.ip_status.grid(row=2, column=1, sticky="w")
        self.ip_status.bind("<Button-1>", lambda e: self.open_browser())
        
        # Control Buttons Frame
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Controls", padding=15)
        control_frame.pack(fill="x", pady=(0, 15))
        
        button_grid = ttk.Frame(control_frame)
        button_grid.pack()
        
        self.start_btn = ttk.Button(button_grid, text="🚀 Start All", 
                                   command=self.start_all, width=15)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(button_grid, text="🛑 Stop All", 
                                  command=self.stop_all, state="disabled", width=15)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.open_browser_btn = ttk.Button(button_grid, text="🌐 Open Browser", 
                                          command=self.open_browser, state="disabled", width=15)
        self.open_browser_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.open_folder_btn = ttk.Button(button_grid, text="📁 Open Upload Folder", 
                                         command=self.open_upload_folder, width=18)
        self.open_folder_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        self.diagnostics_btn = ttk.Button(button_grid, text="🔍 Network Diagnostics", 
                                         command=self.run_diagnostics, width=18)
        self.diagnostics_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Add restart as admin button if not running as admin
        if not self.is_admin():
            self.admin_btn = ttk.Button(button_grid, text="👑 Restart as Admin", 
                                       command=self.restart_as_admin, width=18)
            self.admin_btn.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Hotspot Settings", padding=15)
        settings_frame.pack(fill="x", pady=(0, 15))
        
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill="x")
        
        # Configure grid weights for proper alignment
        settings_grid.columnconfigure(1, weight=1)
        
        ttk.Label(settings_grid, text="Network Name (SSID):").grid(row=0, column=0, sticky="w", pady=5)
        self.ssid_var = tk.StringVar(value="TestHotspot")
        ssid_entry = ttk.Entry(settings_grid, textvariable=self.ssid_var, width=25)
        ssid_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="w")
        
        ttk.Label(settings_grid, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar(value="password")
        password_entry = ttk.Entry(settings_grid, textvariable=self.password_var, width=25, show="*")
        password_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky="w")
        
        # Show/Hide password button
        self.show_password_var = tk.BooleanVar()
        show_pass_check = ttk.Checkbutton(settings_grid, text="Show password", 
                                         variable=self.show_password_var,
                                         command=lambda: password_entry.config(show="" if self.show_password_var.get() else "*"))
        show_pass_check.grid(row=1, column=2, padx=(10, 0), pady=5)
        
        # Upload Directory Frame
        upload_frame = ttk.LabelFrame(main_frame, text="📂 Upload Directory", padding=15)
        upload_frame.pack(fill="x", pady=(0, 15))
        
        dir_grid = ttk.Frame(upload_frame)
        dir_grid.pack(fill="x")
        dir_grid.columnconfigure(0, weight=1)
        
        self.upload_dir_var = tk.StringVar(value=os.getcwd())
        upload_dir_entry = ttk.Entry(dir_grid, textvariable=self.upload_dir_var, width=60)
        upload_dir_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        browse_btn = ttk.Button(dir_grid, text="📁 Browse", 
                               command=self.browse_directory)
        browse_btn.grid(row=0, column=1)
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="📋 Activity Log", padding=15)
        log_frame.pack(fill="both", expand=True)
        
        # Create text widget with scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(log_container, height=12, wrap=tk.WORD, 
                               font=("Consolas", 9), bg="#f8f9fa", fg="#2c3e50")
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Log control buttons
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill="x", pady=(10, 0))
        
        ttk.Button(log_controls, text="🗑️ Clear Log", 
                  command=self.clear_log).pack(side="left")
        ttk.Button(log_controls, text="💾 Save Log", 
                  command=self.save_log).pack(side="left", padx=(10, 0))
          # Initial log messages
        self.log("🟢 CaptivePortal application started")
        if self.is_admin():
            self.log("� Running with Administrator privileges")
            self.log("✅ Full functionality available")
        else:
            self.log("⚠️  Running with LIMITED privileges")
            self.log("💡 Some features may not work properly")
            self.log("🔧 Restart as Administrator for full functionality")
        self.log("💡 Click 'Start All' to begin hotspot and server")
        
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log("📋 Log cleared")
        
    def save_log(self):
        """Save log to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save log file"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"💾 Log saved to: {filename}")
        except Exception as e:
            self.log(f"❌ Failed to save log: {str(e)}")
        
    def browse_directory(self):
        """Browse for upload directory"""
        directory = filedialog.askdirectory(initialdir=self.upload_dir_var.get())
        if directory:
            self.upload_dir_var.set(directory)
            self.log(f"📂 Upload directory changed to: {directory}")
            
    def open_upload_folder(self):
        """Open upload folder in Windows Explorer"""
        try:
            os.startfile(self.upload_dir_var.get())
        except Exception as e:
            self.log(f"❌ Failed to open folder: {str(e)}")
            
    def start_all(self):
        """Start hotspot and server"""
        self.start_btn.config(state="disabled")
        self.log("🚀 Starting hotspot and server...")
        
        # Start in separate thread to prevent UI freezing
        threading.Thread(target=self._start_all_thread, daemon=True).start()
    def _start_all_thread(self):
        """Start hotspot and server in separate thread"""
        try:
            # Give a warning if not running as admin but continue
            if not self.is_admin():
                self.log("⚠️  Running without Administrator privileges")
                self.log("💡 Some network operations may fail")
                
            # Start hotspot
            if self.start_hotspot():
                self.hotspot_active = True
                self.hotspot_status.config(text="✅ Active", fg="green")
                
                # Small delay to ensure network is ready
                time.sleep(3)
                  # Start server
                if self.start_server():
                    self.server_running = True
                    self.server_status.config(text="✅ Running", fg="green")
                    
                    # Update IP status based on hotspot success
                    if self.hotspot_active:
                        self.ip_status.config(text="http://192.168.137.1", fg="blue")
                        self.log("🌐 Access URL: http://192.168.137.1")
                    else:
                        # Try to get actual IP address for server-only mode
                        try:
                            hostname = socket.gethostname()
                            ip_address = socket.gethostbyname(hostname)
                            self.ip_status.config(text=f"http://{ip_address}", fg="blue")
                            self.log(f"🌐 Access URL: http://{ip_address}")
                        except:
                            self.ip_status.config(text="http://localhost", fg="blue")
                            self.log("🌐 Access URL: http://localhost")
                    
                    self.stop_btn.config(state="normal")
                    self.open_browser_btn.config(state="normal")
                    self.log("✅ Server started successfully!")
                    self.log(f"📱 WiFi Network: {self.ssid_var.get()}")
                    self.log(f"🔑 Password: {self.password_var.get()}")
                    self.log("📤 Files will be uploaded to: " + self.upload_dir_var.get())
                else:
                    self.log("❌ Failed to start server")
                    self.start_btn.config(state="normal")
            else:
                self.log("❌ Failed to start hotspot")
                self.start_btn.config(state="normal")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.start_btn.config(state="normal")
            
    def start_hotspot(self):
        """Start WiFi hotspot"""
        try:
            ssid = self.ssid_var.get()
            password = self.password_var.get()
            
            if len(password) < 8:
                self.log("❌ Password must be at least 8 characters")
                return False
            
            self.log(f"📡 Setting up hotspot: {ssid}")
              # First, check if WiFi adapter supports hosted network
            self.log("🔍 Checking WiFi adapter capabilities...")
            check_cmd = "netsh wlan show drivers"
            check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            self.log(f"🔍 Driver check return code: {check_result.returncode}")
            
            if check_result.returncode == 0:
                if "Hosted network supported" in check_result.stdout:
                    hosted_line = check_result.stdout.split("Hosted network supported")[1].split("\n")[0]
                    self.log(f"🔍 Hosted network support line: {hosted_line.strip()}")
                    if "Yes" not in hosted_line:
                        self.log("❌ WiFi adapter does not support hosted network")
                        self.log("💡 Try using Windows Mobile Hotspot instead:")
                        self.log("   Settings > Network & Internet > Mobile hotspot")
                        return self.try_alternative_methods()
                    else:
                        self.log("✅ WiFi adapter supports hosted network")
                else:
                    self.log("⚠️  Could not determine hosted network support")
                    self.log("🔍 Available driver info:")
                    # Show relevant lines from driver info
                    lines = check_result.stdout.split('\n')
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['driver', 'hosted', 'network', 'wireless']):
                            self.log(f"   {line.strip()}")
            else:
                self.log("⚠️  Failed to check WiFi drivers")
                if check_result.stderr:
                    self.log(f"   Error: {check_result.stderr.strip()}")
                
            # Check WLAN service status
            self.log("🔍 Checking WLAN AutoConfig service...")
            service_cmd = 'sc query "WLANSVC"'
            service_result = subprocess.run(service_cmd, shell=True, capture_output=True, text=True)
            
            if service_result.returncode == 0:
                if "RUNNING" in service_result.stdout:
                    self.log("✅ WLAN AutoConfig service is running")
                else:
                    self.log("⚠️  WLAN AutoConfig service is not running")
                    self.log("💡 Try: services.msc > WLAN AutoConfig > Start")
            else:
                self.log("⚠️  Could not check WLAN service status")
            
            # Stop any existing hosted network
            subprocess.run("netsh wlan stop hostednetwork", shell=True, capture_output=True)
              # Set hosted network
            cmd1 = f'netsh wlan set hostednetwork mode=allow ssid="{ssid}" key="{password}"'
            result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
            
            self.log(f"🔍 Debug - Command: {cmd1}")
            self.log(f"🔍 Debug - Return code: {result1.returncode}")
            self.log(f"🔍 Debug - Stderr: '{result1.stderr.strip()}'")
            self.log(f"🔍 Debug - Stdout: '{result1.stdout.strip()}'")
            
            if result1.returncode != 0:
                error_msg = result1.stderr.strip() if result1.stderr.strip() else result1.stdout.strip() if result1.stdout.strip() else "Command failed with no error message"
                self.log(f"❌ Failed to configure hotspot: {error_msg}")
                
                # Check for specific error conditions
                if "access is denied" in error_msg.lower() or "access denied" in error_msg.lower():
                    self.log("💡 Solution: Run as Administrator")
                elif "wireless lan service" in error_msg.lower():
                    self.log("💡 Solution: Start Windows WLAN AutoConfig service")
                elif "hosted network" in error_msg.lower() and "not" in error_msg.lower():
                    self.log("💡 Solution: Your WiFi adapter doesn't support hosted networks")
                    self.log("   Try Windows Mobile Hotspot instead")
                
                return self.try_alternative_methods()
                
            # Start hosted network
            cmd2 = 'netsh wlan start hostednetwork'
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
            
            if result2.returncode != 0:
                error_msg = result2.stderr.strip() if result2.stderr.strip() else "Unknown error"
                self.log(f"❌ Failed to start hotspot: {error_msg}")
                if result2.stdout:
                    self.log(f"   Output: {result2.stdout.strip()}")
                self.log("💡 Common issues and solutions:")
                self.log("   • Run as Administrator")
                self.log("   • Enable WiFi adapter")
                self.log("   • Update WiFi drivers")
                self.log("   • Use Windows Mobile Hotspot instead")
                return self.try_alternative_methods()
                
            self.log("📡 Hotspot started, configuring network...")
            
            # Set IP address - try different adapter names
            adapter_names = [
                "Local Area Connection* 1",
                "Local Area Connection* 2", 
                "Microsoft Hosted Network Virtual Adapter"
            ]
            
            ip_set = False
            for adapter in adapter_names:
                cmd3 = f'netsh interface ip set address "{adapter}" static 192.168.137.1 255.255.255.0'
                result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True)
                if result3.returncode == 0:
                    ip_set = True
                    self.log(f"🌐 IP configured on adapter: {adapter}")
                    break
                    
            if not ip_set:
                self.log("⚠️  Could not automatically set IP address")
                self.log("💡 You may need to manually set 192.168.137.1 on the hosted network adapter")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Hotspot error: {str(e)}")
            return False
            
    def try_alternative_methods(self):
        """Try alternative methods when netsh fails"""
        self.log("🔄 Trying alternative approach...")
        
        # Check if WLAN service is running and offer to start it
        service_cmd = 'sc query "WLANSVC"'
        service_result = subprocess.run(service_cmd, shell=True, capture_output=True, text=True)
        
        if service_result.returncode == 0 and "RUNNING" not in service_result.stdout:
            self.log("� WLAN service is not running. Attempting to start it...")
            if self.start_wlan_service():
                self.log("✅ WLAN service started. Retrying hotspot setup...")
                return self.start_hotspot()  # Retry hotspot creation
        
        self.log("�💡 Manual hotspot setup options:")
        self.log("   1. Windows Settings > Network & Internet > Mobile hotspot")
        self.log("   2. Command Prompt as Admin:")
        self.log(f'      netsh wlan set hostednetwork mode=allow ssid="{self.ssid_var.get()}" key="{self.password_var.get()}"')
        self.log("      netsh wlan start hostednetwork")
        self.log("   3. Use existing WiFi network and connect devices to it")
        
        # Ask user if they want to continue with server-only mode
        result = messagebox.askyesno("Hotspot Failed", 
                                   "Hotspot creation failed. Would you like to:\n\n" +
                                   "YES: Continue with server-only mode\n" +
                                   "NO: Cancel and set up hotspot manually\n\n" +
                                   "If you choose YES, you can:\n" +
                                   "• Use Windows Mobile Hotspot instead\n" +
                                   "• Connect devices to existing WiFi\n" +
                                   "• Access via your computer's IP address")
        
        if result:
            self.log("🌐 Continuing in server-only mode...")
            self.log("💡 To find your IP address, run 'ipconfig' in Command Prompt")
            
            # Try to get actual IP address
            try:
                # Get all network interfaces
                import psutil
                interfaces = psutil.net_if_addrs()
                for interface_name, interface_addresses in interfaces.items():
                    for address in interface_addresses:
                        if address.family == socket.AF_INET and not address.address.startswith('127.'):
                            self.log(f"🌐 Network interface '{interface_name}': {address.address}")
                            self.log(f"📱 Devices can access: http://{address.address}")
            except ImportError:
                # Fallback method without psutil
                try:
                    hostname = socket.gethostname()
                    ip_address = socket.gethostbyname(hostname)
                    self.log(f"🌐 Your computer's IP address: {ip_address}")
                    self.log(f"📱 Devices can access: http://{ip_address}")
                except:
                    self.log("⚠️  Could not detect IP address automatically")
                    self.log("💡 Run 'ipconfig' in Command Prompt to find your IP")
            
            return True
        else:
            self.log("❌ Setup cancelled. Please configure hotspot manually.")
            return False
            
    def start_server(self):
        """Start HTTP server"""
        try:
            # Change to upload directory
            original_dir = os.getcwd()
            os.chdir(self.upload_dir_var.get())
            
            # Find Python executable
            python_cmd = self.find_python()
            if not python_cmd:
                self.log("❌ Python not found in PATH!")
                return False
                
            # Check if uploader.py exists
            uploader_path = os.path.join(original_dir, "uploader.py")
            if not os.path.exists(uploader_path):
                self.log("❌ uploader.py not found!")
                return False
                
            self.log(f"🐍 Starting server with: {python_cmd}")
            
            # Start Python server
            self.server_process = subprocess.Popen(
                [python_cmd, uploader_path],
                cwd=self.upload_dir_var.get(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window
            )
            
            # Check if server started successfully
            time.sleep(2)
            if self.server_process.poll() is None:
                self.log("🌐 HTTP server started on port 80")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                self.log(f"❌ Server failed to start:")
                if stderr:
                    self.log(f"   Error: {stderr.strip()}")
                if stdout:
                    self.log(f"   Output: {stdout.strip()}")
                return False
                
        except Exception as e:
            self.log(f"❌ Server error: {str(e)}")
            return False
            
    def find_python(self):
        """Find Python executable"""
        commands = ["python", "python.exe", "py", "python3"]
        for cmd in commands:
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log(f"🐍 Found Python: {cmd} - {result.stdout.strip()}")
                    return cmd
            except:
                continue
        return None
        
    def stop_all(self):
        """Stop server and hotspot"""
        self.log("🛑 Stopping server and hotspot...")
        
        # Stop server
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
            self.server_process = None
            self.server_running = False
            self.server_status.config(text="❌ Stopped", fg="red")
            self.log("🌐 HTTP server stopped")
            
        # Stop hotspot
        try:
            result = subprocess.run("netsh wlan stop hostednetwork", shell=True, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("📡 Hotspot stopped")
            else:
                self.log("⚠️  Could not stop hotspot")
            self.hotspot_active = False
            self.hotspot_status.config(text="❌ Inactive", fg="red")
        except Exception as e:
            self.log(f"⚠️  Error stopping hotspot: {str(e)}")
            
        self.ip_status.config(text="Not available", fg="gray")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.open_browser_btn.config(state="disabled")
        self.log("✅ All services stopped")
    def open_browser(self):
        """Open browser to server URL"""
        if self.server_running:
            # Get the current IP from the status label
            url = self.ip_status.cget("text")
            if url and url != "Not available":
                webbrowser.open(url)
                self.log(f"🌐 Opened browser to {url}")
            else:
                # Fallback to localhost
                webbrowser.open("http://localhost")
                self.log("🌐 Opened browser to http://localhost")
        else:
            messagebox.showwarning("Server Not Running", "Please start the server first.")
        
    def is_admin(self):
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def on_closing(self):
        """Handle application closing"""
        if self.server_running or self.hotspot_active:
            if messagebox.askquestion("Exit Application", 
                                    "Stop server and hotspot before closing?",
                                    icon='question') == "yes":
                self.stop_all()
                time.sleep(1)  # Give time for cleanup
        self.root.destroy()
    def start_wlan_service(self):
        """Try to start WLAN AutoConfig service"""
        try:
            self.log("🔧 Attempting to start WLAN AutoConfig service...")
            start_cmd = 'net start "WLANSVC"'
            result = subprocess.run(start_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ WLAN AutoConfig service started successfully")
                return True
            else:
                self.log("❌ Failed to start WLAN service")
                if result.stderr:
                    self.log(f"   Error: {result.stderr.strip()}")
                if result.stdout:
                    self.log(f"   Output: {result.stdout.strip()}")
                self.log("💡 Try running as Administrator or start manually:")
                self.log("   services.msc > WLAN AutoConfig > Right-click > Start")
                return False
        except Exception as e:
            self.log(f"❌ Error starting WLAN service: {str(e)}")
            return False

    def restart_as_admin(self):
        """Restart the application with administrator privileges"""
        try:
            result = messagebox.askyesno(
                "Restart as Administrator", 
                "This will close the current application and restart it with Administrator privileges.\n\n" +
                "Continue?",
                icon='question'
            )
            
            if result:
                # Get the path to the current script
                script_path = os.path.abspath(sys.argv[0])
                
                # Use ShellExecute to run as administrator
                ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas", 
                    sys.executable, 
                    f'"{script_path}"', 
                    None, 
                    1
                )
                
                # Close current application
                self.root.quit()
                
        except Exception as e:
            self.log(f"❌ Failed to restart as administrator: {str(e)}")
            messagebox.showerror("Error", f"Failed to restart as administrator:\n{str(e)}")

    def run_diagnostics(self):
        """Run network diagnostics to help troubleshoot issues"""
        self.log("🔍 Running network diagnostics...")
        
        try:
            # Check if running as admin
            admin_status = "Yes" if self.is_admin() else "No"
            self.log(f"👤 Administrator privileges: {admin_status}")
            
            # Check WLAN service
            service_cmd = 'sc query "WLANSVC"'
            service_result = subprocess.run(service_cmd, shell=True, capture_output=True, text=True)
            
            if service_result.returncode == 0:
                if "RUNNING" in service_result.stdout:
                    self.log("✅ WLAN AutoConfig service: Running")
                else:
                    self.log("❌ WLAN AutoConfig service: Not running")
                    self.log("💡 Try: services.msc > WLAN AutoConfig > Start")
            else:
                self.log("⚠️  Could not check WLAN service")
            
            # Check WiFi drivers
            self.log("🔍 Checking WiFi adapter capabilities...")
            check_cmd = "netsh wlan show drivers"
            check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if check_result.returncode == 0:
                if "Hosted network supported" in check_result.stdout:
                    hosted_line = check_result.stdout.split("Hosted network supported")[1].split("\n")[0]
                    if "Yes" in hosted_line:
                        self.log("✅ Hosted network support: Yes")
                    else:
                        self.log("❌ Hosted network support: No")
                        self.log("💡 Use Windows Mobile Hotspot instead")
                else:
                    self.log("⚠️  Could not determine hosted network support")
            else:
                self.log("❌ Failed to check WiFi drivers")
            
            # Check network interfaces
            self.log("🌐 Network interfaces:")
            try:
                # Try to get network interfaces
                import psutil
                interfaces = psutil.net_if_addrs()
                for interface_name, interface_addresses in interfaces.items():
                    for address in interface_addresses:
                        if address.family == socket.AF_INET:
                            if not address.address.startswith('127.'):
                                self.log(f"   {interface_name}: {address.address}")
            except ImportError:
                # Fallback without psutil
                try:
                    hostname = socket.gethostname()
                    ip_address = socket.gethostbyname(hostname)
                    self.log(f"   Computer IP: {ip_address}")
                except:
                    self.log("   Could not detect IP addresses")
            
            # Check if port 80 is available
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 80))
                    self.log("✅ Port 80: Available")
            except OSError:
                self.log("❌ Port 80: In use (may need Admin rights)")
                self.log("💡 Run as Administrator or use different port")
            
            self.log("✅ Diagnostics complete")
            
        except Exception as e:
            self.log(f"❌ Diagnostics error: {str(e)}")
            
    # ...existing code...
def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the application with administrator privileges"""
    try:
        if is_admin():
            return True
        else:
            # Get the path to the current script
            script_path = os.path.abspath(sys.argv[0])
            
            # Use ShellExecute to run as administrator
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                f'"{script_path}"', 
                None, 
                1
            )
            return False
    except Exception as e:
        print(f"Failed to restart as administrator: {e}")
        return False

def main():
    # Check for administrator privileges first
    if not is_admin():
        # Ask user if they want to run as administrator
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        result = messagebox.askyesno(
            "Administrator Privileges Required", 
            "CaptivePortal requires Administrator privileges for:\n\n" +
            "• Creating WiFi hotspots\n" +
            "• Binding to port 80\n" +
            "• Managing network adapters\n\n" +
            "Would you like to restart as Administrator?\n\n" +
            "Click 'No' to continue with limited functionality.",
            icon='question'
        )
        
        root.destroy()
        
        if result:
            # Try to restart as administrator
            if run_as_admin():
                return  # If successful, the new process will take over
            else:
                sys.exit(0)  # Exit current process, new admin process should start
    
    # Check if required files exist
    required_files = ["uploader.py", "style.css", "index.html"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror("Missing Files", 
                           f"Required files not found:\n" + "\n".join(missing_files) +
                           f"\n\nPlease ensure you're running from the correct directory.")
        return
    
    # Create and run the application
    root = tk.Tk()
    app = CaptivePortalApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
