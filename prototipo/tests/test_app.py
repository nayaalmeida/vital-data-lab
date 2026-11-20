"""O app sobe inteiro sem o Ollama (como no Streamlit Cloud) e, com ele, mostra o texto conferido."""
from pathlib import Path

import streamlit as st
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _rodar(**estado):
    st.cache_data.clear()  # a checagem do Ollama fica em cache por 60 s no app
    at = AppTest.from_file(APP, default_timeout=180)
    for chave, valor in estado.items():
        at.session_state[chave] = valor
    return at.run()


def test_app_sem_ia_local_fica_igual(monkeypatch):
    from pulso import agente
    monkeypatch.setattr(agente, "OLLAMA_URL", "http://127.0.0.1:9")
    at = _rodar()
    assert not at.exception
    assert not any(t.label == "Redação por IA local" for t in at.toggle)
    assert not any("IA local" in b.label for b in at.button)


def test_app_com_ia_local_mostra_texto_conferido(ollama_falso):
    ollama_falso["resposta"] = "Ação com bom retorno no histórico para esta equipe."
    at = _rodar()
    assert any(t.label == "Redação por IA local" for t in at.toggle)
    at.toggle(key="ia_local").set_value(True).run()
    botoes = [b for b in at.button if b.label == "Redigir para o pacto (IA local)"]
    assert botoes, "o botão deveria aparecer em cada sugestão"
    botoes[0].click().run()
    assert not at.exception
    assert any("Redigido por IA local" in m.value for m in at.markdown)
