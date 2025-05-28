from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import urllib

HOST = 'localhost'
PORT = 8000

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")  # Leg deine HTML/CSS/JS-Dateien hier hinein

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="text/html"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def serve_file(self, path):
        # Schutz vor Directory Traversal
        safe_path = os.path.normpath(urllib.parse.unquote(path)).lstrip("/")
        file_path = os.path.join(STATIC_DIR, safe_path)
        
        if not os.path.isfile(file_path):
            self.send_error(404, "Datei nicht gefunden")
            return

        self._set_headers(self.get_mime_type(file_path))
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    def get_mime_type(self, filename):
        if filename.endswith(".html"):
            return "text/html"
        elif filename.endswith(".css"):
            return "text/css"
        elif filename.endswith(".js"):
            return "application/javascript"
        elif filename.endswith(".json"):
            return "application/json"
        elif filename.endswith(".png"):
            return "image/png"
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            return "image/jpeg"
        else:
            return "application/octet-stream"

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.handle_api_get()
        else:
            # Wenn / oder /index.html → lade index.html
            filepath = "index.html" if self.path in ["/", "/index.html"] else self.path[1:]
            self.serve_file(filepath)

    def do_POST(self):
        if self.path == "/api/echo":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_error(400, "Ungültiges JSON")
                return
            self._set_headers("application/json")
            response = {"received": data}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_error(404, "API-Endpunkt nicht gefunden")

    def handle_api_get(self):
        if self.path == "/api/hello":
            self._set_headers("application/json")
            response = {"message": "Hallo von der Schülerzeitungs-API!"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_error(404, "API-Endpunkt nicht gefunden")

if __name__ == "__main__":
    print(f"Server läuft auf http://{HOST}:{PORT}")
    print(f"Statischer Ordner: {STATIC_DIR}")
    httpd = HTTPServer((HOST, PORT), SimpleHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wird beendet.")
        httpd.server_close()
