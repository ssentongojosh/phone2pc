import http.server
import socketserver
import os
import cgi
import json

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
        if self.path == '/list_files':
            try:
                # Check if the symbolic link directory exists
                if os.path.exists(LINK_FILES_DIR) and os.path.isdir(LINK_FILES_DIR):
                    # Read the contents of the symbolic link directory
                    files = os.listdir(LINK_FILES_DIR)
                    
                    # Prepare the response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(files).encode('utf-8'))
                else:
                    # If the symbolic link directory doesn't exist
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b"Symbolic link directory 'list_files' not found or is not a directory.")
            except Exception as e:
                # Handle any errors that occur while reading the directory
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error listing files: {e}".encode('utf-8'))
        else:
            # For any other GET requests, use the default handler (e.g., serving index.html)
            super().do_GET()

handler = UploadHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()