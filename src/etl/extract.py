"""
Carregamento das bases de dados fornecidas para o projeto.

Esta etapa realiza apenas a leitura dos arquivos em data/raw/,
sem aplicar tratamentos ou transformações.
"""

from pathlib import Path

import pandas as pd


RAW = Path(__file__).resolve().parents[2] / "data" / "raw"

ARQUIVOS = {
    "equipes": "equipes.csv",
    "resultados": "resultados_ciclos.csv",
    "eixo3": "eixo3_indicadores.csv",
    "nps": "nps_atributos.csv",
    "planos": "planos_acao.csv",
}


def carregar_dados():
    """
    Carrega as cinco bases de dados do projeto.

    Retorna
    -------
    dict[str, pd.DataFrame]
        Dicionário contendo um DataFrame para cada base.
    """

    bases = {}

    for nome, arquivo in ARQUIVOS.items():
        caminho = RAW / arquivo

        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

        dtype = {"codigo_ine": "string"}

        if nome == "equipes":
            dtype["codigo_cnes"] = "string"

        bases[nome] = pd.read_csv(caminho, dtype=dtype)

    return bases


if __name__ == "__main__":
    bases = carregar_dados()

    print("Bases carregadas com sucesso:\n")

    for nome, df in bases.items():
        print(f"{nome}: {df.shape}")