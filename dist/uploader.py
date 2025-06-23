import http.server
import socketserver
import os
import cgi
import mimetypes
import html
import urllib.parse
import io

UPLOAD_DIR = os.getcwd()
PORT = 80
PUBLIC_FOLDER = "C:\\Users\\Public"
LINK_FILES_DIR = "list_files"

class UploadHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            }        )
        
        if "file" in form:
            file_item = form["file"]
            filename = os.path.basename(file_item.filename)
            filepath = os.path.join(UPLOAD_DIR, filename)

            with open(filepath, 'wb') as f:
                f.write(file_item.file.read())
                
            # Send a success response with redirect
            success_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Upload Success</title>
    <link rel="stylesheet" href="/style.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3;url=/">
</head>
<body>
    <div style="text-align: center; margin-top: 50px;">
        <div style="background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; max-width: 400px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
            <i class="fas fa-check-circle" style="font-size: 4em; color: #27ae60; margin-bottom: 20px;"></i>
            <h2 style="color: #27ae60; margin-bottom: 15px;">Upload Successful!</h2>
            <p style="color: #2c3e50; margin-bottom: 20px;">File "<strong>%s</strong>" has been uploaded successfully.</p>
            <p style="color: #7f8c8d; font-size: 0.9em;">Redirecting in 3 seconds...</p>
            <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 20px; background: linear-gradient(45deg, #3498db, #2980b9); color: white; text-decoration: none; border-radius: 25px;">
                <i class="fas fa-arrow-left"></i> Back to Upload
            </a>
        </div>
    </div>
</body>
</html>''' % html.escape(filename)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(success_html.encode('utf-8'))
        else:
            # Send an error response
            error_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Upload Error</title>
    <link rel="stylesheet" href="/style.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div style="text-align: center; margin-top: 50px;">
        <div style="background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; max-width: 400px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
            <i class="fas fa-times-circle" style="font-size: 4em; color: #e74c3c; margin-bottom: 20px;"></i>
            <h2 style="color: #e74c3c; margin-bottom: 15px;">Upload Failed</h2>
            <p style="color: #2c3e50; margin-bottom: 20px;">No file was selected for upload.</p>
            <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 20px; background: linear-gradient(45deg, #e74c3c, #c0392b); color: white; text-decoration: none; border-radius: 25px;">
                <i class="fas fa-arrow-left"></i> Try Again
            </a>
        </div>
    </div>
</body>
</html>'''
            
            self.send_response(400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(error_html.encode('utf-8'))
            
    def list_directory(self, path):
        """Helper to produce a directory listing with custom styling."""
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        file_list.sort(key=lambda a: a.lower())
        
        # Calculate the relative path from PUBLIC_FOLDER to current path
        try:
            rel_path = os.path.relpath(path, PUBLIC_FOLDER)
            if rel_path == '.':
                rel_path = ''
            # Convert Windows path separators to URL separators
            url_path = rel_path.replace('\\', '/')
        except ValueError:
            url_path = ''
        
        # Generate custom HTML
        r = []
        r.append('<!DOCTYPE html>')
        r.append('<html>')
        r.append('<head>')
        r.append('<title>Directory listing for %s</title>' % html.escape(url_path or '/'))
        r.append('<link rel="stylesheet" href="/style.css">')
        r.append('<meta charset="UTF-8">')
        r.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        r.append('</head>')
        r.append('<body>')
        
        # Add dark mode toggle button
        r.append('<button class="dark-mode-toggle" onclick="toggleDarkMode()" aria-label="Toggle dark mode"></button>')
        
        r.append('<div style="text-align: center; margin-bottom: 20px;">')
        r.append('<a href="/" class="back-to-upload">Back to Upload</a>')
        r.append('</div>')
        r.append('<div id="folder-structure">')
        r.append('<h2>Contents of /%s:</h2>' % html.escape(url_path))
        r.append('<ul>')

        # Add a ".." link if not at the root
        if url_path:
            if '/' in url_path:
                parent_path = '/'.join(url_path.split('/')[:-1])
                parent_href = '/list_files/' + parent_path if parent_path else '/list_files'
            else:
                parent_href = '/list_files'
            r.append('<li><a href="%s">.. (Parent Directory)</a></li>' % parent_href)

        for name in file_list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            
            # Escape special characters
            displayname = html.escape(displayname, quote=False)
            linkname = urllib.parse.quote(linkname, errors='surrogatepass')
            
            if os.path.isdir(fullname):
                displayname = name + "/"
                if url_path:
                    href = '/list_files/' + url_path + '/' + linkname
                else:
                    href = '/list_files/' + linkname
            else:
                if url_path:
                    href = '/list_files/' + url_path + '/' + linkname
                else:
                    href = '/list_files/' + linkname

            r.append('<li><a href="%s">%s</a></li>' % (href, html.escape(displayname)))

        r.append('</ul>')
        r.append('</div>')
        
        # Add complete JavaScript for dark mode
        r.append('<script>')
        r.append('function toggleDarkMode() {')
        r.append('  const html = document.documentElement;')
        r.append('  const currentTheme = html.getAttribute("data-theme");')
        r.append('  if (currentTheme === "dark") {')
        r.append('    html.setAttribute("data-theme", "light");')
        r.append('    localStorage.setItem("theme", "light");')
        r.append('  } else {')
        r.append('    html.setAttribute("data-theme", "dark");')
        r.append('    localStorage.setItem("theme", "dark");')
        r.append('  }')
        r.append('}')
        r.append('function initTheme() {')
        r.append('  const savedTheme = localStorage.getItem("theme");')
        r.append('  const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;')
        r.append('  if (savedTheme) {')
        r.append('    document.documentElement.setAttribute("data-theme", savedTheme);')
        r.append('  } else if (systemPrefersDark) {')
        r.append('    document.documentElement.setAttribute("data-theme", "dark");')
        r.append('  }')
        r.append('}')
        r.append('window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {')
        r.append('  if (!localStorage.getItem("theme")) {')
        r.append('    document.documentElement.setAttribute("data-theme", e.matches ? "dark" : "light");')
        r.append('  }')
        r.append('});')
        r.append('initTheme();')
        r.append('</script>')
        r.append('</body>')
        r.append('</html>')

        encoded = '\n'.join(r).encode('utf-8', 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f
        
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/list_files' or path.startswith('/list_files/'):
            # Extract the subpath from the URL path directly
            if path == '/list_files':
                requested_subpath = ''
            else:
                # Remove the '/list_files/' prefix to get the actual subpath
                requested_subpath = path[len('/list_files/'):]
                
            current_dir = os.path.join(PUBLIC_FOLDER, requested_subpath)
            
            try:
                # Security check to prevent directory traversal
                if not os.path.commonpath([os.path.realpath(current_dir), os.path.realpath(PUBLIC_FOLDER)]) == os.path.realpath(PUBLIC_FOLDER):
                    raise Exception("Access denied: Attempted directory traversal.")

                if os.path.exists(current_dir) and os.path.isdir(current_dir):
                    # Directory listing
                    f = self.list_directory(current_dir)
                    if f:
                        self.copyfile(f, self.wfile)
                        
                elif os.path.exists(current_dir) and os.path.isfile(current_dir):
                    # File serving
                    try:
                        # Determine content type
                        content_type, _ = mimetypes.guess_type(current_dir)
                        if content_type is None:
                            content_type = 'application/octet-stream'
                        
                        # Get file size
                        file_size = os.path.getsize(current_dir)
                        
                        # Send headers
                        self.send_response(200)
                        self.send_header('Content-Type', content_type)
                        self.send_header('Content-Length', str(file_size))
                        
                        # For certain file types, suggest filename for download
                        filename = os.path.basename(current_dir)
                        if content_type.startswith('application/') or content_type == 'application/octet-stream':
                            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                        
                        self.end_headers()
                        
                        # Send file content
                        with open(current_dir, 'rb') as file:
                            self.copyfile(file, self.wfile)
                            
                    except Exception as file_error:
                        self.send_error(500, f"Error serving file: {str(file_error)}")

                else:
                    # 404 error page
                    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Not Found</title>
    <link rel="stylesheet" href="/style.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="folder-structure">
        <h2>Error: Path '{html.escape(requested_subpath)}' not found.</h2>
    </div>
</body>
</html>'''
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))

            except Exception as e:
                # 500 error page
                html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Internal Server Error</title>
    <link rel="stylesheet" href="/style.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="folder-structure">
        <h2>Error: {html.escape(str(e))}</h2>
    </div>
</body>
</html>'''
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
        else:
            # For any other GET requests, use the default handler
            super().do_GET()
   
handler = UploadHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
