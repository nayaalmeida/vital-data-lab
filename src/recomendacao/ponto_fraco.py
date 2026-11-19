"""
Ponto fraco defensável — só apontar como fraqueza o que se repete.

O PROBLEMA (alerta do professor, seção 12 do agente de referência)
    Dizer "o ponto fraco desta equipe é X" a partir de UM ciclo é frágil: o item mais
    baixo muda de um ciclo para o outro na grande maioria dos casos. Na base comum,
    o indicador mais baixo do Eixo 3 se repete no ciclo seguinte em só ~11% dos pares
    (medido no notebook 04). Apontar isso como fraqueza seria apontar ruído — e,
    num programa que não pode punir equipe, ruído apontado vira injustiça.

A REGRA ADOTADA
    Um item só é ponto fraco se foi o mais baixo da equipe em `minimo` dos últimos
    `janela` ciclos consecutivos (padrão: 3 de 3). Caso contrário, a resposta é
    "não há ponto fraco defensável" (None), e a tela mostra os eixos sem eleger um vilão.

Funciona com qualquer painel em formato largo: uma linha por equipe e ciclo, uma
coluna por item. Serve para a base comum (IND01–IND10) e para o protótipo.
"""

from __future__ import annotations

import pandas as pd


def _ordenar(painel: pd.DataFrame, id_col: str, ciclo_col: str) -> pd.DataFrame:
    ordem = {c: i for i, c in enumerate(sorted(painel[ciclo_col].dropna().unique()))}
    return (painel.assign(_idx=painel[ciclo_col].map(ordem))
                  .sort_values([id_col, "_idx"]).reset_index(drop=True))


def item_mais_baixo(painel: pd.DataFrame, itens: list[str]) -> pd.Series:
    """Nome do item com o menor valor em cada linha (itens vazios são ignorados)."""
    valores = painel[itens].astype(float)
    tem_valor = valores.notna().any(axis=1)
    resultado = pd.Series(None, index=painel.index, dtype=object)
    resultado[tem_valor] = valores[tem_valor].idxmin(axis=1)
    return resultado


def taxa_repeticao(painel: pd.DataFrame, itens: list[str], id_col: str, ciclo_col: str) -> dict:
    """
    Em quantos pares de ciclos consecutivos o item mais baixo se repete.

    Devolve {"pares": n, "repete": proporção, "muda": proporção}.
    """
    p = _ordenar(painel, id_col, ciclo_col)
    p["_baixo"] = item_mais_baixo(p, itens)
    g = p.groupby(id_col)
    seguinte, idx_seg = g["_baixo"].shift(-1), g["_idx"].shift(-1)
    ok = (idx_seg - p["_idx"] == 1) & p["_baixo"].notna() & seguinte.notna()
    repete = float((p.loc[ok, "_baixo"] == seguinte[ok]).mean()) if ok.any() else float("nan")
    return {"pares": int(ok.sum()), "repete": round(repete, 3), "muda": round(1 - repete, 3)}


def ponto_fraco_defensavel(historico: pd.DataFrame, itens: list[str], ciclo_col: str,
                           janela: int = 3, minimo: int = 3) -> str | None:
    """
    Histórico de UMA equipe → item que foi o mais baixo em `minimo` dos últimos
    `janela` ciclos, ou None se não houver item que se sustente.
    """
    if historico.empty:
        return None
    h = historico.sort_values(ciclo_col).tail(janela)
    if len(h) < minimo:
        return None
    contagem = item_mais_baixo(h, itens).value_counts()
    if contagem.empty or contagem.iloc[0] < minimo:
        return None
    return str(contagem.index[0])


def cobertura_regra(painel: pd.DataFrame, itens: list[str], id_col: str, ciclo_col: str,
                    janela: int = 3, minimo: int = 3) -> dict:
    """No último ciclo, quantas equipes têm um ponto fraco defensável pela regra."""
    ultimo = painel[ciclo_col].max()
    com_dado = painel[painel[itens].notna().any(axis=1)]
    equipes = com_dado.loc[com_dado[ciclo_col] == ultimo, id_col].unique()
    achados = {e: ponto_fraco_defensavel(com_dado[com_dado[id_col] == e], itens, ciclo_col, janela, minimo)
               for e in equipes}
    n_com = sum(v is not None for v in achados.values())
    return {"equipes": len(equipes), "com_ponto_fraco": n_com,
            "proporcao": round(n_com / len(equipes), 3) if len(equipes) else float("nan")}
