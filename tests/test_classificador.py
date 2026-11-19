import numpy as np
import pandas as pd
import pytest

from src.indice.regua import faixa_acao
from src.modelos import classificador as clf


@pytest.fixture(scope="module")
def pares(base):
    return clf.montar_pares(base)


def test_alvo_e_a_faixa_do_ciclo_seguinte(base, pares):
    """Anti-vazamento: o alvo vem do PRÓXIMO ciclo da mesma equipe, nunca do atual."""
    amostra = pares.sample(50, random_state=0)
    for _, linha in amostra.iterrows():
        seguinte = base[(base["codigo_ine"] == linha["codigo_ine"]) &
                        (base["ciclo"].round(1) == round(linha["ciclo_seguinte"], 1))]
        assert len(seguinte) == 1
        assert faixa_acao(seguinte["pontuacao_final"].iloc[0]) == linha["alvo"]


def test_so_pares_consecutivos_e_sem_desclassificada(base, pares):
    ordem = {c: i for i, c in enumerate(sorted(base["ciclo"].unique()))}
    passo = pares["ciclo_seguinte"].map(ordem) - pares["ciclo"].map(ordem)
    assert (passo == 1).all()
    assert pares["faixa_atual"].notna().all() and pares["alvo"].notna().all()
    assert not pares.duplicated(["codigo_ine", "ciclo"]).any()


def test_bloco_a_sem_quorum_entra_como_ausente(pares):
    sem_quorum = pares["bloco_a_valido_num"] == 0
    assert sem_quorum.any()
    assert pares.loc[sem_quorum, "eixo1_bloco_a"].isna().all()


def test_matriz_tem_sempre_as_mesmas_colunas(pares):
    X1 = clf.matriz_X(pares)
    X2 = clf.matriz_X(pares[pares["distrito_sanitario"] == "Distrito Sanitário I"])
    assert list(X1.columns) == list(X2.columns)
    assert "alvo" not in X1.columns and "faixa_atual" not in X1.columns


def test_metricas_de_baseline_perfeita():
    m = clf.metricas(["Crítico", "Atenção"], ["Crítico", "Atenção"])
    assert m["acuracia"] == 1.0 and m["recall_critico"] == 1.0


def test_avaliacao_completa_e_reprodutivel(base, monkeypatch):
    """Versão rápida (poucas árvores) da avaliação: roda de ponta a ponta e dá o mesmo resultado duas vezes."""
    monkeypatch.setattr(clf, "N_ARVORES", 40)
    monkeypatch.setattr(clf, "GRADE", [{"min_samples_leaf": 3, "class_weight": "balanced"}])
    r1, r2 = clf.avaliar(base), clf.avaliar(base)
    assert r1["random_forest_teste_temporal"] == r2["random_forest_teste_temporal"]
    assert r1["n_treino"] + r1["n_teste"] == r1["n_pares"]
    teste = r1["_pares"]["ciclo_seguinte"].round(1).isin([2026.1, 2026.2])
    treino_ciclos = r1["_pares"].loc[~teste, "ciclo_seguinte"]
    assert treino_ciclos.max() < 2026.1  # nada do futuro no treino
    assert np.array(r1["matriz_confusao"]["valores"]).sum() == r1["n_teste"]
    # o modelo precisa, no mínimo, bater a classe mais comum
    assert r1["random_forest_teste_temporal"]["f1_macro"] > r1["baseline_classe_comum"]["f1_macro"]
