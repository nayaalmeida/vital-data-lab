"""
Salvamento das bases processadas pelo pipeline de dados.
"""

from pathlib import Path
import pandas as pd


PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"


def salvar_bases_tratadas(bases):
    """
    Salva as cinco bases tratadas em data/processed/.
    """
    PROCESSED.mkdir(parents=True, exist_ok=True)

    nomes_arquivos = {
        "equipes": "equipes_tratado.csv",
        "resultados": "resultados_ciclos_tratado.csv",
        "eixo3": "eixo3_indicadores_tratado.csv",
        "nps": "nps_atributos_tratado.csv",
        "planos": "planos_acao_tratado.csv",
    }

    for nome, arquivo in nomes_arquivos.items():
        bases[nome].to_csv(PROCESSED / arquivo, index=False)


def salvar_base_analitica(
    base_integrada: pd.DataFrame,
    caminho_saida=None
):
    """
    Salva a base analítica integrada em data/processed/.
    """
    if caminho_saida is None:
        caminho_saida = PROCESSED / "base_analitica.csv"

    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    base_integrada.to_csv(caminho_saida, index=False)

    return caminho_saida