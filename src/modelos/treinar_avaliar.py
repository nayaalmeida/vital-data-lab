"""
Vital Data Lab · SR2 · Avaliação de todos os modelos num comando só.

    python -m src.modelos.treinar_avaliar          (na raiz do repositório)

O que roda (~1 minuto em notebook comum, sem GPU, sem chave de API, sem internet):
  1. Random Forest — faixa de ação no próximo ciclo, na base comum (132 equipes).
  2. Motor de sugestões do app (Ridge) — erro com e sem as ações do pacto, e se ele
     reencontra os efeitos usados para gerar os dados do protótipo.
  3. K-Means de território do app — silhueta por k.
  4. Ponto fraco — com que frequência o item mais baixo se repete entre ciclos.
  5. Régua — quantas equipes-ciclo mudam de zona entre Manual e dicionário.

Tudo que sai daqui vai para reports/ e é a ÚNICA fonte dos números do deck e do site:
  reports/metricas_modelos.json   todos os números
  reports/matriz_confusao.csv     matriz do Random Forest no teste temporal
  reports/RELATORIO_MODELOS.md    leitura em português, pronta para o site/Drive
  reports/figuras/*.png           gráficos na paleta do projeto

BASE SINTÉTICA: nenhum número daqui representa a rede real do Recife.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "prototipo") not in sys.path:
    sys.path.insert(0, str(RAIZ / "prototipo"))

from src.indice.regua import ORDEM_FAIXAS, comparar_reguas, n_mudam_de_zona  # noqa: E402
from src.modelos import classificador, clusterizacao  # noqa: E402
from src.recomendacao.ponto_fraco import cobertura_regra, taxa_repeticao  # noqa: E402
from src.viz.tema import PALETA, SEMAFORO  # noqa: E402

BASE = RAIZ / "data" / "processed" / "base_analitica.csv"
SAIDA = RAIZ / "reports"
FIGURAS = SAIDA / "figuras"
AVISO = "Base sintética · não é dado real"

TINTA, TINTA_2, GRADE_COR, FUNDO = "#3B1E17", "#7A3B2E", "#E4D9C8", "#FBF7F0"
CINZA_BASE = "#C8BFB3"
INDICADORES = [f"IND{i:02d}" for i in range(1, 11)]


# ----------------------------------------------------------------------------- estilo dos gráficos

def _estilo():
    plt.rcParams.update({
        "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
        "axes.edgecolor": GRADE_COR, "axes.labelcolor": TINTA_2, "axes.titlecolor": TINTA,
        "axes.titleweight": "bold", "axes.titlesize": 12, "axes.titlelocation": "left",
        "xtick.color": TINTA_2, "ytick.color": TINTA_2, "font.size": 10.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRADE_COR, "grid.linewidth": 0.8,
        "font.family": "DejaVu Sans",  # mesma fonte em qualquer máquina (reprodutível)
    })


def _rodape(fig):
    fig.text(0.01, 0.01, f"Vital Data Lab · {AVISO}", fontsize=8, color=PALETA["terracota"])


def _salvar(fig, nome):
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIGURAS / nome, dpi=160)
    plt.close(fig)


def figura_comparacao(rf: dict, persist: dict, comum: dict):
    metr = [("f1_macro", "F1 macro"), ("recall_critico", "Recall do Crítico")]
    series = [("Random Forest", rf, PALETA["terracota"]),
              ("Regra \"fica onde está\"", persist, PALETA["marrom"]),
              ("Classe mais comum", comum, CINZA_BASE)]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(metr))
    w = 0.26
    for k, (nome, m, cor) in enumerate(series):
        valores = [m[c] for c, _ in metr]
        barras = ax.bar(x + (k - 1) * w, valores, w * 0.92, color=cor, label=nome, zorder=3)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.2f}".replace(".", ","),
                    ha="center", va="bottom", fontsize=9.5, color=TINTA,
                    bbox=dict(fc=FUNDO, ec="none", pad=1))
    ax.axhline(0.80, color=PALETA["verde"], lw=1.2, ls="--", zorder=2)
    ax.text(len(metr) - 0.5, 0.815, "meta do KPI 3 (F1 ≥ 0,80)", color=PALETA["verde"], fontsize=8.5, ha="right")
    ax.set_xticks(x, [r for _, r in metr])
    ax.set_ylim(0, 1.18)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.grid(axis="x", visible=False)
    ax.set_title("Prever a faixa do próximo ciclo: o modelo não supera a persistência")
    ax.legend(frameon=False, loc="upper left", ncol=3, fontsize=9)
    _salvar(fig, "01_rf_vs_baselines.png")


def figura_matriz(cm: list):
    cm = np.array(cm)
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.imshow(cm, cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
        "vdl", ["#F6EFE4", PALETA["ambar"], PALETA["terracota"]]))
    for i in range(3):
        for j in range(3):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=13, fontweight="bold",
                    color="white" if cm[i, j] > cm.max() * 0.55 else TINTA)
    ax.set_xticks(range(3), ORDEM_FAIXAS)
    ax.set_yticks(range(3), ORDEM_FAIXAS)
    ax.set_xlabel("previsto pelo Random Forest")
    ax.set_ylabel("faixa real no ciclo seguinte")
    ax.grid(False)
    ax.set_title("Matriz de confusão · teste 2026")
    _salvar(fig, "02_matriz_confusao.png")


def figura_importancia(imp: dict):
    s = pd.Series(imp).sort_values()
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.barh(s.index, s.values, color=PALETA["ambar"], height=0.62, zorder=3)
    for y, v in enumerate(s.values):
        ax.text(v + s.max() * 0.01, y, f"{v:.3f}".replace(".", ","), va="center", fontsize=9, color=TINTA)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("queda no F1 macro ao embaralhar a variável (teste)")
    ax.set_title("O que o modelo mais usa: a própria pontuação atual")
    _salvar(fig, "03_importancia_variaveis.png")


def figura_motor(curva: pd.DataFrame, mae_sem: float):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(curva["ciclos"], curva["mae"], color=PALETA["terracota"], lw=2, marker="o", ms=7, zorder=3,
            label="motor com as ações do pacto")
    ax.axhline(mae_sem, color=PALETA["marrom"], lw=1.4, ls="--", label="sem considerar as ações")
    for x, y in zip(curva["ciclos"].iloc[[0, -1]], curva["mae"].iloc[[0, -1]]):
        ax.annotate(f"{y:.2f} pp".replace(".", ","), (x, y), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=9, color=TINTA)
    ax.set_xlabel("ciclos de histórico usados no treino")
    ax.set_ylabel("erro médio da previsão (pp)")
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("Motor de sugestões: o erro cai a cada ciclo que entra")
    _salvar(fig, "04_motor_curva_aprendizado.png")


def figura_silhueta(sil: dict, k_app: int):
    ks, vs = list(sil), list(sil.values())
    fig, ax = plt.subplots(figsize=(7, 3.8))
    cores = [PALETA["terracota"] if k == k_app else CINZA_BASE for k in ks]
    ax.bar([str(k) for k in ks], vs, color=cores, width=0.6, zorder=3)
    for k, v in zip(ks, vs):
        ax.text(str(k), v + 0.01, f"{v:.2f}".replace(".", ","), ha="center", fontsize=9.5, color=TINTA)
    ax.axhline(0.25, color=TINTA_2, lw=1, ls=":")
    ax.text(len(ks) - 0.5, 0.265, "abaixo de 0,25 = estrutura fraca", fontsize=8.5, color=TINTA_2, ha="right")
    ax.set_xlabel("número de grupos (k)")
    ax.set_ylabel("silhueta média")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"K-Means de território: k = {k_app} no app (escolha de domínio)")
    _salvar(fig, "05_kmeans_silhueta.png")


def figura_ponto_fraco(comum: dict, proto: dict):
    nomes = ["Base comum\n(IND01–IND10)", "Gerador do protótipo\n(17 itens)"]
    vals = [comum["repete"], proto["repete"]]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.bar(nomes, vals, color=[PALETA["terracota"], CINZA_BASE], width=0.5, zorder=3)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.0%}".replace(".", ","), ha="center", fontsize=11, fontweight="bold", color=TINTA)
    ax.set_ylim(0, 1)
    ax.set_ylabel("o item mais baixo se repete\nno ciclo seguinte")
    ax.grid(axis="x", visible=False)
    ax.set_title("Ponto fraco de um ciclo só não se sustenta")
    _salvar(fig, "06_ponto_fraco_estabilidade.png")


# ----------------------------------------------------------------------------- avaliações

def avaliar_prototipo() -> dict:
    """Modelos que estão no app (prototipo/): motor Ridge e K-Means de território."""
    from pulso.dados import DEPENDE_DE_ACS, EFEITOS_REAIS, gerar_base
    from pulso.eixos import ACOES, ITENS
    from pulso.motor import GRUPOS, atribuir_grupos, efeitos, transicoes, treinar

    equipes, painel, pactos = gerar_base()
    grupos_app = atribuir_grupos(equipes)
    equipes["grupo"] = grupos_app
    motor = treinar(transicoes(painel, equipes, pactos))

    # Efeito aprendido × efeito usado para gerar os dados, no estado atual das equipes.
    estado = painel[painel["t"] == painel["t"].max()].merge(equipes, on="equipe")
    aprendido = efeitos(motor, estado)
    acs_mod = 0.5 + (estado["cobertura_acs"].to_numpy() - 35) / 65
    verdadeiro = np.zeros_like(aprendido)
    itens, acoes = list(ITENS), list(ACOES)
    for k, a in enumerate(acoes):
        for item, ganho in EFEITOS_REAIS[a].items():
            j = itens.index(item)
            folga = np.clip((100 - estado[item].to_numpy()) / 50, 0.2, 1.6)
            verdadeiro[:, k, j] = ganho * folga * 0.85 * (acs_mod if a in DEPENDE_DE_ACS else 1.0)
    corr = float(np.corrcoef(aprendido.mean(axis=0).ravel(), verdadeiro.mean(axis=0).ravel())[0, 1])
    mutirao = float(aprendido[:, acoes.index("mutirao_sabado"), :].sum(axis=1).mean())
    melhor = acoes[int(aprendido.sum(axis=2).mean(axis=0).argmax())]

    # K-Means: mesma preparação do app, silhueta por k e conferência de que os grupos batem.
    Z = clusterizacao.padronizar(equipes.assign(renda_=equipes["renda"]), ["idhm", "saneamento", "renda_"],
                                 em_log=("renda_",))
    sil = clusterizacao.silhuetas(Z, range(2, 8))
    rot = clusterizacao.agrupar(Z, len(GRUPOS))
    mesmo_agrupamento = bool(pd.crosstab(rot, grupos_app.to_numpy()).gt(0).sum(axis=1).eq(1).all())

    rep = taxa_repeticao(painel, itens, "equipe", "t")
    return {
        "n_equipes": int(len(equipes)), "n_ciclos": int(painel["ciclo"].nunique()),
        "n_transicoes": int(motor.n_transicoes),
        "motor": {
            "mae_com_acoes_pp": round(motor.mae_ia, 3),
            "mae_sem_acoes_pp": round(motor.mae_sem_acoes, 3),
            "reducao_erro": round(1 - motor.mae_ia / motor.mae_sem_acoes, 3),
            "curva_aprendizado": motor.curva.round(3).to_dict(orient="records"),
            "correlacao_efeito_aprendido_vs_gerador": round(corr, 3),
            "ganho_medio_mutirao_sabado_pp": round(mutirao, 2),
            "acao_de_maior_ganho_medio": melhor,
        },
        "kmeans_territorio": {
            "variaveis": ["idhm", "saneamento", "log(renda)"], "k_app": len(GRUPOS),
            "silhueta_por_k": sil, "silhueta_k_app": sil[len(GRUPOS)],
            "k_maior_silhueta": max(sil, key=sil.get),
            "reproduz_grupos_do_app": mesmo_agrupamento,
        },
        "ponto_fraco": rep,
        "_curva": motor.curva,
    }


def relatorio_md(r: dict) -> str:
    rf, per, com = r["rf"]["random_forest_teste_temporal"], r["rf"]["baseline_persistencia"], r["rf"]["baseline_classe_comum"]
    cv, cvp = r["rf"]["random_forest_cv_por_equipe"], r["rf"]["persistencia_cv_mesmas_linhas"]
    m, km, p = r["prototipo"]["motor"], r["prototipo"]["kmeans_territorio"], r["prototipo"]
    pfc = r["ponto_fraco_base_comum"]
    f = lambda v: f"{v:.3f}".replace(".", ",")  # noqa: E731
    pct = lambda v: f"{v * 100:.0f}%"  # noqa: E731
    cm = r["rf"]["matriz_confusao"]["valores"]
    hp = r["rf"]["hiperparametros"]
    return f"""# Relatório dos modelos — Vital Data Lab (SR2)

