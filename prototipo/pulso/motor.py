"""Motor de sugestões: aprende com o histórico de pactos quanto cada ação mudou cada item dos eixos.

Para cada item, uma regressão regularizada explica a variação entre um ciclo e o
seguinte a partir do ponto de partida, do território e das ações pactuadas. Os
termos de interação deixam o efeito de cada ação variar com o espaço que o item
tem para crescer e com a cobertura de ACS da equipe.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from .eixos import ACOES, CICLOS, EIXOS, ITENS, pontuacoes

# Efeitos menores que isso (pp) são tratados como ruído e não entram nas sugestões.
LIMIAR_EFEITO = 0.5
ALPHA = 3.0

GRUPOS = [
    "A · vulnerabilidade muito alta",
    "B · vulnerabilidade alta",
    "C · vulnerabilidade moderada",
    "D · vulnerabilidade baixa",
]


def atribuir_grupos(equipes: pd.DataFrame, seed: int = 0) -> pd.Series:
    """Agrupa as equipes pelo contexto do território, para comparar cada uma com as parecidas."""
    x = equipes[["idhm", "saneamento"]].assign(renda=np.log(equipes["renda"]))
    rotulos = KMeans(n_clusters=len(GRUPOS), n_init=20, random_state=seed).fit_predict(StandardScaler().fit_transform(x))
    ordem = pd.Series(equipes["idhm"].to_numpy()).groupby(rotulos).mean().sort_values().index
    nomes = {c: GRUPOS[i] for i, c in enumerate(ordem)}
    return pd.Series(rotulos, index=equipes.index).map(nomes)


def transicoes(painel: pd.DataFrame, equipes: pd.DataFrame, pactos: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por equipe e ciclo: estado no fim do ciclo, ações do pacto seguinte e variação de cada item."""
    seguinte = painel[["equipe", "t"] + list(ITENS)].assign(t=lambda d: d["t"] - 1)
    df = painel.merge(seguinte, on=["equipe", "t"], suffixes=("", "_seg"))
    df = df.merge(equipes[["equipe", "cobertura_acs", "idhm", "grupo"]], on="equipe", how="left")
    df["ciclo_pacto"] = df["t"].map(lambda t: CICLOS[t + 1])
    flags = (pactos.assign(v=1)
             .pivot_table(index=["equipe", "ciclo"], columns="acao", values="v", fill_value=0)
             .reindex(columns=list(ACOES), fill_value=0))
    df = df.merge(flags, left_on=["equipe", "ciclo_pacto"], right_index=True, how="left")
    df[list(ACOES)] = df[list(ACOES)].fillna(0)
    for i in ITENS:
        df[f"d_{i}"] = df[f"{i}_seg"] - df[i]
    return df


@dataclass
class Motor:
    coefs: dict[str, pd.Series]
    acs_media: float
    acs_dp: float
    mae_ia: float
    mae_sem_acoes: float
    curva: pd.DataFrame
    aplicacoes: pd.Series
    n_transicoes: int


def _features(df: pd.DataFrame, item: str, acs_media: float, acs_dp: float, com_acoes: bool = True) -> pd.DataFrame:
    folga = (100 - df[item]) / 50
    acs = (df["cobertura_acs"] - acs_media) / acs_dp
    x = {"folga": folga, "acs": acs, "idhm": df["idhm"]}
    if com_acoes:
        for a in ACOES:
            x[a] = df[a]
            x[f"{a}*folga"] = df[a] * folga
            x[f"{a}*acs"] = df[a] * acs
    return pd.DataFrame(x)


def _ajustar(trans: pd.DataFrame, acs_media: float, acs_dp: float, com_acoes: bool = True) -> dict[str, Ridge]:
    return {item: Ridge(alpha=ALPHA).fit(_features(trans, item, acs_media, acs_dp, com_acoes), trans[f"d_{item}"])
            for item in ITENS}


def _erro(modelos: dict, trans: pd.DataFrame, acs_media: float, acs_dp: float, com_acoes: bool = True) -> float:
    erros = [np.abs(m.predict(_features(trans, item, acs_media, acs_dp, com_acoes)) - trans[f"d_{item}"]).mean()
             for item, m in modelos.items()]
    return float(np.mean(erros))


