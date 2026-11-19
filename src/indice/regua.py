"""
Réguas usadas pelo Vital Data Lab sobre a pontuação oficial do Recife Monitora (0 a 1.000).

Há duas coisas diferentes aqui, e o projeto não mistura as duas:

1. FAIXA DE AÇÃO (nossa, para priorizar): Crítico < 500 · Atenção 500–749 · Excelência ≥ 750.
   É o semáforo do Tripé de Ação. Serve para ordenar onde a gestão vai primeiro.

2. ZONA DE CERTIFICAÇÃO (do programa): cinco zonas. Existem duas versões em circulação,
   e elas não batem:
     - Manual de Avaliação de Qualidade (5ª versão): 900 / 800 / 600 / 400
     - Dicionário de dados da base comum:            850 / 700 / 550 / 400
   A coluna `zona_classificacao` da base segue o dicionário. A divergência foi
   apontada pelo professor e levada ao NIIMA. Enquanto não houver resposta,
   o projeto usa o dicionário (é o que a base reflete) e declara a diferença.

Regra comum às duas: pontuação ausente (equipe desclassificada) não tem faixa nem
zona. Ausência de dado nunca vira nota zero.
"""

from __future__ import annotations

import math

import pandas as pd

ORDEM_FAIXAS = ["Crítico", "Atenção", "Excelência"]
LIMITE_ATENCAO = 500
LIMITE_EXCELENCIA = 750

ZONAS_DICIONARIO = [(850, "Excelência"), (700, "Qualidade"), (550, "Aperfeiçoamento"), (400, "Crítica")]
ZONAS_MANUAL = [(900, "Excelência"), (800, "Qualidade"), (600, "Aperfeiçoamento"), (400, "Crítica")]
ZONA_ABAIXO = "Insuficiente"
REGUAS = {"dicionario": ZONAS_DICIONARIO, "manual": ZONAS_MANUAL}


def _ausente(valor) -> bool:
    return valor is None or (isinstance(valor, float) and math.isnan(valor)) or pd.isna(valor)


def faixa_acao(pontuacao) -> str | None:
    """Faixa do semáforo de ação. Devolve None quando não há pontuação (desclassificada)."""
    if _ausente(pontuacao):
        return None
    if pontuacao < LIMITE_ATENCAO:
        return "Crítico"
    if pontuacao < LIMITE_EXCELENCIA:
        return "Atenção"
    return "Excelência"


def zona(pontuacao, regua: str = "dicionario") -> str | None:
    """Zona de certificação do programa, na régua escolhida ('dicionario' ou 'manual')."""
    if _ausente(pontuacao):
        return None
    for corte, nome in REGUAS[regua]:
        if pontuacao >= corte:
            return nome
    return ZONA_ABAIXO


def comparar_reguas(pontuacoes: pd.Series) -> pd.DataFrame:
    """Tabela cruzada Manual × Dicionário. Fora da diagonal estão as equipes-ciclo que mudam de zona."""
    validas = pontuacoes.dropna()
    return pd.crosstab(validas.map(lambda p: zona(p, "manual")).rename("zona_manual"),
                       validas.map(lambda p: zona(p, "dicionario")).rename("zona_dicionario"))


def n_mudam_de_zona(pontuacoes: pd.Series) -> int:
    """Quantas equipes-ciclo trocam de zona entre a régua do Manual e a do dicionário."""
    validas = pontuacoes.dropna()
    return int((validas.map(lambda p: zona(p, "manual")) != validas.map(lambda p: zona(p, "dicionario"))).sum())