> **{AVISO}.** Gerado por `python -m src.modelos.treinar_avaliar` em {r['gerado_em']}.
> Todo número abaixo sai deste comando. Não edite à mão: rode de novo.

## 1. Random Forest — faixa de ação no próximo ciclo (base comum)

**Pergunta:** olhando a equipe neste ciclo, em que faixa ela vai estar no próximo?
(Crítico < 500 · Atenção 500–749 · Excelência ≥ 750). Prever o *próximo* ciclo evita vazamento:
a faixa do ciclo atual é só a soma dos eixos.

- {r['rf']['n_pares']} pares equipe×ciclo consecutivos, {r['rf']['n_equipes']} equipes.
  Treino: {r['rf']['n_treino']} · Teste temporal (alvo em 2026.1 e 2026.2): {r['rf']['n_teste']}
  ({r['rf']['distribuicao_teste']['Crítico']} Crítico, {r['rf']['distribuicao_teste']['Atenção']} Atenção,
  {r['rf']['distribuicao_teste']['Excelência']} Excelência).
- Hiperparâmetros escolhidos por validação cruzada **só no treino**: `min_samples_leaf={hp['min_samples_leaf']}`,
  `class_weight={hp['class_weight']}`, {hp['n_estimators']} árvores, semente {hp['random_state']}.

