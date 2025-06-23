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
            }
        )
        
        if "file" in form:
            file_item = form["file"]
            filename = os.path.basename(file_item.filename)
            filepath = os.path.join(UPLOAD_DIR, filename)

            with open(filepath, 'wb') as f:
                f.write(file_item.file.read())
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"File uploaded successfully!\n")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No file was uploaded.\n")
            
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
        r.append('<div id="folder-structure">')
        r.append('<h2>Contents of /%s:</h2>' % html.escape(url_path))
        r.append('<ul>')

        # Add a ".." link if not at the root
        if url_path:
            if '/' in url_path:
                parent_path = '/'.join(url_path.split('/')[:-1])
                parent_url = '/list_files/' + parent_path if parent_path else '/list_files'
            else:
                parent_url = '/list_files'
            r.append('<li><a href="%s">..</a></li>' % parent_url)

        for name in file_list:
            fullname = os.path.join(path, name)
            displayname = name
            
            # Append '/' for directories
            if os.path.isdir(fullname):
                displayname = name + "/"

            # Construct the href for the link
            if url_path:
                href = '/list_files/' + url_path + '/' + urllib.parse.quote(name, safe='')
            else:
                href = '/list_files/' + urllib.parse.quote(name, safe='')

            r.append('<li><a href="%s">%s</a></li>' % (href, html.escape(displayname)))

        r.append('</ul>')
        r.append('</div>')
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
