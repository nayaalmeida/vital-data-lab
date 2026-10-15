"""
Integração das bases tratadas do projeto.

A base analítica principal possui granularidade de equipe por ciclo.
"""
from pathlib import Path
import pandas as pd


def integrar(bases):
    """
    Integra os resultados por ciclo aos dados cadastrais das equipes.

    A base resultante mantém uma linha por equipe e ciclo.
    """

    equipes = bases["equipes"].copy()
    resultados = bases["resultados"].copy()

    ines_equipes = set(
        equipes["codigo_ine"].dropna()
    )

    mascara_com_equipe = (
        resultados["codigo_ine"].isin(ines_equipes)
    )

    resultados_validos = (
        resultados.loc[mascara_com_equipe]
        .copy()
    )

    base_integrada = resultados_validos.merge(
        equipes,
        on="codigo_ine",
        how="left",
        validate="many_to_one"
    )
    # ---------------------------------------------------------
    # 3. Integração do detalhamento dos indicadores do Eixo 3
    # ---------------------------------------------------------

    eixo3 = bases["eixo3"].copy()

    eixo3_pivot = eixo3.pivot(
        index=["codigo_ine", "ciclo"],
        columns="codigo_indicador",
        values="percentual_alcancado"
    ).reset_index()

    # Remove o nome do eixo criado pelo pivot
    eixo3_pivot.columns.name = None

    base_integrada = base_integrada.merge(
        eixo3_pivot,
        on=["codigo_ine", "ciclo"],
        how="left",
        validate="one_to_one"
    )
    # ---------------------------------------------------------
    # 4. Integração dos atributos de NPS
    # ---------------------------------------------------------

    nps = bases["nps"].copy()

    nps_pivot = nps.pivot(
        index=["codigo_ine", "ciclo"],
        columns="codigo_atributo",
        values="nps"
    ).reset_index()

    nps_pivot.columns.name = None

    base_integrada = base_integrada.merge(
        nps_pivot,
        on=["codigo_ine", "ciclo"],
        how="left",
        validate="one_to_one"
    )
    # ---------------------------------------------------------
    # 5. Integração dos planos de ação
    # ---------------------------------------------------------

    planos = bases["planos"].copy()

    base_integrada = base_integrada.merge(
        planos,
        on=["codigo_ine", "ciclo"],
        how="left",
        validate="one_to_one"
    )
    return base_integrada

def salvar_base_analitica(base_integrada, caminho_saida=None):
    """
    Salva a base analítica integrada em data/processed/.
    """

    if caminho_saida is None:
        caminho_saida = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "processed"
            / "base_analitica.csv"
        )

    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    base_integrada.to_csv(
        caminho_saida,
        index=False
    )

    return caminho_saida