"""
Vital Data Lab — dashboard do Pulso da Unidade.

    python src/etl/pipeline.py      # gera os dados
    streamlit run app.py            # sobe o painel

Três telas, três perguntas do gestor:
    Visão geral    -> onde ir primeiro
    Unidade        -> por que está assim
    Recomendações  -> o que fazer agora

Ideia que não responde a uma dessas três perguntas não entra no MVP.

Responsável: Pedro Henrique Macêdo · interface: Beatriz Amaral
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.indice.pulso import FAIXAS
from src.modelos import classificador
from src.viz.tema import ESCALA_PULSO, PALETA, SEMAFORO, aplicar_tema

PULSO = Path("data/processed/pulso_por_unidade.csv")
RECOMENDACOES = Path("data/processed/recomendacoes.csv")

st.set_page_config(page_title="Vital Data Lab — Pulso da Unidade",
                   page_icon="🫀", layout="wide")
aplicar_tema()

st.markdown(f"""
<style>
  .stApp {{ background-color: {PALETA['bege']}; }}
  h1, h2, h3 {{ color: #3B1E17; font-family: 'Montserrat', sans-serif; letter-spacing:-.01em; }}
  p, li, label {{ color: {PALETA['marrom']}; }}
  [data-testid="stMetricValue"] {{ color: {PALETA['marrom']}; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def carregar():
    if not PULSO.exists():
        return None, None
    base = pd.read_csv(PULSO)
    recs = pd.read_csv(RECOMENDACOES) if RECOMENDACOES.exists() else pd.DataFrame()
    return base, recs


@st.cache_resource
def treinar_modelo(base: pd.DataFrame):
    X, y = classificador.preparar(base)
    return classificador.treinar(X, y), classificador.importancia_variaveis(
        classificador.treinar(X, y))


base, recs = carregar()

st.title("Pulso da Unidade")
st.caption("o pulso do Recife em decisões que salvam")

if base is None:
    st.error("Base não encontrada. Rode antes:  `python src/etl/pipeline.py`")
    st.stop()

if "origem_dado" in base.columns and base["origem_dado"].iloc[0] == "SIMULADO":
    st.warning("⚠️  **Dados simulados.** Esta versão roda sobre uma base sintética "
               "gerada para desenvolvimento. Nenhum número nesta tela representa "
               "o desempenho real da rede de saúde do Recife.")

# ---------------------------------------------------------------- filtros
with st.sidebar:
    st.header("Filtros")
    distritos = ["Todos"] + sorted(base["distrito"].unique())
    distrito = st.selectbox("Distrito Sanitário", distritos)
    faixas = st.multiselect("Classificação", list(FAIXAS), default=list(FAIXAS))
    st.divider()
    st.caption(f"{len(base)} equipes na base")

filtrada = base.copy()
if distrito != "Todos":
    filtrada = filtrada[filtrada["distrito"] == distrito]
if faixas:
    filtrada = filtrada[filtrada["classificacao"].isin(faixas)]

aba1, aba2, aba3 = st.tabs(["Visão geral", "Unidade", "Recomendações"])

# ------------------------------------------------------------- tela 1
with aba1:
    st.subheader("Onde ir primeiro")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Equipes", len(filtrada))
    c2.metric("Pulso mediano", f"{filtrada['pulso'].median():.0f}")
    c3.metric("Em situação crítica",
              int((filtrada["classificacao"] == "Crítico").sum()))
    c4.metric("Em excelência",
              int((filtrada["classificacao"] == "Excelência").sum()))

    esq, dir_ = st.columns([1, 1])

    with esq:
        contagem = (filtrada["classificacao"].value_counts()
                    .reindex(list(FAIXAS)).fillna(0).reset_index())
        contagem.columns = ["classificacao", "equipes"]
        fig = px.bar(contagem, x="classificacao", y="equipes",
                     color="classificacao", color_discrete_map=SEMAFORO,
                     title="Distribuição das equipes por faixa")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="equipes")
        st.plotly_chart(fig, use_container_width=True)

    with dir_:
        fig = px.histogram(filtrada, x="pulso", nbins=20,
                           title="Distribuição do índice",
                           color_discrete_sequence=[PALETA["ambar"]])
        fig.update_layout(xaxis_title="Pulso da Unidade", yaxis_title="equipes")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Fila de prioridade")
    st.caption("As equipes com menor índice, já ordenadas. É por aqui que o gestor começa.")
    fila = (filtrada.nsmallest(15, "pulso")
            [["unidade", "distrito", "pulso", "classificacao",
              "desempenho_bruto", "ajuste_contexto"]]
            .rename(columns={"unidade": "Unidade", "distrito": "Distrito",
                             "pulso": "Pulso", "classificacao": "Faixa",
                             "desempenho_bruto": "Bruto",
                             "ajuste_contexto": "Ajuste"}))
    st.dataframe(fila, use_container_width=True, hide_index=True)

# ------------------------------------------------------------- tela 2
with aba2:
    st.subheader("Por que esta unidade está assim")

    unidade = st.selectbox("Unidade", sorted(filtrada["unidade"].unique())
                           if len(filtrada) else sorted(base["unidade"].unique()))
    linha = base[base["unidade"] == unidade].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Pulso da Unidade", f"{linha['pulso']:.0f}")
    c2.metric("Classificação", linha["classificacao"])
    c3.metric("Ajuste por contexto", f"{linha['ajuste_contexto']:+.0f}",
              help="Correção aplicada pelo contexto socioterritorial do bairro.")

    esq, dir_ = st.columns([1.2, 1])

    with esq:
        indicadores = ["cobertura_pre_natal", "vacinacao_infantil",
                       "hipertensos_acompanhados", "diabeticos_acompanhados",
                       "saude_bucal_atendimentos", "citopatologico_coletado"]
        rotulos = [i.replace("_", " ").capitalize() for i in indicadores]
        grupo = base[base["grupo"] == linha["grupo"]]

        fig = go.Figure()
        fig.add_trace(go.Bar(y=rotulos, x=[linha[i] for i in indicadores],
                             name="Esta unidade", orientation="h",
                             marker_color=PALETA["terracota"]))
        fig.add_trace(go.Bar(y=rotulos, x=[grupo[i].median() for i in indicadores],
                             name="Mediana do grupo semelhante", orientation="h",
                             marker_color=PALETA["mostarda"], opacity=.55))
        fig.update_layout(title="Comparação com unidades de contexto semelhante",
                          barmode="group", xaxis_title="cobertura (%)",
                          legend=dict(orientation="h", y=-.18))
        st.plotly_chart(fig, use_container_width=True)

    with dir_:
        st.markdown("##### O que mais pesou na classificação")
        st.caption("Variáveis com maior importância no modelo, e o valor desta unidade.")
        modelo, importancias = treinar_modelo(base)
        topo = importancias.head(5)
        tabela = pd.DataFrame({
            "Variável": [n.replace("_", " ").capitalize() for n in topo.index],
            "Peso no modelo": (topo.values * 100).round(1),
            "Valor da unidade": [round(float(linha[n]), 1) for n in topo.index],
        })
        st.dataframe(tabela, use_container_width=True, hide_index=True)

        st.markdown("##### Contexto do território")
        st.write(f"IDHM do bairro: **{linha['idhm_bairro']:.2f}**")
        st.write(f"Saneamento: **{linha['saneamento_pct']:.0f}%**")
        st.write(f"População adscrita: **{int(linha['populacao_adscrita']):,}**".replace(",", "."))

# ------------------------------------------------------------- tela 3
with aba3:
    st.subheader("O que fazer agora")

    if recs.empty:
        st.info("Nenhuma recomendação gerada. Rode o pipeline novamente.")
    else:
        recomendacoes = recs.copy()
        if distrito != "Todos":
            recomendacoes = recomendacoes[recomendacoes["distrito"] == distrito]

        prioridade = st.radio("Prioridade", ["Todas", "alta", "média", "baixa"],
                              horizontal=True)
        if prioridade != "Todas":
            recomendacoes = recomendacoes[recomendacoes["prioridade"] == prioridade]

        st.caption(f"{len(recomendacoes)} recomendações · ordenadas por prioridade")

        cores = {"alta": PALETA["terracota"], "média": PALETA["ambar"],
                 "baixa": PALETA["verde"]}
        for _, r in recomendacoes.head(30).iterrows():
            cor = cores.get(r["prioridade"], PALETA["marrom"])
            st.markdown(
                f"""<div style="border-left:4px solid {cor};background:#F7F3EC;
                     border-radius:0 8px 8px 0;padding:14px 16px;margin-bottom:10px">
                  <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
                       color:{cor};font-weight:600">prioridade {r['prioridade']}</div>
                  <div style="font-weight:700;color:#3B1E17;margin:3px 0 4px">
                       {r['unidade']} · {r['distrito']}</div>
                  <div style="color:#7A3B2E;font-size:14px;margin-bottom:5px">{r['acao']}</div>
                  <div style="color:#8A6A58;font-size:12.5px">{r['motivo']}</div>
                </div>""", unsafe_allow_html=True)

st.divider()
st.caption("Vital Data Lab · Projeto 5 — Gestão de TI · CESAR School · 2026.2 · "
           "Parceiro do desafio: SEAB / NIIMA — Secretaria de Saúde do Recife")
