"""
Orquestrador do pipeline. É este arquivo que o README manda executar.

    python src/etl/pipeline.py

Ordem: obter base -> anonimizar -> calcular índice -> agrupar -> recomendar -> salvar.

Enquanto a SEAB não libera os dados reais, o pipeline roda sobre a base
SIMULADA gerada por src/dados_sinteticos/gerar.py. A troca por dado real é
substituição de arquivo: basta colocar a base analítica real em
data/processed/base_analitica.csv que o pipeline passa a usá-la.

Responsável: Leônidas Carvalho
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.dados_sinteticos import gerar as sintetico          # noqa: E402
from src.etl import transform                                # noqa: E402
from src.indice import pulso                                 # noqa: E402
from src.modelos import clusterizacao                        # noqa: E402
from src.recomendacao import motor                           # noqa: E402

BASE_REAL = Path("data/processed/base_analitica.csv")
BASE_SIMULADA = Path("data/processed/base_analitica_SIMULADA.csv")
SAIDA_PULSO = Path("data/processed/pulso_por_unidade.csv")
SAIDA_RECOMENDACOES = Path("data/processed/recomendacoes.csv")


def obter_base() -> tuple[pd.DataFrame, str]:
    """Usa a base real se ela existir; senão, gera a simulada."""
    if BASE_REAL.exists():
        return pd.read_csv(BASE_REAL), "REAL"
    if not BASE_SIMULADA.exists():
        sintetico.salvar(sintetico.gerar())
    return pd.read_csv(BASE_SIMULADA), "SIMULADO"


def executar() -> pd.DataFrame:
    print("[1/5] Obtendo base analítica...")
    df, origem = obter_base()
    if origem == "SIMULADO":
        print("       >>> ATENÇÃO: dados SIMULADOS. Rotular como tal em qualquer tela ou slide.")
    print(f"       {len(df)} equipes.")

    print("[2/5] Removendo dados pessoais...")
    df = transform.remover_pii(df)

    print("[3/5] Calculando o Pulso da Unidade...")
    df = pulso.calcular_pulso(df)

    print("[4/5] Agrupando unidades semelhantes...")
    df = clusterizacao.agrupar(df)

    print("[5/5] Gerando recomendações...")
    recomendacoes = motor.gerar(df)

    SAIDA_PULSO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA_PULSO, index=False, encoding="utf-8")
    recomendacoes.to_csv(SAIDA_RECOMENDACOES, index=False, encoding="utf-8")

    print()
    print(f"Base com índice:  {SAIDA_PULSO}")
    print(f"Recomendações:    {SAIDA_RECOMENDACOES}  ({len(recomendacoes)} geradas)")
    print()
    print(df["classificacao"].value_counts().to_string())
    return df


if __name__ == "__main__":
    executar()
