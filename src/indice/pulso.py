"""
Cálculo do Pulso da Unidade — índice composto de 0 a 100.

O índice combina os três eixos do Recife Monitora e é ajustado pelo
contexto socioterritorial obtido do IBGE. É esse ajuste que sustenta o
princípio de justiça do projeto: comparar unidades pelo desempenho
relativo ao seu território, não pela sorte de território.

Responsável: Cauã Cabral (Cientista de Dados)
Validação dos indicadores: Danilo Brito (Domínio e Conformidade)
"""

import pandas as pd

# Peso de cada eixo na composição do índice.
# DEFINIR EM REUNIÃO com Danilo Brito e registrar a justificativa no
# Documento Mestre. Peso escolhido sem justificativa registrada não
# sustenta a defesa do índice.
PESOS = {
    "indicadores_assistenciais": None,   # eixo 1 — SISAB
    "autoavaliacao_equipes":     None,   # eixo 2 — Recife Monitora
    "satisfacao_usuarios":       None,   # eixo 3 — Recife Monitora
}

# Faixas do semáforo. Validar com a Secretaria antes de fixar.
FAIXAS = {
    "Crítico":    (0, 50),
    "Atenção":    (50, 75),
    "Excelência": (75, 100),
}


def normalizar(serie: pd.Series) -> pd.Series:
    """Leva uma métrica para a escala 0-100, preservando a ordem."""
    raise NotImplementedError


def ajustar_por_contexto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajusta o desempenho bruto pelo contexto socioterritorial.

    Entram aqui IDHM, saneamento e renda do bairro da unidade.
    O objetivo NÃO é premiar território pobre nem punir território rico:
    é comparar cada unidade com o que é razoável esperar no seu contexto.
    """
    raise NotImplementedError


def calcular_pulso(df: pd.DataFrame) -> pd.DataFrame:
    """Devolve o dataframe com as colunas `pulso` (0-100) e `classificacao`."""
    raise NotImplementedError