| Teste temporal | Acurácia | F1 macro | Recall Crítico | Precisão Crítico |
|---|---|---|---|---|
| **Random Forest** | {f(rf['acuracia'])} | **{f(rf['f1_macro'])}** | {f(rf['recall_critico'])} | {f(rf['precisao_critico'])} |
| Regra "fica onde está" | {f(per['acuracia'])} | {f(per['f1_macro'])} | {f(per['recall_critico'])} | {f(per['precisao_critico'])} |
| Classe mais comum | {f(com['acuracia'])} | {f(com['f1_macro'])} | {f(com['recall_critico'])} | {f(com['precisao_critico'])} |

Validação cruzada agrupada por equipe (5 partes, mesma equipe nunca no treino e no teste):
Random Forest F1 macro **{f(cv['f1_macro'])}** × regra "fica onde está" {f(cvp['f1_macro'])}.

Matriz de confusão do Random Forest (linha = real, coluna = previsto; Crítico, Atenção, Excelência):
`{cm[0]}` · `{cm[1]}` · `{cm[2]}`.

**Leitura honesta.** O modelo supera com folga a classe mais comum, mas **empata com a regra "fica onde está"
na validação cruzada e perde para ela no teste temporal**. A faixa muda pouco de um ciclo para o outro:
das {r['rf']['n_teste']} equipes do teste, só {r['rf']['equipes_que_mudaram_de_faixa_no_teste']} mudaram de faixa, e o modelo acertou
{pct(r['rf']['rf_acerto_entre_as_que_mudaram'])} delas. A variável que ele mais usa é a pontuação atual.
**KPI 3 (F1 macro ≥ 0,80): não atingido ({f(rf['f1_macro'])}).**

