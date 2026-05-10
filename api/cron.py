from http.server import BaseHTTPRequestHandler
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scraper.main import run

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        asyncio.run(run())
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
