"""
Agrupamento de equipes por contexto do território — K-Means.

Serve para comparação justa (CP-FIT, Brown et al. 2019): cada equipe é comparada
com as de território parecido, não com a média da cidade. "Abaixo da média" pune
quem atende o território mais difícil; "abaixo dos pares" diz onde há espaço real.

O app (prototipo/pulso/motor.py · atribuir_grupos) usa K-Means com 4 grupos sobre
IDHM, saneamento e log da renda. Este módulo traz as mesmas peças de forma
genérica, para AVALIAR essa escolha no notebook 04 (silhueta por k) e para ser
reaproveitado quando a base real chegar com variáveis de território.

Dois limites declarados:
- A base comum do desafio (132 equipes) não traz IDHM, saneamento nem renda; nela a
  comparação justa é feita pelo GRUPO oficial (1 a 4), como o programa manda.
- k = 4 é escolha de domínio (quatro níveis de vulnerabilidade, legíveis pelo gestor),
  não o k de maior silhueta. A silhueta é reportada para mostrar que a estrutura
  com 4 grupos é razoável, e não para escolher sozinha.

Responsável: Nicolas Soares · leitura de domínio dos grupos: Danilo Brito
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

SEMENTE = 0          # mesma semente do app, para reproduzir os grupos exatamente
N_INICIOS = 20


def padronizar(df: pd.DataFrame, colunas: list[str], em_log: tuple[str, ...] = ()) -> np.ndarray:
    """Z-score das colunas (K-Means é sensível à escala). Colunas em `em_log` passam por log antes."""
    x = df[colunas].astype(float).copy()
    for c in em_log:
        x[c] = np.log(x[c])
    return StandardScaler().fit_transform(x)


def agrupar(Z: np.ndarray, k: int, semente: int = SEMENTE) -> np.ndarray:
    return KMeans(n_clusters=k, n_init=N_INICIOS, random_state=semente).fit_predict(Z)


def silhuetas(Z: np.ndarray, ks=range(2, 8), semente: int = SEMENTE) -> dict[int, float]:
    """Silhueta média para cada k. Acima de 0,5 = estrutura razoável; abaixo de 0,25 = fraca."""
    return {int(k): round(float(silhouette_score(Z, agrupar(Z, k, semente))), 3) for k in ks}


def resumo_grupos(df: pd.DataFrame, rotulos, colunas: list[str]) -> pd.DataFrame:
    """Média de cada variável por grupo e quantas equipes há em cada um."""
    return (df.assign(_grupo=np.asarray(rotulos))
              .groupby("_grupo")[colunas].mean()
              .assign(equipes=pd.Series(np.asarray(rotulos)).value_counts().sort_index().values)
              .round(3))
