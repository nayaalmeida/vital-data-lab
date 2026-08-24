"""
Vital Data Lab — dashboard do Pulso da Unidade.

    streamlit run app.py

O modelo de IA roda dentro desta aplicação: o gestor move um filtro,
o modelo recalcula e a recomendação se atualiza. Não há exportação
intermediária entre a inteligência e a interface.

Responsável: Pedro Henrique Macêdo (Desenvolvedor e Qualidade)
Interface e navegação: Beatriz Amaral (UI/UX)
"""

import streamlit as st

from src.viz.tema import PALETA, SEMAFORO, aplicar_tema

st.set_page_config(
    page_title="Vital Data Lab — Pulso da Unidade",
    page_icon="🫀",
    layout="wide",
)

aplicar_tema()

# --- identidade visual da aplicação ---
st.markdown(f"""
<style>
  .stApp {{ background-color: {PALETA['bege']}; }}
  h1, h2, h3 {{ color: #3B1E17; font-family: 'Montserrat', sans-serif; }}
  p, li, label {{ color: {PALETA['marrom']}; }}
</style>
""", unsafe_allow_html=True)

st.title("Pulso da Unidade")
st.caption("o pulso do Recife em decisões que salvam")

# --- filtros ---
with st.sidebar:
    st.header("Filtros")
    st.selectbox("Distrito Sanitário", ["Todos"])
    st.selectbox("Unidade", ["Todas"])
    st.selectbox("Classificação", ["Todas"] + list(SEMAFORO.keys()))

# --- telas previstas ---
aba1, aba2, aba3 = st.tabs(["Visão geral", "Unidade", "Recomendações"])

with aba1:
    st.subheader("Visão geral do município")
    st.info("Em construção — previsão: novembro de 2026.")

with aba2:
    st.subheader("Detalhe da unidade")
    st.info("Em construção — previsão: novembro de 2026.")

with aba3:
    st.subheader("Recomendações prioritárias")
    st.info("Em construção — previsão: novembro de 2026.")
