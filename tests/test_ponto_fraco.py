import pandas as pd

from src.recomendacao.ponto_fraco import (cobertura_regra, item_mais_baixo,
                                          ponto_fraco_defensavel, taxa_repeticao)

ITENS = ["a", "b", "c"]


def painel(valores_por_ciclo):
    return pd.DataFrame([{"eq": "E1", "ciclo": c, **v} for c, v in valores_por_ciclo.items()])


def test_item_mais_baixo_ignora_vazios():
    df = pd.DataFrame({"a": [1, None], "b": [2, None], "c": [0.5, None]})
    r = item_mais_baixo(df, ITENS)
    assert r[0] == "c" and pd.isna(r[1])


def test_fraqueza_que_se_repete_e_defensavel():
    p = painel({1: {"a": 1, "b": 5, "c": 6}, 2: {"a": 2, "b": 5, "c": 6}, 3: {"a": 1, "b": 7, "c": 6}})
    assert ponto_fraco_defensavel(p, ITENS, "ciclo") == "a"


def test_fraqueza_que_troca_nao_e_apontada():
    p = painel({1: {"a": 1, "b": 5, "c": 6}, 2: {"a": 9, "b": 2, "c": 6}, 3: {"a": 1, "b": 7, "c": 6}})
    assert ponto_fraco_defensavel(p, ITENS, "ciclo") is None
    assert ponto_fraco_defensavel(p.head(2), ITENS, "ciclo") is None  # histórico curto


def test_taxa_de_repeticao_so_conta_ciclos_consecutivos():
    p = painel({1: {"a": 1, "b": 5, "c": 6}, 2: {"a": 1, "b": 5, "c": 6}, 3: {"a": 9, "b": 1, "c": 6}})
    r = taxa_repeticao(p, ITENS, "eq", "ciclo")
    assert r["pares"] == 2 and r["repete"] == 0.5


def test_base_comum_ponto_fraco_raramente_se_sustenta(base):
    validas = base[base["pontuacao_final"].notna()]
    ind = [f"IND{i:02d}" for i in range(1, 11)]
    assert taxa_repeticao(validas, ind, "codigo_ine", "ciclo")["repete"] < 0.3
    assert cobertura_regra(validas, ind, "codigo_ine", "ciclo")["equipes"] > 100
