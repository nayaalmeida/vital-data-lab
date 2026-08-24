"""
Agrupamento de unidades por perfil de desempenho e contexto.

Técnica: K-Means.

Serve para comparação justa: uma unidade é comparada com as suas semelhantes,
não com a média do município. É o que permite dizer ao gestor "a sua unidade
está 22 pontos abaixo das unidades de contexto parecido" em vez de "abaixo da
média", que não significa nada para quem atende um território difícil.

Responsável: Cauã Cabral · nomes dos grupos validados com Danilo Brito
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

SEMENTE = 42

VARIAVEIS = [
    "eixo_indicadores_assistenciais",
    "eixo_autoavaliacao_equipes",
    "eixo_satisfacao_usuarios",
    "idhm_bairro",
    "saneamento_pct",
]


def preparar(df: pd.DataFrame):
    """Padroniza as variáveis — o K-Means é sensível a escala."""
    return StandardScaler().fit_transform(df[VARIAVEIS])


def escolher_k(X, faixa=range(2, 9), semente: int = SEMENTE):
    """
    Escolhe o número de grupos pelo silhouette score.

    Devolve (melhor_k, {k: score}). Registrar o gráfico dessa escolha:
    ele é evidência para o critério de Avaliação do Modelo.
    """
    notas = {}
    for k in faixa:
        rotulos = KMeans(n_clusters=k, n_init=10, random_state=semente).fit_predict(X)
        notas[k] = round(float(silhouette_score(X, rotulos)), 3)
    melhor = max(notas, key=notas.get)
    return melhor, notas


def agrupar(df: pd.DataFrame, k: int | None = None, semente: int = SEMENTE) -> pd.DataFrame:
    """Acrescenta a coluna `grupo` ao dataframe."""
    X = preparar(df)
    if k is None:
        k, _ = escolher_k(X, semente=semente)
    modelo = KMeans(n_clusters=k, n_init=10, random_state=semente)
    resultado = df.copy()
    resultado["grupo"] = modelo.fit_predict(X)
    return resultado


def descrever_grupos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Descreve cada grupo em linguagem de gestão.

    Grupo sem nome compreensível não serve ao gestor: "grupo 3" não diz nada,
    "desempenho médio em contexto vulnerável" diz tudo.
    """
    resumo = df.groupby("grupo").agg(
        equipes=("unidade", "count"),
        pulso_mediano=("pulso", "median"),
        desempenho=("eixo_indicadores_assistenciais", "mean"),
        idhm_medio=("idhm_bairro", "mean"),
    ).round(2)

    def nomear(linha):
        desempenho = ("alto" if linha["desempenho"] >= 66
                      else "médio" if linha["desempenho"] >= 40 else "baixo")
        contexto = ("favorável" if linha["idhm_medio"] >= 0.72
                    else "intermediário" if linha["idhm_medio"] >= 0.62 else "vulnerável")
        return f"desempenho {desempenho}, contexto {contexto}"

    resumo["descricao"] = resumo.apply(nomear, axis=1)
    return resumo