def treinar(trans: pd.DataFrame) -> Motor:
    """Valida nos dois ciclos mais recentes, mede a curva de aprendizado e treina com todo o histórico."""
    acs_media, acs_dp = trans["cobertura_acs"].mean(), trans["cobertura_acs"].std()
    ultimo = trans["t"].max()
    treino, teste = trans[trans["t"] < ultimo - 1], trans[trans["t"] >= ultimo - 1]
    mae_ia = _erro(_ajustar(treino, acs_media, acs_dp), teste, acs_media, acs_dp)
    mae_sem = _erro(_ajustar(treino, acs_media, acs_dp, False), teste, acs_media, acs_dp, False)

    alvo = trans[trans["t"] == ultimo]
    curva = pd.DataFrame([
        {"ciclos": k, "mae": _erro(_ajustar(trans[trans["t"] < k], acs_media, acs_dp), alvo, acs_media, acs_dp)}
        for k in range(1, ultimo + 1)
    ])

    modelos = _ajustar(trans, acs_media, acs_dp)
    colunas = _features(trans.head(1), next(iter(ITENS)), acs_media, acs_dp).columns
    return Motor(
        coefs={item: pd.Series(m.coef_, index=colunas) for item, m in modelos.items()},
        acs_media=acs_media, acs_dp=acs_dp,
        mae_ia=mae_ia, mae_sem_acoes=mae_sem, curva=curva,
        aplicacoes=trans[list(ACOES)].sum().astype(int),
        n_transicoes=len(trans),
    )


def efeitos(motor: Motor, estado: pd.DataFrame) -> np.ndarray:
    """Ganho esperado (pp) de cada ação em cada item, por equipe: array [equipe, ação, item]."""
    acs = ((estado["cobertura_acs"] - motor.acs_media) / motor.acs_dp).to_numpy()
    res = np.zeros((len(estado), len(ACOES), len(ITENS)))
    for j, item in enumerate(ITENS):
        c = motor.coefs[item]
        folga = ((100 - estado[item]) / 50).to_numpy()
        for k, a in enumerate(ACOES):
            res[:, k, j] = c[a] + c[f"{a}*folga"] * folga + c[f"{a}*acs"] * acs
    return np.where(np.abs(res) >= LIMIAR_EFEITO, res, 0.0)


def efeitos_medios(motor: Motor, estado: pd.DataFrame) -> pd.DataFrame:
    """O que a IA aprendeu: efeito médio de cada ação em cada item, nas equipes de hoje."""
    return pd.DataFrame(efeitos(motor, estado).mean(axis=0), index=list(ACOES), columns=list(ITENS))


def projetar(estado: pd.DataFrame, delta: np.ndarray) -> pd.DataFrame:
    """Pontuação dos eixos depois de somar delta (pp) aos itens."""
    novo = (estado[list(ITENS)] + delta).clip(0, 100)
    return pontuacoes(novo)


def sugestoes(motor: Motor, estado: pd.DataFrame) -> pd.DataFrame:
    """Ganho esperado de cada ação em cada eixo, para todas as equipes do estado (uma linha por equipe e ação)."""
    ef = efeitos(motor, estado)
    atual = pontuacoes(estado)
    nomes = list(ITENS)
    partes = []
    for k, a in enumerate(ACOES):
        ganho = projetar(estado, ef[:, k, :]) - atual
        itens = [
            sorted(((nomes[j], ef[e, k, j]) for j in range(len(nomes)) if ef[e, k, j] > 0), key=lambda p: -p[1])
            for e in range(len(estado))
        ]
        partes.append(pd.DataFrame({
            "equipe": estado["equipe"].to_numpy(), "acao": a,
            **{f"ganho_{e}": ganho[e].to_numpy() for e in EIXOS},
            "itens": itens,
        }))
    return pd.concat(partes, ignore_index=True)


def evidencia(trans: pd.DataFrame, acao: str, item: str, valor: float, faixa: float = 10) -> dict:
    """Comparação direta no histórico: equipes que partiram de um valor parecido, com e sem a ação."""
    perto = trans[(trans[item] - valor).abs() <= faixa]
    com, sem = perto[perto[acao] == 1][f"d_{item}"], perto[perto[acao] == 0][f"d_{item}"]
    return {"n_com": len(com), "media_com": com.mean() if len(com) else np.nan,
            "n_sem": len(sem), "media_sem": sem.mean() if len(sem) else np.nan}


def confianca(n_aplicacoes: int) -> str:
    if n_aplicacoes >= 150:
        return "alta"
    if n_aplicacoes >= 60:
        return "média"
    return "baixa"
