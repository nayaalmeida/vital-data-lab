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


@pytest.fixture
def agente_falso(monkeypatch):
    """Servidor HTTP local que imita o agente de referência da disciplina (/saude, /escopos, /perguntar)."""
    estado = {
        "pedidos": [],
        "status": 200,
        "resposta": {
            "base": "sintética", "resposta": "A média do distrito V no ciclo 2026.2 é 643,2 pontos.",
            "modo": "regras", "recorte": "Distrito Sanitário V", "ciclo": "2026.2",
            "fontes": [{"tabela": "resultados_ciclos", "campos": ["pontuacao_final"]}],
            "verificacao": {"executada": False, "aprovada": None, "numeros_nao_encontrados": []},
        },
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _json(self, dados, status=200):
            corpo = json.dumps(dados).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            if self.path.startswith("/saude"):
                self._json({"status": "ok", "ciclos": ["2026.1", "2026.2"],
                            "modelo": {"nome": "qwen2.5:7b", "acessivel": False},
                            "regua_zonas": [{"zona": "Excelência", "a_partir_de": 850},
                                            {"zona": "Qualidade", "a_partir_de": 700},
                                            {"zona": "Aperfeiçoamento", "a_partir_de": 550},
                                            {"zona": "Crítica", "a_partir_de": 400}]})
            elif self.path.startswith("/escopos"):
                self._json({"ciclos": ["2026.1", "2026.2"],
                            "distritos": [{"id": "V", "nome": "Distrito Sanitário V"},
                                          {"id": "VIII", "nome": "Distrito Sanitário VIII"}],
                            "equipes": [{"id": "6000000008", "nome": "Equipe 009", "unidade": "USF V-842"}]})
            else:
                self._json({"erro": "não encontrado"}, 404)

        def do_POST(self):
            estado["pedidos"].append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            if estado["status"] == 200:
                self._json(estado["resposta"])
            else:
                self._json({"erro": "Distrito inexistente: IX"}, estado["status"])

    servidor = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    from pulso import agente_referencia
    monkeypatch.setattr(agente_referencia, "URL", f"http://127.0.0.1:{servidor.server_port}")
    yield estado
    servidor.shutdown()