**Decisão:** o Random Forest **não entra no app**. Um alerta que não bate a regra mais simples não pode ser
vendido ao gestor como previsão (Rudin, 2019). O valor está em recomendar a ação — seção 2.

## 2. Motor de sugestões (Ridge) — o modelo que está no app

Base do protótipo: {p['n_equipes']} equipes, {p['n_ciclos']} ciclos, {p['n_transicoes']} transições.
Teste: os dois ciclos mais recentes.

- Erro médio da previsão do ciclo seguinte: **{f(m['mae_com_acoes_pp'])} pp** com as ações do pacto ×
  {f(m['mae_sem_acoes_pp'])} pp sem elas → **{pct(m['reducao_erro'])} menos erro**.
- Correlação entre o efeito que o motor aprendeu e o efeito usado para gerar os dados: **{f(m['correlacao_efeito_aprendido_vs_gerador'])}**.
- O "mutirão de sábado", que as equipes escolhem achando que ajuda, rende em média só
  {str(m['ganho_medio_mutirao_sabado_pp']).replace('.', ',')} pp somados nos itens — o motor descobre isso sozinho.
- Limite: no protótipo os efeitos verdadeiros são conhecidos porque fomos nós que geramos os dados.
  Com dado real, essa conferência não existe; o que vale é o erro no ciclo seguinte, medido a cada ciclo.

## 3. K-Means de território — com quem é justo comparar

Variáveis: IDHM, saneamento e log da renda (padronizados). Silhueta por k: {km['silhueta_por_k']}.
O app usa **k = {km['k_app']}** (silhueta {f(km['silhueta_k_app'])}): quatro níveis de vulnerabilidade,
legíveis pelo gestor. O maior valor é k = {km['k_maior_silhueta']}, mas dois grupos não separam o território o
bastante para comparar pares. Reproduz exatamente os grupos do app: {'sim' if km['reproduz_grupos_do_app'] else 'NÃO'}.

## 4. Ponto fraco — só apontar o que se repete

