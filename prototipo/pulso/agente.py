"""Redação da justificativa por um modelo de linguagem LOCAL, com verificação de números. Opcional.

Como funciona
    O motor (Ridge) calcula tudo: a ação, o item, o valor de hoje, o efeito esperado e a
    evidência do histórico. O modelo de linguagem só REESCREVE esses fatos em duas frases
    para o gestor. Depois, a verificação confere cada número do texto: se aparecer um
    número que não está nos fatos calculados, o texto é descartado e a tela fica só com a
    justificativa do catálogo (que já aparece sempre). Ideia copiada da peça
    `servico/verificacao.py` do agente de referência da disciplina.

Por que local
    Roda no Ollama, na própria máquina (qwen2.5:7b). Nenhum dado sai do computador e não
    há chave de API — IA soberana, como o cliente pediu em 10/09.

Quando liga
    Só quando o Ollama responde em http://localhost:11434 com o modelo baixado. No Streamlit
    Cloud ele não existe, então o app publicado continua exatamente igual.

Limite declarado (seção 3 do README do professor)
    A verificação garante que todo número do texto existe nos fatos, mas NÃO garante que o
    número foi atribuído ao item certo. Por isso o texto aparece marcado como "redigido por
    IA local" e a pessoa revisa antes de levar ao pacto.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Iterable

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODELO = os.environ.get("VDL_MODELO", "qwen2.5:7b")
TOLERANCIA = 0.051  # aceita o mesmo número arredondado para uma casa

# Número em português ou inglês: 12 · 12,5 · 12.5 · 1.234 · 1.234,5 · -3,2
_NUMERO = re.compile(r"(?<![\w])[-+]?\d{1,3}(?:\.\d{3})+(?:,\d+)?(?![\d])|(?<![\w])[-+]?\d+(?:[.,]\d+)?(?![\d])")


@dataclass
class Resultado:
    ok: bool
    texto: str | None
    motivo: str = ""
    numeros_rejeitados: list[float] = field(default_factory=list)


# ----------------------------------------------------------------------------- verificação

def _para_float(trecho: str) -> float:
    t = trecho.replace("+", "")
    if re.fullmatch(r"-?\d{1,3}(?:\.\d{3})+(?:,\d+)?", t):      # 1.234 ou 1.234,5
        t = t.replace(".", "").replace(",", ".")
    else:                                                     # 12,5 ou 12.5
        t = t.replace(",", ".")
    return float(t)


def numeros_do_texto(texto: str) -> list[float]:
    """Todos os números que aparecem no texto, já convertidos para float."""
    return [_para_float(m.group(0)) for m in _NUMERO.finditer(texto)]


def verificar(texto: str, permitidos: Iterable[float], tolerancia: float = TOLERANCIA) -> tuple[bool, list[float]]:
    """
    Todo número do texto precisa existir entre os permitidos (com a tolerância de
    arredondamento). Sinal é ignorado: "-2,3 pp" e "caiu 2,3 pp" são o mesmo fato.
    Devolve (aprovado, números intrusos).
    """
    base = [abs(float(p)) for p in permitidos]
    intrusos = [n for n in numeros_do_texto(texto)
                if not any(abs(abs(n) - p) <= tolerancia for p in base)]
    return (not intrusos, intrusos)


# ----------------------------------------------------------------------------- modelo local

def ollama_disponivel(timeout: float = 0.8) -> bool:
    """True se o Ollama está rodando E o modelo já foi baixado (ollama pull qwen2.5:7b)."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=timeout) as resp:
            nomes = [m.get("name", "") for m in json.load(resp).get("models", [])]
    except (urllib.error.URLError, OSError, ValueError):
        return False
    return MODELO in nomes or f"{MODELO}:latest" in nomes


def gerar_ollama(prompt: str, timeout: float = 120) -> str:
    """Uma chamada ao /api/generate do Ollama, sem streaming e com temperatura baixa."""
    corpo = json.dumps({"model": MODELO, "prompt": prompt, "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 160}}).encode("utf-8")
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=corpo,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp).get("response", "").strip()


def montar_prompt(fatos: dict) -> str:
    linhas = "\n".join(f"- {chave}: {valor}" for chave, valor in fatos.items())
    return (
        "Você escreve para gestores da Atenção Básica do Recife. Reescreva os FATOS abaixo em no "
        "máximo duas frases curtas, em português do Brasil, tom humano e sem culpar a equipe.\n"
        "Regras: use SOMENTE os números que aparecem nos FATOS, escritos do mesmo jeito; não invente "
        "número, prazo, meta ou porcentagem; não cite pessoas; não use listas nem títulos.\n\n"
        f"FATOS:\n{linhas}\n\nTexto:"
    )


def redigir(fatos: dict, permitidos: Iterable[float],
            gerar: Callable[[str], str] = gerar_ollama) -> Resultado:
    """
    Pede o texto ao modelo e só devolve se passar na verificação.
    Qualquer falha (Ollama fora do ar, demora, número inventado) devolve ok=False e texto=None.
    """
    try:
        texto = gerar(montar_prompt(fatos))
    except (urllib.error.URLError, OSError, TimeoutError, ValueError) as erro:
        return Resultado(False, None, f"modelo local indisponível ({type(erro).__name__})")
    texto = (texto or "").strip().strip('"').strip()
    if not texto:
        return Resultado(False, None, "o modelo devolveu texto vazio")
    # Números que já vêm escritos nos fatos (ex.: "1ª consulta" no título da ação) também valem.
    todos = list(permitidos) + [n for v in fatos.values() for n in numeros_do_texto(str(v))]
    aprovado, intrusos = verificar(texto, todos)
    if not aprovado:
        return Resultado(False, None, "o texto citou número que não está nos dados", intrusos)
    return Resultado(True, texto)


def fatos_da_sugestao(titulo_acao: str, item: str, valor_atual: float, efeito_pp: float,
                      n_com: int, media_com: float, media_sem: float) -> tuple[dict, list[float]]:
    """Monta os fatos de uma sugestão do motor e a lista de números permitidos na resposta."""
    atual = round(float(valor_atual))
    esperado = round(min(float(valor_atual) + float(efeito_pp), 100))
    ganho = round(float(efeito_pp), 1)
    fatos = {
        "ação sugerida": titulo_acao,
        "item que mais melhora": item,
        "valor de hoje": f"{atual}%",
        "valor esperado no fim do próximo ciclo": f"{esperado}%",
        "ganho esperado": f"{ganho:+.1f} pontos percentuais".replace(".", ","),
        "evidência": (f"{n_com} equipes com valor parecido fizeram essa ação e variaram "
                      f"{media_com:+.1f} pontos percentuais; as que não fizeram variaram "
                      f"{media_sem:+.1f}").replace(".", ","),
    }
    permitidos = [atual, esperado, ganho, n_com, round(media_com, 1), round(media_sem, 1)]
    return fatos, permitidos
