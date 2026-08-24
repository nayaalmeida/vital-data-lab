"""
Agrupamento de unidades por perfil de desempenho e contexto.

Técnica: K-Means.

Serve para comparação justa: uma unidade é comparada com as suas
semelhantes, não com a média do município.

Responsável: Cauã Cabral (Cientista de Dados)
"""

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

SEMENTE = 42


def escolher_k(X, faixa=range(2, 9)):
    """
    Escolhe o número de grupos pelo silhouette score.

    Registrar o gráfico da escolha: ele é evidência do critério de
    Avaliação do Modelo.
    """
    raise NotImplementedError


def agrupar(X, k: int):
    """Ajusta o K-Means e devolve o rótulo de grupo de cada unidade."""
    raise NotImplementedError


def descrever_grupos(df, rotulos):
    """
    Descreve cada grupo em linguagem de gestão.

    Grupo sem nome compreensível não serve ao gestor. Nomear com Danilo
    Brito — por exemplo: "alta cobertura, contexto vulnerável".
    """
    raise NotImplementedError