O indicador mais baixo do Eixo 3 se repete no ciclo seguinte em **{pct(pfc['repete'])}** dos
{pfc['pares']} pares da base comum (muda em {pct(pfc['muda'])}). Com a regra "mais baixo em 3 dos últimos 3 ciclos",
**{r['ponto_fraco_regra_base_comum']['com_ponto_fraco']} de {r['ponto_fraco_regra_base_comum']['equipes']} equipes**
têm um ponto fraco defensável no último ciclo. No gerador do protótipo o item mais baixo se repete em
{pct(p['ponto_fraco']['repete'])} — diferença do gerador, não da realidade. Por isso a regra vale para quando o
app for ligado à base comum ou à real.

## 5. Régua

{r['regua']['mudam_de_zona']} equipes-ciclo mudam de zona entre a régua do Manual (900/800/600/400) e a do
dicionário (850/700/550/400). O semáforo de ação (500/750) é do projeto e não depende dessa escolha.
Pendência levada ao NIIMA.
"""


def main():
    _estilo()
    FIGURAS.mkdir(parents=True, exist_ok=True)
    if not BASE.exists():
        sys.exit("Base analítica não encontrada. Rode antes:  python -m src.etl.pipeline")

    base = pd.read_csv(BASE)
    print("[1/5] Random Forest na base comum (escolha de hiperparâmetros + teste temporal + CV)...")
    rf = classificador.avaliar(base)
    print("[2/5] Motor de sugestões e K-Means do protótipo...")
    proto = avaliar_prototipo()
    print("[3/5] Ponto fraco e régua...")
    validas = base[base["pontuacao_final"].notna()]
    pf = taxa_repeticao(validas, INDICADORES, "codigo_ine", "ciclo")
    pf_regra = cobertura_regra(validas, INDICADORES, "codigo_ine", "ciclo")

    resultado = {
        "aviso": AVISO, "gerado_em": date.today().isoformat(),
        "rf": {k: v for k, v in rf.items() if not k.startswith("_")},
        "prototipo": {k: v for k, v in proto.items() if not k.startswith("_")},
        "ponto_fraco_base_comum": pf, "ponto_fraco_regra_base_comum": pf_regra,
        "regua": {"mudam_de_zona": n_mudam_de_zona(base["pontuacao_final"]),
                  "manual_x_dicionario": comparar_reguas(base["pontuacao_final"]).to_dict()},
    }

    print("[4/5] Gráficos...")
    figura_comparacao(rf["random_forest_teste_temporal"], rf["baseline_persistencia"], rf["baseline_classe_comum"])
    figura_matriz(rf["matriz_confusao"]["valores"])
    figura_importancia(rf["importancia_permutacao_top10"])
    figura_motor(proto["_curva"], proto["motor"]["mae_sem_acoes_pp"])
    figura_silhueta(proto["kmeans_territorio"]["silhueta_por_k"], proto["kmeans_territorio"]["k_app"])
    figura_ponto_fraco(pf, proto["ponto_fraco"])

    print("[5/5] Salvando relatórios...")
    (SAIDA / "metricas_modelos.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(rf["matriz_confusao"]["valores"], index=[f"real_{f}" for f in ORDEM_FAIXAS],
                 columns=[f"prev_{f}" for f in ORDEM_FAIXAS]).to_csv(SAIDA / "matriz_confusao.csv")
    (SAIDA / "RELATORIO_MODELOS.md").write_text(relatorio_md(resultado), encoding="utf-8")

    r, b = rf["random_forest_teste_temporal"], rf["baseline_persistencia"]
    m = proto["motor"]
    print("\n================ RESUMO (base sintética) ================")
    print(f"Random Forest (teste 2026.1–2026.2): F1 macro {r['f1_macro']} · recall Crítico {r['recall_critico']}")
    print(f"Regra 'fica onde está':              F1 macro {b['f1_macro']} · recall Crítico {b['recall_critico']}")
    print(f"Motor do app: erro {m['mae_com_acoes_pp']} pp com ações × {m['mae_sem_acoes_pp']} sem "
          f"({m['reducao_erro']:.0%} menos) · correlação efeitos {m['correlacao_efeito_aprendido_vs_gerador']}")
    print(f"K-Means do app: k={proto['kmeans_territorio']['k_app']} silhueta {proto['kmeans_territorio']['silhueta_k_app']}")
    print(f"Ponto fraco se repete: {pf['repete']:.0%} (base comum) · régua: {resultado['regua']['mudam_de_zona']} mudam de zona")
    print(f"Arquivos em {SAIDA.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()
