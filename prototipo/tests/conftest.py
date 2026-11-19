"""Testes do protótipo: rode de dentro de prototipo/ com  python -m pytest -q"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

PROTOTIPO = Path(__file__).resolve().parents[1]
if str(PROTOTIPO) not in sys.path:
    sys.path.insert(0, str(PROTOTIPO))


@pytest.fixture
def ollama_falso(monkeypatch):
    """Servidor HTTP local que imita o Ollama (/api/tags e /api/generate). Devolve o texto configurado."""
    estado = {"resposta": "", "prompts": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _json(self, dados):
            corpo = json.dumps(dados).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            self._json({"models": [{"name": "qwen2.5:7b"}]})

        def do_POST(self):
            pedido = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            estado["prompts"].append(pedido["prompt"])
            self._json({"response": estado["resposta"], "done": True})

    servidor = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    from pulso import agente
    monkeypatch.setattr(agente, "OLLAMA_URL", f"http://127.0.0.1:{servidor.server_port}")
    yield estado
    servidor.shutdown()
