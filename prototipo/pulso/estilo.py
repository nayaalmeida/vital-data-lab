"""Identidade visual do Vital Data Lab aplicada ao Streamlit e ao Plotly."""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

TINTA = "#1C1C1C"
VINHO = "#7A3B2E"
CORAL = "#D9543B"
AREIA = "#EDE6DA"
PAPEL = "#F7F3EC"
CINZA = "#8F857C"
GRADE = "#E4DCCF"
VERDE = "#2F7D5B"
VERMELHO = "#C2412D"

CORES_EIXO = {"e1": "#3F6C8C", "e2": CORAL, "e3": VINHO}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li, .stApp label,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"], .stTabs button p, .pulso {
  font-family: 'Montserrat', sans-serif;
}
.block-container { padding-top: 2rem; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs button p { font-weight: 600; }
[data-testid="stMetric"] {
  background: #FFFFFF; border: 1px solid #E4DCCF; border-radius: 14px; padding: 12px 16px;
}
[class*="st-key-cartao_"] { background: #FFFFFF; border-radius: 14px; }
.pulso-hero {
  background: #1C1C1C; color: #F9F9F9; border-radius: 16px; padding: 22px 26px; margin-bottom: 14px;
  background-image: radial-gradient(circle at 92% 15%, rgba(217,84,59,.55), transparent 42%);
}
.pulso-hero h1 { color: #F9F9F9; margin: 0; padding: 0; font-weight: 800; font-size: 2.1rem; }
.pulso-hero p { color: #EDE6DA; margin: .35rem 0 0; }
.pulso-eyebrow { text-transform: uppercase; letter-spacing: .14em; font-size: .7rem; color: #EDE6DA; opacity: .85; }
.pulso-card {
  background: #FFFFFF; border: 1px solid #E4DCCF; border-radius: 14px; padding: 16px 18px;
  height: 100%; margin-bottom: 10px;
}
.pulso-card h4 { margin: 0 0 .2rem; font-size: 1rem; font-weight: 700; }
.pulso-tag {
  display: inline-block; background: #EDE6DA; color: #7A3B2E; border-radius: 6px;
  padding: 2px 8px; font-size: .76rem; margin: 0 6px 6px 0; font-weight: 600;
}
.pulso-chip {
  display: inline-block; border-radius: 999px; padding: 2px 10px; font-size: .78rem;
  font-weight: 700; margin: 0 6px 6px 0; color: #FFFFFF;
}
.pulso-num { font-weight: 800; color: #D9543B; font-size: 1.6rem; line-height: 1; }
.pulso-titulo { font-weight: 700; font-size: 1.02rem; margin: 0 0 .25rem; }
.pulso-grande { font-weight: 800; font-size: 2.2rem; line-height: 1.1; }
.pulso-muted { color: #6B625A; font-size: .84rem; }
.pulso-sobe { color: #2F7D5B; font-weight: 700; font-size: .86rem; }
.pulso-desce { color: #C2412D; font-weight: 700; font-size: .86rem; }
.pulso-linha { display: flex; justify-content: space-between; gap: 8px; padding: 5px 0; border-bottom: 1px dashed #E4DCCF; font-size: .84rem; }
.pulso-linha:last-child { border-bottom: none; }
.pulso-aviso {
  background: #FFF6E5; border-left: 4px solid #D99A1E; padding: 8px 12px; border-radius: 6px; font-size: .8rem;
}
.pulso-pivo { background: #FFFFFF; border: 1px dashed #D9543B; border-radius: 14px; padding: 14px 18px; font-size: .88rem; }
</style>
"""


def aplicar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    pio.templates["pulso"] = go.layout.Template(layout=dict(
        font=dict(family="Montserrat, sans-serif", color=TINTA, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[VINHO, CORAL, "#3F6C8C", VERDE, "#D99A1E", "#6B5B95", CINZA, "#B5651D"],
        separators=",.",
        margin=dict(l=10, r=10, t=36, b=10),
        xaxis=dict(gridcolor=GRADE, zeroline=False, linecolor=GRADE),
        yaxis=dict(gridcolor=GRADE, zeroline=False, linecolor=GRADE),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hoverlabel=dict(font_family="Montserrat, sans-serif"),
    ))
    pio.templates.default = "plotly_white+pulso"
