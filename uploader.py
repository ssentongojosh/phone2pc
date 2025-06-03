import http.server
import socketserver
import os
import cgi

import json

UPLOAD_DIR = os.getcwd()
PORT = 80
PUBLIC_FOLDER = "C:\\Users\\Public"

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/list_files':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                items = os.listdir(PUBLIC_FOLDER)
                # Return a list of items, not a dictionary
                response = items
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, "Folder not found")
        else:
 super().do_GET()

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

handler = UploadHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
