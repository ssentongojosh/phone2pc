import http.server
import socketserver
import os
import cgi
import json # Still needed if you use it elsewhere, but not for /list_files response
import html # Import the html module for escaping
import urllib.parse

UPLOAD_DIR = os.getcwd()
PORT = 80
PUBLIC_FOLDER = "C:\\Users\\Public"
LINK_FILES_DIR = "list_files" # Define the name of the symbolic link directory

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
            self.wfile.write(b"File uploaded successfully!\\n")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No file was uploaded.\\n")
            
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if path == '/list_files':
            requested_subpath = query.get('path', [''])[0]
            current_dir = os.path.join(LINK_FILES_DIR, requested_subpath)
            try:
                # Security check
                if not os.path.commonpath([os.path.realpath(current_dir), os.path.realpath(LINK_FILES_DIR)]) == os.path.realpath(LINK_FILES_DIR):
                     raise Exception("Access denied: Attempted directory traversal.")

                if os.path.exists(current_dir) and os.path.isdir(current_dir):
                    items = os.listdir(current_dir)

                    # Generate the HTML for the file listing page
                    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>File Listing: {html.escape(requested_subpath or "C:/Users/Public")}</title>
    <link rel="stylesheet" href="/style.css"> <!-- Link to your style.css -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="folder-structure">
        <h2>Contents of {html.escape(requested_subpath or 'C:/Users/Public')}:</h2>
        <ul>'''

                    # Add a ".." link
                    if requested_subpath:
                         parent_dir = os.path.dirname(requested_subpath)
                         # Note: Removed class="folder-link" and data-path since we are navigating directly now
                         html_content += f'<li><a href="/list_files?path={urllib.parse.quote_plus(parent_dir)}">..</a></li>' 


                    for item in items:
                        item_path = os.path.join(current_dir, item)
                        safe_item = html.escape(item)
                        
                        if os.path.isdir(item_path):
                            # If it's a directory, create a link
                            new_path = os.path.join(requested_subpath, item)
                            # Note: Removed class="folder-link" and data-path
                            html_content += f'<li><a href="/list_files?path={urllib.parse.quote_plus(new_path)}">{safe_item}</a></li>' 
                        else:
                            # If it's a file, just display the name
                            html_content += f"<li>{safe_item}</li>"
                    html_content += "</ul>"
                    html_content += '</div>' # Close the div
                    # --- End of modification ---


                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                else:
                    # Generate HTML for the 404 error page
                    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Not Found</title>'''
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f"<h2>Error: Directory '{html.escape(requested_subpath)}' not found or is not a directory.</h2>".encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
    
#     
                self.end_headers()
                self.wfile.write(f"<h2>Error listing files: {html.escape(str(e))}</h2>".encode('utf-8'))
        else:
            super().do_GET()

   
handler = UploadHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
