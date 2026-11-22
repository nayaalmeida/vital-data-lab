"""A aba "Pergunte ao agente" fala com o serviço de referência da disciplina, e o ▼ só marca fraqueza que se repete."""
from pathlib import Path

import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from pulso import agente_referencia
from pulso.eixos import CICLOS, ITENS
from pulso.motor import fracos_persistentes

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _rodar():
    st.cache_data.clear()  # o estado do serviço fica em cache no app
    return AppTest.from_file(APP, default_timeout=180).run()


def _perguntar(at, texto):
    return at.chat_input(key="agente_pergunta").set_value(texto).run()


# ----------------------------------------------------------------------------- cliente

def test_cliente_envia_pergunta_e_recorte(agente_falso):
    r = agente_referencia.perguntar("Quais equipes precisam de atenção?", "distrito", "V", "2026.2")
    assert r["modo"] == "regras"
    assert agente_falso["pedidos"][-1] == {"pergunta": "Quais equipes precisam de atenção?",
                                           "escopo": {"nivel": "distrito", "id": "V"}, "ciclo": "2026.2"}


def test_cliente_traduz_a_recusa_do_servico(agente_falso):
    agente_falso["status"] = 404
    with pytest.raises(agente_referencia.ErroAgente, match="Distrito inexistente"):
        agente_referencia.perguntar("Como está o distrito IX?", "distrito", "IX")


def test_cliente_sem_servico(monkeypatch):
    monkeypatch.setattr(agente_referencia, "URL", "http://127.0.0.1:9")
    assert agente_referencia.saude() is None
    with pytest.raises(agente_referencia.ErroAgente, match="não respondeu"):
        agente_referencia.perguntar("Quais equipes precisam de atenção?")


# ----------------------------------------------------------------------------- aba no app

def test_aba_avisa_quando_o_servico_esta_fora(monkeypatch):
    monkeypatch.setattr(agente_referencia, "URL", "http://127.0.0.1:9")
    at = _rodar()
    assert not at.exception
    assert any("não respondeu" in i.value for i in at.info)


def test_aba_mostra_a_resposta_do_agente(agente_falso):
    at = _perguntar(_rodar(), "Qual a média da rede?")
    assert not at.exception
    assert agente_falso["pedidos"][-1]["escopo"] == {"nivel": "rede", "id": None}
    assert any("643,2" in m.value for m in at.markdown)
    assert any("modo: regras" in c.value for c in at.caption)


def test_aba_avisa_quando_o_texto_do_modelo_foi_rejeitado(agente_falso):
    agente_falso["resposta"]["verificacao"] = {"executada": True, "aprovada": False,
                                               "numeros_nao_encontrados": ["82"]}
    at = _perguntar(_rodar(), "Quanto a equipe caiu?")
    assert any("82" in w.value and "rejeitado" in w.value for w in at.warning)


def test_gestor_distrital_pergunta_sobre_o_proprio_distrito(agente_falso):
    at = _rodar()
    next(r for r in at.radio if r.label == "Perfil de acesso").set_value("Gestão distrital").run()
    next(s for s in at.selectbox if s.label == "Distrito sanitário").set_value("DS VIII").run()
    at = _perguntar(at, "Quais equipes precisam de atenção?")
    assert not at.exception
    assert agente_falso["pedidos"][-1]["escopo"] == {"nivel": "distrito", "id": "VIII"}


# ----------------------------------------------------------------------------- ponto fraco

def _base(equipe, pares):
    """Uma equipe e três pares no mesmo grupo, nos últimos ciclos; só o pré-natal varia."""
    ciclos = CICLOS[-len(equipe):]
    linhas = [{"equipe": "A", "grupo": "g", "ciclo": c, **dict.fromkeys(ITENS, 50.0), "prenatal": v}
              for c, v in zip(ciclos, equipe)]
    linhas += [{"equipe": f"P{n}", "grupo": "g", "ciclo": c, **dict.fromkeys(ITENS, 50.0), "prenatal": v}
               for n in range(3) for c, v in zip(ciclos, pares)]
    return pd.DataFrame(linhas)


def test_fraqueza_so_aparece_quando_se_repete_nos_3_ultimos_ciclos():
    assert fracos_persistentes(_base([40, 41, 42], [50, 50, 50]), "A", "g", CICLOS[-1]) == {"prenatal"}
    assert fracos_persistentes(_base([50, 50, 40], [50, 50, 50]), "A", "g", CICLOS[-1]) == set()


def test_sem_3_ciclos_de_historico_nao_ha_fraqueza():
    assert fracos_persistentes(_base([40, 40, 40], [50, 50, 50]), "A", "g", CICLOS[1]) == set()
