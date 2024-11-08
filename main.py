from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote_plus
import json
import mimetypes
from pathlib import Path
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.send_messages()
        else:
            if Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            data = self.rfile.read(int(self.headers['Content-Length']))
            data_parse = unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            timestamp = datetime.now().isoformat()

            # Load existing data, add new message, and save to JSON
            storage_path = Path('storage/data.json')
            if storage_path.exists():
                with open(storage_path, 'r', encoding='utf-8') as f:
                    stored_data = json.load(f)
            else:
                stored_data = {}

            stored_data[timestamp] = {
                "username": data_dict.get("username"),
                "message": data_dict.get("message")
            }
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(stored_data, f, indent=2)

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def send_messages(self):
        storage_path = Path('storage/data.json')
        if storage_path.exists():
            with open(storage_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        else:
            messages = {}

        # Construct HTML response for displaying messages
        response = '<html><head><title>Messages</title></head><body>'
        response += '<h1>Messages</h1>'
        for timestamp, msg_data in messages.items():
            response += f"<p><strong>{msg_data['username']}</strong> ({timestamp}): {msg_data['message']}</p>"
        response += '</body></html>'

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    print("Starting server on port 3000...")
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()