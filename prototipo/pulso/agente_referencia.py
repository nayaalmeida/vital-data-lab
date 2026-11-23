"""Cliente do agente Recife Monitora da disciplina (serviço HTTP de referência). Opcional.

O serviço roda à parte, a partir do material da disciplina (pasta `agente/`):

    uvicorn servico.api:app --port 8000

e responde sobre a base comum do desafio (`DADOS/`, 132 equipes), não sobre a base sintética
deste protótipo. Este app só envia a pergunta e o recorte, e mostra o que voltar: resposta,
fontes, modo e o resultado da verificação de números feita pelo serviço.

Ponto de partida: `exemplos/grupo1_streamlit.py` do agente de referência. O contrato completo
fica em http://127.0.0.1:8000/docs com o serviço no ar.

127.0.0.1, não "localhost": no Windows, o Python tenta primeiro o IPv6 de "localhost" e perde
uns 2 s a cada chamada esperando ele falhar.
"""

from __future__ import annotations

import os

import requests

URL = os.environ.get("AGENTE_URL", "http://127.0.0.1:8000")
TIMEOUT_CONSULTA = 3
# Em CPU, a primeira pergunta que vai ao modelo local pode levar até 1 minuto e meio.
TIMEOUT_PERGUNTA = 240


class ErroAgente(Exception):
    """O serviço está fora do ar ou recusou a pergunta (recorte inexistente, pergunta inválida)."""


def _get(caminho: str) -> dict | None:
    try:
        resposta = requests.get(f"{URL}{caminho}", timeout=TIMEOUT_CONSULTA)
        resposta.raise_for_status()
        return resposta.json()
    except (requests.RequestException, ValueError):
        return None


def saude() -> dict | None:
    """Estado do serviço (modelo, ciclos, régua de zonas), ou None se ele não responder."""
    return _get("/saude")


def escopos() -> dict | None:
    """Distritos, unidades, equipes e ciclos da base comum, para preencher os filtros."""
    return _get("/escopos")


def perguntar(pergunta: str, nivel: str = "rede", id: str | None = None, ciclo: str | None = None) -> dict:
    corpo = {"pergunta": pergunta, "escopo": {"nivel": nivel, "id": id}, "ciclo": ciclo}
    try:
        resposta = requests.post(f"{URL}/perguntar", json=corpo, timeout=TIMEOUT_PERGUNTA)
    except requests.RequestException as erro:
        raise ErroAgente(f"o serviço não respondeu em {URL} ({type(erro).__name__})") from erro
    if resposta.status_code >= 400:
        try:
            dados = resposta.json()
            motivo = dados.get("erro") or dados.get("detail")
        except ValueError:
            motivo = None
        if isinstance(motivo, list) and motivo:  # validação do FastAPI: lista de erros, em inglês
            motivo = motivo[0].get("msg") if isinstance(motivo[0], dict) else str(motivo[0])
        raise ErroAgente(f"o serviço recusou a pergunta ({resposta.status_code}): {motivo or resposta.reason}")
    return resposta.json()
