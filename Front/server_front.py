"""
Servidor simples para servir os arquivos do Front-end
Executa em http://127.0.0.1:8000
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

# Muda para o diretório Front
os.chdir(Path(__file__).parent / 'Front')

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Adiciona headers CORS para permitir requisições do front-end para a API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('127.0.0.1', port), CORSRequestHandler)
    print(f"🌐 Servidor do Front-end rodando em http://127.0.0.1:{port}")
    print(f"📱 Abra http://127.0.0.1:{port} no navegador")
    print("Pressione CTRL+C para parar o servidor")
    server.serve_forever()
