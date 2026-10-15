"""Pulso da Unidade v2: motor de sugestões de ações sobre os três eixos do Recife Monitora."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pulso import estilo
from pulso.dados import DISTRITOS, gerar_base
from pulso.eixos import ACOES, CICLOS, EIXOS, ITENS, ITENS_DO_EIXO, PROXIMO_CICLO, pontuacoes
from pulso.estilo import CINZA, CORES_EIXO, TINTA, VERDE, VERMELHO
from pulso.motor import (atribuir_grupos, confianca, efeitos, efeitos_medios, evidencia, projetar,
                         sugestoes, transicoes, treinar)

st.set_page_config(page_title="Pulso da Unidade · Vital Data Lab", page_icon="🩺", layout="wide")
estilo.aplicar()

TODOS = "Todos os distritos"
FOCOS = {
    "Os três eixos": {"e1": 1.0, "e2": 1.0, "e3": 1.0},
    "Eixo 1 · Profissionais": {"e1": 1.0, "e2": 0.25, "e3": 0.25},
    "Eixo 2 · Cidadãos": {"e1": 0.25, "e2": 1.0, "e3": 0.25},
    "Eixo 3 · Desempenho": {"e1": 0.25, "e2": 0.25, "e3": 1.0},
}
N_SUGESTOES = 5


# ----------------------------------------------------------------------------- dados e motor

@st.cache_resource(show_spinner="Preparando os dados e treinando o motor de sugestões…")
def carregar():
    equipes, painel, pactos = gerar_base()
    equipes["grupo"] = atribuir_grupos(equipes)
    trans = transicoes(painel, equipes, pactos)
    motor = treinar(trans)
    base = painel.merge(equipes, on="equipe", how="left")
    base = pd.concat([base, pontuacoes(base)], axis=1)
    return base, pactos, trans, motor


@st.cache_data(show_spinner="Calculando as sugestões do ciclo…")
def sugestoes_do_ciclo(ciclo: str) -> pd.DataFrame:
    base, _, _, motor = carregar()
    return sugestoes(motor, base[base["ciclo"] == ciclo].reset_index(drop=True))


def ranquear(sug: pd.DataFrame, pesos: dict, descartadas: set) -> pd.DataFrame:
    """Ordena as ações de cada equipe pelo ganho esperado nos eixos, com o peso do foco escolhido."""
    s = sug.assign(
        prioridade=sum(sug[f"ganho_{e}"] * w for e, w in pesos.items()),
        ganho_total=sug[[f"ganho_{e}" for e in EIXOS]].sum(axis=1),
    )
    if descartadas:
        s = s[[(eq, a) not in descartadas for eq, a in zip(s["equipe"], s["acao"])]]
    s = s[s["prioridade"] > 0.05].sort_values(["equipe", "prioridade"], ascending=[True, False])
    return s.assign(ordem=s.groupby("equipe").cumcount() + 1)


# ----------------------------------------------------------------------------- pacto e retorno das equipes

st.session_state.setdefault("pacto", {})
st.session_state.setdefault("descartadas", {})


def chave(equipe: str, ciclo: str) -> str:
    return f"{equipe}|{ciclo}"


def alternar_pacto(k: str, acao: str) -> None:
    lista = st.session_state["pacto"].setdefault(k, [])
    if acao in lista:
        lista.remove(acao)
    else:
        lista.append(acao)


def descartar(k: str, acao: str) -> None:
    st.session_state["descartadas"].setdefault(k, []).append(acao)
    if acao in st.session_state["pacto"].get(k, []):
        st.session_state["pacto"][k].remove(acao)


def restaurar_descartes(k: str) -> None:
    st.session_state["descartadas"][k] = []


def definir_pacto(k: str, acoes: list) -> None:
    st.session_state["pacto"][k] = list(acoes)


def descartadas_do_ciclo(ciclo: str) -> set:
    return {(k.split("|")[0], a) for k, acoes in st.session_state["descartadas"].items()
            if k.endswith(f"|{ciclo}") for a in acoes}


# ----------------------------------------------------------------------------- formatação

def num(v: float, casas: int = 1) -> str:
    return f"{v:,.{casas}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pp(v: float) -> str:
    if v is None or np.isnan(v):
        return "—"
    return f"{'+' if v >= 0 else '−'}{num(abs(v))} pp"


def html(conteudo: str) -> None:
    # Em linha única: linhas em branco seguidas de indentação virariam bloco de código no Markdown.
    st.markdown(" ".join(linha.strip() for linha in conteudo.splitlines() if linha.strip()), unsafe_allow_html=True)


def grafico(fig: go.Figure, altura: int | None = None) -> None:
    if altura:
        fig.update_layout(height=altura)
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False}, width="stretch")


def variacao(atual: float, anterior: float | None) -> str:
    if anterior is None:
        return ""
    d = atual - anterior
    classe = "pulso-sobe" if d >= 0 else "pulso-desce"
    return f"<span class='{classe}'>{'▲' if d >= 0 else '▼'} {num(abs(d))}</span>"


def heatmap_diferenca(tabela: pd.DataFrame, altura: int, casas: int = 0) -> None:
    """Mapa de calor divergente (vermelho abaixo de zero, verde acima) com os itens dos eixos nas colunas."""
    texto = [[num(v, casas) if abs(v) >= 0.5 else "" for v in linha] for linha in tabela.to_numpy()]
    limite = max(5.0, float(np.nanmax(np.abs(tabela.to_numpy()))))
    rotulos = [f"<span style='color:{CORES_EIXO[ITENS[i]['eixo']]}'>●</span> {ITENS[i]['nome']}" for i in tabela.columns]
    fig = go.Figure(go.Heatmap(
        z=tabela.to_numpy(), x=rotulos, y=tabela.index,
        text=texto, texttemplate="%{text}", textfont={"size": 11},
        colorscale=[[0, VERMELHO], [0.5, "#FFFFFF"], [1, VERDE]], zmin=-limite, zmax=limite,
        hovertemplate="%{y} · %{x}: %{z:+.1f} pp<extra></extra>", showscale=False, xgap=2, ygap=2,
    ))
    fig.update_layout(xaxis=dict(side="top", tickangle=-35), yaxis=dict(autorange="reversed"),
                      margin=dict(l=10, r=10, t=120, b=10))
    grafico(fig, altura)
    st.caption(" · ".join(f"<span style='color:{CORES_EIXO[e]}'>●</span> {EIXOS[e]['titulo']}" for e in EIXOS),
               unsafe_allow_html=True)


# ----------------------------------------------------------------------------- telas

def tela_visao(escopo, escopo_anterior, historico, rank_escopo, base_ciclo, recorte, distrito):
    c = st.columns(4)
    c[0].metric("Equipes avaliadas", len(escopo))
    for col, e in zip(c[1:], EIXOS):
        delta = None
        if escopo_anterior is not None:
            delta = f"{escopo[e].mean() - escopo_anterior[e].mean():+.1f}".replace(".", ",")
        col.metric(EIXOS[e]["titulo"], num(escopo[e].mean()), delta)

    esq, dir_ = st.columns(2)
    with esq:
        if distrito == TODOS:
            st.markdown("#### Eixos por distrito")
            g = escopo.groupby("distrito")[list(EIXOS)].mean().reindex(list(DISTRITOS))
            fig = go.Figure([go.Bar(x=g.index, y=g[e], name=EIXOS[e]["titulo"], marker_color=CORES_EIXO[e],
                                    hovertemplate="%{x}: %{y:.1f}<extra>" + EIXOS[e]["curto"] + "</extra>")
                             for e in EIXOS])
            fig.update_layout(barmode="group", yaxis_range=[0, 100], bargap=0.25)
            grafico(fig, 360)
        else:
            st.markdown(f"#### Eixos por equipe · {distrito}")
            g = escopo.set_index("nome")[list(EIXOS)]
            diferenca = g - base_ciclo[list(EIXOS)].mean()
            ordem = diferenca.mean(axis=1).sort_values().index
            g, diferenca = g.loc[ordem], diferenca.loc[ordem]
            limite = max(5.0, float(np.abs(diferenca.to_numpy()).max()))
            fig = go.Figure(go.Heatmap(
                z=diferenca.to_numpy(), x=[EIXOS[e]["titulo"] for e in EIXOS], y=g.index,
                text=[[num(v, 0) for v in linha] for linha in g.to_numpy()], texttemplate="%{text}",
                customdata=g.to_numpy(), colorscale=[[0, VERMELHO], [0.5, "#FFFFFF"], [1, VERDE]],
                zmin=-limite, zmax=limite, showscale=False, xgap=3, ygap=3,
                hovertemplate="%{y} · %{x}: %{customdata:.1f} (%{z:+.1f} vs. Recife)<extra></extra>",
            ))
            fig.update_layout(xaxis=dict(side="top"), yaxis=dict(autorange="reversed"),
                              margin=dict(l=10, r=10, t=40, b=10))
            grafico(fig, max(360, 24 * len(g) + 60))
            st.caption("Cor: acima (verde) ou abaixo (vermelho) da média de Recife no eixo. "
                       "As equipes mais abaixo aparecem primeiro.")
    with dir_:
        st.markdown("#### Evolução dos eixos")
        m = historico.groupby("ciclo")[list(EIXOS)].mean().reindex(CICLOS)
        fig = go.Figure([go.Scatter(x=m.index, y=m[e], mode="lines+markers", name=EIXOS[e]["titulo"],
                                    line=dict(color=CORES_EIXO[e], width=3),
                                    hovertemplate="%{x}: %{y:.1f}<extra>" + EIXOS[e]["curto"] + "</extra>")
                         for e in EIXOS])
        fig.update_layout(yaxis=dict(range=[0, 100], title="Pontuação média"))
        grafico(fig, 360)

    st.markdown("#### Onde estão os pontos fracos")
    st.caption("Diferença de cada item em relação à mediana de Recife no ciclo, em pontos percentuais. "
               "Vermelho fica abaixo, verde fica acima.")
    linha_por = "distrito" if distrito == TODOS else "nome"
    tabela = escopo.groupby(linha_por)[list(ITENS)].mean() - base_ciclo[list(ITENS)].median()
    if distrito == TODOS:
        tabela = tabela.reindex(list(DISTRITOS))
    heatmap_diferenca(tabela, max(380, 26 * len(tabela) + 140))

    st.markdown(f"#### Ações com mais retorno · {recorte}")
    top3 = rank_escopo[rank_escopo["ordem"] <= 3]
    if top3.empty:
        st.info("Nenhuma sugestão para este recorte.")
    else:
        agg = (top3.groupby("acao").agg(equipes=("equipe", "nunique"), ganho=("ganho_total", "sum"))
               .sort_values(["equipes", "ganho"]))
        esq, dir_ = st.columns([1.15, 1])
        with esq:
            fig = go.Figure(go.Bar(
                y=[ACOES[a]["titulo"] for a in agg.index], x=agg["equipes"], orientation="h", marker_color=estilo.VINHO,
                text=agg["equipes"], textposition="outside", cliponaxis=False, customdata=agg["ganho"],
                hovertemplate="%{y}<br>Entre as 3 primeiras de %{x} equipes · +%{customdata:.0f} pp somados<extra></extra>",
            ))
            fig.update_layout(xaxis=dict(title="Nº de equipes (ação entre as 3 primeiras)",
                                         range=[0, agg["equipes"].max() * 1.15]))
            grafico(fig, max(300, 30 * len(agg) + 80))
        with dir_:
            for a in agg.index[::-1][:3]:
                n_equipes, ganho = int(agg.at[a, "equipes"]), float(agg.at[a, "ganho"])
                html(f"""<div class='pulso-card'>
                    <div class='pulso-titulo'>{ACOES[a]['titulo']}</div>
                    <div class='pulso-muted'>{ACOES[a]['detalhe']}</div>
                    <div class='pulso-sobe' style='margin:.4rem 0'>Entre as 3 primeiras de {n_equipes} equipes · {pp(ganho)} somados nos eixos</div>
                    <span class='pulso-tag'>{ACOES[a]['responsavel']}</span></div>""")

    st.markdown("#### Equipes com maior potencial de avanço")
    st.caption("Ganho esperado nos três eixos se a equipe fizer as três primeiras ações sugeridas.")
    potencial = top3.groupby("equipe")["ganho_total"].sum()
    primeira = rank_escopo[rank_escopo["ordem"] == 1].set_index("equipe")["acao"]
    topo = escopo.assign(potencial=escopo["equipe"].map(potencial)).nlargest(12, "potencial")
    st.dataframe(pd.DataFrame({
        "Equipe": topo["nome"], "Distrito": topo["distrito"],
        **{EIXOS[e]["curto"]: topo[e] for e in EIXOS},
        "Primeira sugestão": topo["equipe"].map(primeira).map(lambda a: ACOES[a]["titulo"] if isinstance(a, str) else ""),
        "Ganho": topo["potencial"],
    }), hide_index=True, width="stretch", height=35 * (len(topo) + 1) + 3, column_config={
        **{EIXOS[e]["curto"]: st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f", width="small")
           for e in EIXOS},
        "Distrito": st.column_config.TextColumn(width="small"),
        "Ganho": st.column_config.NumberColumn(format="+%.1f pp", width="small",
                                               help="Ganho esperado nos três eixos com as três primeiras sugestões"),
    })

    colunas = ["equipe", "nome", "cnes", "unidade", "distrito", "grupo", "ciclo"] + list(EIXOS) + list(ITENS)
    st.download_button("Baixar dados do recorte (CSV)",
                       escopo[colunas].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                       file_name=f"pulso_{recorte.replace(' ', '_')}.csv", mime="text/csv")


def cartao_eixo(e, linha, anterior, pares):
    itens = ""
    for i in ITENS_DO_EIXO[e]:
        v, ref = linha[i], pares[i].median()
        fraco = v <= ref - 5
        meta = f" · meta {ITENS[i]['meta']}%" if "meta" in ITENS[i] else ""
        itens += (f"<div class='pulso-linha'><span>{'▼ ' if fraco else ''}{ITENS[i]['nome']}</span>"
                  f"<span><b class='{'pulso-desce' if fraco else ''}'>{num(v, 0)}%</b>"
                  f" <span class='pulso-muted'>· pares {num(ref, 0)}%{meta}</span></span></div>")
    html(f"""<div class='pulso-card' style='border-top:4px solid {CORES_EIXO[e]}'>
        <h4>{EIXOS[e]['titulo']}</h4><div class='pulso-muted'>{EIXOS[e]['fonte']}</div>
        <div style='display:flex;align-items:baseline;gap:12px;margin:.6rem 0 .4rem'>
        <span class='pulso-grande' style='color:{CORES_EIXO[e]}'>{num(linha[e])}</span>
        {variacao(linha[e], anterior[e] if anterior is not None else None)}
        <span class='pulso-muted'>pares {num(pares[e].median())}</span></div>{itens}</div>""")


def cartao_sugestao(posicao, r, linha, trans, motor, k, no_pacto, ja_pactuada, ciclo):
    acao = ACOES[r.acao]
    with st.container(border=True, key=f"cartao_{r.acao}"):
        c0, c1, c2 = st.columns([0.05, 0.53, 0.42], gap="medium")
        c0.markdown(f"<div class='pulso-num'>{posicao}</div>", unsafe_allow_html=True)
        with c1:
            tags = f"<span class='pulso-tag'>{acao['responsavel']}</span>"
            if ja_pactuada:
                tags += f"<span class='pulso-tag'>Já estava no pacto de {ciclo}</span>"
            html(f"<div class='pulso-titulo'>{acao['titulo']}</div><div class='pulso-muted'>{acao['detalhe']}</div>"
                 f"<div style='margin-top:.5rem'>{tags}</div>")
            if r.itens:
                item = r.itens[0][0]
                ev = evidencia(trans, r.acao, item, linha[item])
                if ev["n_com"]:
                    st.caption(f"**Por quê:** no histórico, equipes com {ITENS[item]['nome'].lower()} perto de "
                               f"{num(linha[item], 0)}% que fizeram essa ação variaram {pp(ev['media_com'])} no ciclo "
                               f"seguinte ({ev['n_com']} casos). As que não fizeram variaram {pp(ev['media_sem'])}.")
        with c2:
            linhas = "".join(
                f"<div class='pulso-linha'><span>{ITENS[i]['nome']}</span><span>{num(linha[i], 0)}% → "
                f"<b>{num(min(linha[i] + d, 100), 0)}%</b> <span class='pulso-sobe'>{pp(d)}</span></span></div>"
                for i, d in r.itens[:3])
            chips = "".join(
                f"<span class='pulso-chip' style='background:{CORES_EIXO[e]}'>{EIXOS[e]['curto']} {pp(getattr(r, f'ganho_{e}'))}</span>"
                for e in EIXOS if getattr(r, f"ganho_{e}") >= 0.05)
            n = int(motor.aplicacoes[r.acao])
            html(f"<div class='pulso-muted'>Efeito esperado no ciclo seguinte</div>{linhas}"
                 f"<div style='margin-top:.6rem'>{chips}</div>"
                 f"<div class='pulso-muted'>Confiança {confianca(n)} · usada {n} vezes no histórico de pactos</div>")
            b1, b2 = st.columns(2)
            b1.button("✓ No pacto" if no_pacto else "Incluir no pacto", key=f"pacto_{r.acao}",
                      type="secondary" if no_pacto else "primary", width="stretch",
                      help="Clique para tirar do pacto" if no_pacto else None,
                      on_click=alternar_pacto, args=(k, r.acao))
            b2.button("Não se aplica", key=f"descarta_{r.acao}", width="stretch",
                      help="Some das sugestões desta equipe e fica registrado como retorno para a IA",
                      on_click=descartar, args=(k, r.acao))


def tela_sugestoes(linha, base_ciclo, anterior, rank_eq, trans, motor, k, ja_pactuadas, ciclo, ciclo_seg, foco):
    pares = base_ciclo[(base_ciclo["grupo"] == linha["grupo"]) & (base_ciclo["equipe"] != linha["equipe"])]
    html(f"<h3 style='margin-bottom:.2rem'>{linha['nome']}</h3>"
         f"<span class='pulso-tag'>{linha['distrito']}</span><span class='pulso-tag'>{linha['bairro']}</span>"
         f"<span class='pulso-tag'>CNES {linha['cnes']}</span><span class='pulso-tag'>Território {linha['grupo']}</span>"
         f"<span class='pulso-tag'>{linha['respostas_eixo2']} respostas na pesquisa do ciclo</span>")
    st.caption(f"Resultado do Recife Monitora no ciclo {ciclo}. \"Pares\" são as equipes com território parecido; "
               "▼ marca itens 5 pp ou mais abaixo delas.")
    for col, e in zip(st.columns(3), EIXOS):
        with col:
            cartao_eixo(e, linha, anterior, pares)

    st.markdown(f"#### Ações sugeridas para o pacto de {ciclo_seg}")
    st.caption(f"Ordenadas pelo ganho esperado nos eixos, com foco em: **{foco.lower()}**. "
               "O efeito de cada ação foi aprendido com o histórico de pactos de todas as equipes.")
    top = rank_eq.head(N_SUGESTOES)
    if top.empty:
        st.success("O motor não encontrou ações com ganho relevante para esta equipe.")
        return
    d = top.iloc[::-1]
    fig = go.Figure([go.Bar(y=[ACOES[a]["titulo"] for a in d["acao"]], x=d[f"ganho_{e}"].clip(lower=0),
                            name=EIXOS[e]["titulo"], orientation="h", marker_color=CORES_EIXO[e],
                            hovertemplate="%{y}<br>+%{x:.1f} pp<extra>" + EIXOS[e]["curto"] + "</extra>")
                     for e in EIXOS])
    fig.update_layout(barmode="stack", xaxis_title="Ganho esperado nos eixos (pp)", legend_traceorder="normal",
                      legend_y=1.12, margin=dict(l=10, r=10, t=60, b=10))
    grafico(fig, 300)

    no_pacto = st.session_state["pacto"].get(k, [])
    for posicao, r in enumerate(top.itertuples(), start=1):
        cartao_sugestao(posicao, r, linha, trans, motor, k, r.acao in no_pacto, r.acao in ja_pactuadas, ciclo)

    descartadas = st.session_state["descartadas"].get(k, [])
    if descartadas:
        c1, c2 = st.columns([3, 1])
        c1.caption(f"{len(descartadas)} sugestão(ões) marcada(s) como \"não se aplica\": "
                   + ", ".join(ACOES[a]["titulo"] for a in descartadas) + ".")
        c2.button("Mostrar de novo", on_click=restaurar_descartes, args=(k,), width="stretch")


def tela_pacto(linha, sug_eq, rank_eq, motor, k, ciclo_seg):
    st.markdown(f"#### Pacto de {ciclo_seg} · {linha['nome']}")
    acoes = st.session_state["pacto"].get(k, [])
    if not acoes:
        st.info("Nenhuma ação no pacto ainda. Inclua ações na aba de sugestões ou comece pelas três primeiras.")
        st.button("Começar com as 3 primeiras sugestões", type="primary",
                  on_click=definir_pacto, args=(k, rank_eq.head(3)["acao"].tolist()))
        return

    estado = pd.DataFrame([linha]).reset_index(drop=True)
    estado[list(ITENS) + ["cobertura_acs"]] = estado[list(ITENS) + ["cobertura_acs"]].astype(float)
    ef = efeitos(motor, estado)[0]
    delta = ef[[list(ACOES).index(a) for a in acoes]].sum(axis=0)
    atual = pontuacoes(estado).iloc[0]
    projetado = projetar(estado, delta[None, :]).iloc[0]

    ganhos = sug_eq.set_index("acao")
    st.dataframe(pd.DataFrame({
        "Ação": [ACOES[a]["titulo"] for a in acoes],
        "Responsável": [ACOES[a]["responsavel"] for a in acoes],
        "Ganho esperado nos eixos": [
            " · ".join(f"{EIXOS[e]['curto']} {pp(ganhos.at[a, f'ganho_{e}'])}"
                       for e in EIXOS if abs(ganhos.at[a, f"ganho_{e}"]) >= 0.05)
            for a in acoes],
    }), hide_index=True, width="stretch")
    st.button("Limpar pacto", on_click=definir_pacto, args=(k, []))

    esq, dir_ = st.columns([1.1, 1], gap="large")
    with esq:
        mudancas = [(i, linha[i], min(linha[i] + d, 100) - linha[i]) for i, d in zip(ITENS, delta) if d >= 0.5]
        if mudancas:
            st.markdown("**Itens que devem subir**")
            st.dataframe(pd.DataFrame({
                "Item": [ITENS[i]["nome"] for i, _, _ in mudancas],
                "Eixo": [EIXOS[ITENS[i]["eixo"]]["curto"] for i, _, _ in mudancas],
                "Hoje": [f"{num(v)}%" for _, v, _ in mudancas],
                "Esperado": [f"{num(v + d)}%" for _, v, d in mudancas],
                "Variação": [pp(d) for _, _, d in mudancas],
            }), hide_index=True, width="stretch", height=35 * (len(mudancas) + 1) + 3)
    with dir_:
        fig = go.Figure([
            go.Bar(x=[EIXOS[e]["titulo"] for e in EIXOS], y=[atual[e] for e in EIXOS], name=f"Hoje", marker_color="#CBBFAF",
                   text=[num(atual[e]) for e in EIXOS], textposition="outside"),
            go.Bar(x=[EIXOS[e]["titulo"] for e in EIXOS], y=[projetado[e] for e in EIXOS], name=f"Esperado em {ciclo_seg}",
                   marker_color=[CORES_EIXO[e] for e in EIXOS], text=[num(projetado[e]) for e in EIXOS], textposition="outside"),
        ])
        fig.update_layout(barmode="group", yaxis_range=[0, 105], bargap=0.3)
        grafico(fig, 340)
        st.caption("Os efeitos das ações são somados. Ações com o mesmo alvo podem render um pouco menos juntas.")

    html(f"""<div class='pulso-pivo' style='margin-top:1rem'><b>Como a IA aprende com este pacto.</b>
        A equipe executa as ações durante {ciclo_seg}. No fim do ciclo, o Recife Monitora devolve os três eixos.
        O motor compara o que era esperado com o que aconteceu e é treinado de novo: as ações que renderam mais
        ganham prioridade nas próximas sugestões, e as marcadas como "não se aplica" deixam de aparecer para quem respondeu.</div>""")
    st.download_button("Baixar o pacto (CSV)",
                       pd.DataFrame({"equipe": linha["nome"], "ciclo": ciclo_seg,
                                     "acao": [ACOES[a]["titulo"] for a in acoes],
                                     "responsavel": [ACOES[a]["responsavel"] for a in acoes]})
                       .to_csv(index=False, sep=";").encode("utf-8-sig"),
                       file_name=f"pacto_{linha['equipe']}_{ciclo_seg.replace(' ', '_')}.csv", mime="text/csv")


def tela_ia(motor, estado):
    st.markdown("#### O que a IA aprendeu com o histórico")
    m = st.columns(4)
    m[0].metric("Ciclos de equipe analisados", f"{motor.n_transicoes:,}".replace(",", "."))
    m[1].metric("Ações no catálogo", len(ACOES))
    m[2].metric("Erro da previsão com a IA", f"{num(motor.mae_ia, 2)} pp",
                f"{num((motor.mae_ia / motor.mae_sem_acoes - 1) * 100, 0)}% vs. sem ações", delta_color="inverse",
                help=f"Sem considerar as ações do pacto, o erro seria de {num(motor.mae_sem_acoes, 2)} pp.")
    m[3].metric("Ciclos de histórico", len(CICLOS))

    st.markdown("**Quanto cada ação mudou cada item, em média (pp por ciclo)**")
    st.caption("Aprendido a partir dos pactos que as equipes fizeram e do resultado no ciclo seguinte, descontando "
               "o ponto de partida e o território. Células vazias: efeito menor que 0,5 pp.")
    em = efeitos_medios(motor, estado)
    em.index = [ACOES[a]["titulo"] for a in em.index]
    heatmap_diferenca(em, 640, casas=1)

    esq, dir_ = st.columns(2, gap="large")
    with esq:
        st.markdown("**A IA melhora a cada ciclo**")
        fig = go.Figure(go.Scatter(x=motor.curva["ciclos"], y=motor.curva["mae"], mode="lines+markers",
                                   line=dict(color=estilo.VINHO, width=3), marker=dict(size=10),
                                   hovertemplate="%{x} ciclos de histórico: erro de %{y:.2f} pp<extra></extra>"))
        fig.update_layout(xaxis=dict(title="Ciclos de histórico usados no treino", dtick=1),
                          yaxis_title="Erro médio da previsão (pp)")
        grafico(fig, 300)
        st.caption(f"Erro ao prever a variação dos itens no ciclo mais recente ({CICLOS[-1]}), "
                   "treinando com cada vez mais ciclos.")
    with dir_:
        st.markdown("**Como o motor funciona**")
        passos = [
            ("1. Junta os dados", "os três eixos de cada equipe, ciclo a ciclo, e o pacto que ela assumiu."),
            ("2. Aprende", "quanto cada ação mudou cada item no ciclo seguinte, considerando o ponto de partida e o território."),
            ("3. Sugere", "para cada equipe, as ações com maior ganho esperado nos eixos."),
            ("4. Reaprende", "com o resultado do pacto e com as sugestões marcadas como \"não se aplica\"."),
        ]
        html("<div class='pulso-card'>" + "".join(
            f"<div style='padding:6px 0;border-bottom:1px dashed #E4DCCF;font-size:.88rem'><b>{t}:</b> "
            f"<span class='pulso-muted'>{d}</span></div>" for t, d in passos) + "</div>")
        st.caption("Modelo: uma regressão regularizada (Ridge, scikit-learn) por item, com interações entre cada ação, "
                   "o espaço que o item tem para crescer e a cobertura de ACS.")

    st.markdown("#### O que mudou desde a primeira versão")
    html("""<div class='pulso-pivo'>Na <b>v1</b>, o protótipo criava uma régua própria: o Índice Pulso, de 0 a 100,
        com a classificação Crítico, Atenção ou Excelência. Na conversa com o Recife Monitora, ficou claro que a avaliação
        oficial continua sendo feita pelos <b>três eixos</b> e que o que agrega valor é a <b>recomendação de ações</b>.
        Na <b>v2</b>, o índice e as faixas saíram, os três eixos passaram a ser a entrada do sistema, e o produto virou
        um <b>motor de sugestões</b> que aprende com os pactos e os resultados de cada ciclo.</div>""")

    st.markdown("#### Fontes de dados, privacidade e acesso")
    a, b, c = st.columns(3)
    with a:
        html("""<div class='pulso-card'><h4>Fontes</h4><div class='pulso-muted'>
            <b>Recife Monitora</b>: os três eixos de cada equipe por ciclo e os pactos pela qualidade.<br>
            <b>SISAB / e-SUS APS</b>: indicadores do Eixo 3.<br><b>CNES</b>: cadastro de unidades e equipes.<br>
            <b>IBGE</b>: IDHM, saneamento e renda do bairro.</div></div>""")
    with b:
        html("""<div class='pulso-card'><h4>Privacidade</h4><div class='pulso-muted'>Só dados agregados por equipe, sem
            nenhum dado individual de paciente ou de profissional. As sugestões apoiam o pacto da equipe e não servem
            para ranquear ou punir.</div></div>""")
    with c:
        html("""<div class='pulso-card'><h4>Acesso por perfil</h4><div class='pulso-muted'><b>Gestão central</b>: o município.<br>
            <b>Gestão distrital</b>: o seu distrito.<br><b>Equipe</b>: a própria equipe.<br>
            Neste protótipo o perfil é escolhido na barra lateral; em produção viria do login.</div></div>""")
    html("<div class='pulso-aviso' style='margin-top:1rem'>Protótipo acadêmico com <b>dados sintéticos</b>: bairros e distritos "
         "dão a geografia, mas os eixos, os pactos e os efeitos das ações foram gerados e não representam nenhuma equipe real.</div>")


# ----------------------------------------------------------------------------- página

base, pactos, trans, motor = carregar()

with st.sidebar:
    html("<div class='pulso' style='font-weight:800;font-size:1.35rem;color:#7A3B2E'>Pulso da Unidade</div>"
         "<div class='pulso-muted' style='margin-bottom:1rem'>Vital Data Lab · CESAR School</div>")
    perfil = st.radio("Perfil de acesso", ["Gestão central", "Gestão distrital", "Equipe"],
                      help="Simula o controle de acesso: cada perfil enxerga só o seu recorte.")
    ciclo = st.selectbox("Ciclo do Recife Monitora", CICLOS[::-1],
                         help="Ciclos de quatro meses. As sugestões são para o pacto do ciclo seguinte.")
    distrito = st.selectbox("Distrito sanitário", ([TODOS] if perfil == "Gestão central" else []) + list(DISTRITOS))

    base_ciclo = base[base["ciclo"] == ciclo]
    escopo = base_ciclo if distrito == TODOS else base_ciclo[base_ciclo["distrito"] == distrito]
    pesos = FOCOS[st.session_state.get("foco", "Os três eixos")]
    rank = ranquear(sugestoes_do_ciclo(ciclo), pesos, descartadas_do_ciclo(ciclo))
    nomes = escopo.set_index("equipe")["nome"]
    opcoes = nomes.sort_values().index.tolist()
    if st.session_state.get("equipe") not in opcoes:
        potencial = rank[(rank["ordem"] <= 3) & rank["equipe"].isin(opcoes)].groupby("equipe")["prioridade"].sum()
        st.session_state["equipe"] = potencial.idxmax() if not potencial.empty else opcoes[0]
    equipe = st.selectbox("Sua equipe" if perfil == "Equipe" else "Equipe em foco", opcoes, key="equipe",
                          format_func=lambda e: nomes[e])
    foco = st.selectbox("Foco das sugestões", list(FOCOS), key="foco",
                        help="Dá mais peso ao eixo escolhido na ordem das sugestões.")
    html("<div class='pulso-aviso' style='margin-top:1.5rem'>Dados sintéticos para demonstração. "
         "Nenhum número representa uma equipe real.</div>")

i_ciclo = CICLOS.index(ciclo)
ciclo_anterior = CICLOS[i_ciclo - 1] if i_ciclo > 0 else None
ciclo_seguinte = CICLOS[i_ciclo + 1] if i_ciclo + 1 < len(CICLOS) else PROXIMO_CICLO
linha = base_ciclo[base_ciclo["equipe"] == equipe].iloc[0]
anterior = base[(base["equipe"] == equipe) & (base["ciclo"] == ciclo_anterior)]
anterior = anterior.iloc[0] if len(anterior) else None
k = chave(equipe, ciclo)
rank_eq = rank[rank["equipe"] == equipe]
sug_eq = sugestoes_do_ciclo(ciclo).query("equipe == @equipe")
ja_pactuadas = set(pactos[(pactos["equipe"] == equipe) & (pactos["ciclo"] == ciclo)]["acao"])

recorte = "Recife" if distrito == TODOS else distrito
subtitulo = linha["nome"] if perfil == "Equipe" else ("Recife, todos os distritos" if distrito == TODOS else distrito)
html(f"""<div class='pulso-hero'><div class='pulso-eyebrow'>Vital Data Lab · protótipo v2 · motor de sugestões</div>
    <h1>Pulso da Unidade</h1>
    <p>Sugestões de ações para o pacto de cada equipe, a partir dos três eixos do Recife Monitora ·
    <b>{subtitulo} · ciclo {ciclo}</b></p></div>""")

if perfil == "Equipe":
    aba_sug, aba_pacto, aba_ia = st.tabs(["Sugestões", "Pacto do ciclo", "O que a IA aprendeu"])
else:
    aba_visao, aba_sug, aba_pacto, aba_ia = st.tabs(["Visão do ciclo", "Sugestões da equipe", "Pacto do ciclo",
                                                     "O que a IA aprendeu"])
    with aba_visao:
        escopo_anterior = None
        if ciclo_anterior:
            base_ant = base[base["ciclo"] == ciclo_anterior]
            escopo_anterior = base_ant if distrito == TODOS else base_ant[base_ant["distrito"] == distrito]
        historico = base if distrito == TODOS else base[base["distrito"] == distrito]
        tela_visao(escopo, escopo_anterior, historico, rank[rank["equipe"].isin(escopo["equipe"])],
                   base_ciclo, recorte, distrito)

with aba_sug:
    tela_sugestoes(linha, base_ciclo, anterior, rank_eq, trans, motor, k, ja_pactuadas, ciclo, ciclo_seguinte, foco)
with aba_pacto:
    tela_pacto(linha, sug_eq, rank_eq, motor, k, ciclo_seguinte)
with aba_ia:
    tela_ia(motor, base_ciclo)
