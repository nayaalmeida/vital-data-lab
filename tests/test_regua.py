import numpy as np
import pandas as pd

from src.indice.regua import comparar_reguas, faixa_acao, n_mudam_de_zona, zona


def test_faixas_de_acao_nos_limites():
    assert faixa_acao(0) == "Crítico"
    assert faixa_acao(499.9) == "Crítico"
    assert faixa_acao(500) == "Atenção"
    assert faixa_acao(749.9) == "Atenção"
    assert faixa_acao(750) == "Excelência"
    assert faixa_acao(1000) == "Excelência"


def test_desclassificada_nunca_vira_zero():
    assert faixa_acao(np.nan) is None
    assert faixa_acao(None) is None
    assert zona(np.nan) is None


def test_duas_reguas_de_zona():
    assert zona(860, "dicionario") == "Excelência" and zona(860, "manual") == "Qualidade"
    assert zona(560, "dicionario") == "Aperfeiçoamento" and zona(560, "manual") == "Crítica"
    assert zona(399, "dicionario") == zona(399, "manual") == "Insuficiente"


def test_contagem_de_mudanca_de_zona():
    s = pd.Series([860, 560, 399, np.nan])
    assert n_mudam_de_zona(s) == 2
    assert comparar_reguas(s).to_numpy().sum() == 3


def test_coluna_da_base_segue_o_dicionario(base):
    validas = base[base["zona_classificacao"].notna()]
    calculada = validas["pontuacao_final"].map(zona)
    assert (calculada == validas["zona_classificacao"]).all()
