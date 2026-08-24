"""
Limpeza, anonimização e integração.

REGRA INEGOCIÁVEL: a anonimização acontece ANTES de qualquer análise.
Nenhuma coluna com potencial de identificação individual sobrevive a
este módulo.

Toda decisão de tratamento tomada aqui precisa estar registrada em
docs/decisoes_limpeza.md — é o que sustenta o critério de Limpeza dos
Dados na avaliação.

Responsáveis: Marcela Santos (limpeza) e Leônidas Carvalho (integração)
"""

import pandas as pd

# Colunas que nunca podem chegar à base analítica.
# Se qualquer uma aparecer numa fonte nova, acrescente aqui.
COLUNAS_PROIBIDAS = [
    "cpf", "cns", "nome", "nome_paciente", "nome_mae",
    "data_nascimento", "endereco", "telefone", "email",
]


def remover_pii(df: pd.DataFrame) -> pd.DataFrame:
    """Descarta qualquer coluna com potencial de identificação individual."""
    achadas = [c for c in df.columns if c.strip().lower() in COLUNAS_PROIBIDAS]
    if achadas:
        print(f"[LGPD] Colunas removidas: {achadas}")
    return df.drop(columns=achadas, errors="ignore")


def tratar_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata valores ausentes.

    Registrar em docs/decisoes_limpeza.md, para cada coluna:
    o que foi feito, por quê, e quantas linhas foram afetadas.
    """
    raise NotImplementedError


def tratar_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata valores fora de faixa.

    Atenção: em indicadores de saúde, outlier pode ser dado real de uma
    unidade em situação crítica — exatamente o que queremos encontrar.
    Validar com Danilo Brito antes de descartar qualquer linha.
    """
    raise NotImplementedError


def integrar(sisab: pd.DataFrame, cnes: pd.DataFrame,
             ibge: pd.DataFrame, territorio: pd.DataFrame) -> pd.DataFrame:
    """
    Une as quatro bases pela chave CNES.

    Caminho: SISAB -> CNES -> Recife em Dados (distrito) -> IBGE (contexto).

    Reportar a taxa de casamento das chaves: ela é métrica de qualidade
    de dados e vira evidência na avaliação.
    """
    raise NotImplementedError
