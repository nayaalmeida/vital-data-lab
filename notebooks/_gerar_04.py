"""Gera e executa notebooks/04_modelagem.ipynb (rode na raiz: python notebooks/_gerar_04.py)."""
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

nb = nbf.v4.new_notebook()
nb.cells = [
    md("""# 04 · Modelagem e avaliação

**Vital Data Lab · Projeto 5 · GTI · CESAR School · 2026.2**

> ⚠️ **Base sintética.** Nenhum número deste notebook representa equipes, unidades ou resultados reais da Secretaria de Saúde do Recife.

Este notebook responde a quatro perguntas, cada uma com um modelo e uma avaliação honesta:

| Pergunta | Técnica | Onde está |
|---|---|---|
| Quanto cada ação muda cada item? | Regressão Ridge, um modelo por item | `prototipo/pulso/motor.py` (no app) |
| Com quem é justo comparar? | K-Means de território | `prototipo/pulso/motor.py` (no app) · `src/modelos/clusterizacao.py` |
| Em que faixa a equipe vai estar no próximo ciclo? | Random Forest | `src/modelos/classificador.py` (avaliado, fora do app) |
| Qual é o ponto fraco da equipe? | Regra de estabilidade | `src/recomendacao/ponto_fraco.py` |

Tudo é calculado por **um comando**, que também gera `reports/`. O notebook só lê e explica:

```bash
python -m src.etl.pipeline           # gera data/processed/base_analitica.csv
python -m src.modelos.treinar_avaliar  # avalia tudo e escreve reports/
```"""),
    code("""import json, os, sys
from pathlib import Path

# O notebook mora em notebooks/; o código espera a raiz do repositório.
if Path.cwd().name == "notebooks":
    os.chdir("..")
sys.path.insert(0, str(Path.cwd()))

import pandas as pd
from IPython.display import Image, Markdown, display

from src.modelos import treinar_avaliar
treinar_avaliar.main()
R = json.loads(Path("reports/metricas_modelos.json").read_text(encoding="utf-8"))
fig = lambda nome: display(Image(filename=f"reports/figuras/{nome}", width=760))"""),

    md("""## 1. Random Forest: em que faixa a equipe vai estar no próximo ciclo?

**Por que o próximo ciclo:** a faixa do ciclo atual é só a soma dos eixos cortada em 500 e 750. Prever isso seria vazamento: o modelo copiaria a soma e acertaria 100% sem valor nenhum.

**Protocolo:**
1. **Teste temporal:** treina com o passado e testa nos pares cujo alvo é 2026.1 ou 2026.2, como seria em produção.
2. **Hiperparâmetros** escolhidos por validação cruzada **só no treino**.
3. **Validação cruzada agrupada por equipe** (5 partes): a mesma equipe nunca aparece no treino e no teste ao mesmo tempo.
4. **Duas linhas de base:** classe mais comum e "a equipe fica onde está" (persistência).
5. **Regras do programa:** desclassificada fica fora, nunca vira zero. O Bloco A sem quórum de 30% entra como ausente."""),
    code("""rf = R["rf"]
print(f"{rf['n_pares']} pares · {rf['n_equipes']} equipes · treino {rf['n_treino']} · teste {rf['n_teste']}")
print("Distribuição no teste:", rf["distribuicao_teste"])
print("Hiperparâmetros escolhidos no treino:", rf["hiperparametros"])
pd.DataFrame({
    "Random Forest (teste temporal)": rf["random_forest_teste_temporal"],
    "Regra 'fica onde está'": rf["baseline_persistencia"],
    "Classe mais comum": rf["baseline_classe_comum"],
    "Random Forest (CV por equipe)": rf["random_forest_cv_por_equipe"],
    "Persistência (mesmas linhas da CV)": rf["persistencia_cv_mesmas_linhas"],
}).T"""),
    code("""print("Grade de hiperparâmetros (validação cruzada só no treino, ordenada por F1 macro):")
pd.DataFrame(rf["grade_cv_treino"])"""),
    code("""fig("01_rf_vs_baselines.png"); fig("02_matriz_confusao.png"); fig("03_importancia_variaveis.png")"""),
    code("""m = rf["random_forest_teste_temporal"]; p = rf["baseline_persistencia"]
display(Markdown(f'''**Leitura.** O Random Forest supera com folga a classe mais comum (F1 {m["f1_macro"]} × {rf["baseline_classe_comum"]["f1_macro"]}),
mas **não supera a regra "fica onde está"** (F1 {p["f1_macro"]}; recall do Crítico {p["recall_critico"]} × {m["recall_critico"]}).
Das {rf["n_teste"]} equipes do teste, só **{rf["equipes_que_mudaram_de_faixa_no_teste"]}** mudaram de faixa, e o modelo acertou
**{rf["rf_acerto_entre_as_que_mudaram"]:.0%}** delas. A variável que ele mais usa é a pontuação atual.

**KPI 3 (F1 macro ≥ 0,80): não atingido ({m["f1_macro"]}).**

**Decisão:** o Random Forest **não entra no app**. Um alerta que não bate a regra mais simples não pode ser
apresentado ao gestor como previsão (Rudin, 2019). O valor está em recomendar a ação, como mostra a seção 2.'''))"""),

    md("""## 2. Motor de sugestões (Ridge): o modelo que está no app

Para cada item dos três eixos, uma regressão Ridge explica a variação de um ciclo para o outro a partir do ponto de partida, do território e das ações pactuadas. As interações deixam o efeito de cada ação variar com o espaço que o item tem para crescer e com a cobertura de ACS. Assim o motor separa o efeito da ação da volta natural à média.

O protótipo usa um gerador sintético próprio, e por isso dá para conferir se o motor **reencontra** os efeitos usados para gerar os dados."""),
    code("""mo = R["prototipo"]["motor"]
display(pd.Series({
    "equipes no protótipo": R["prototipo"]["n_equipes"],
    "transições equipe×ciclo": R["prototipo"]["n_transicoes"],
    "erro com as ações (pp)": mo["mae_com_acoes_pp"],
    "erro sem as ações (pp)": mo["mae_sem_acoes_pp"],
    "redução do erro": f"{mo['reducao_erro']:.0%}",
    "correlação efeito aprendido × gerador": mo["correlacao_efeito_aprendido_vs_gerador"],
    "ganho médio do mutirão de sábado (pp)": mo["ganho_medio_mutirao_sabado_pp"],
    "ação de maior ganho médio": mo["acao_de_maior_ganho_medio"],
}, name="motor"))
fig("04_motor_curva_aprendizado.png")"""),
    md("""**Limite declarado:** no protótipo, os efeitos verdadeiros são conhecidos porque nós geramos os dados. Com dado real essa conferência não existe; o que vale é o erro de previsão do ciclo seguinte, medido a cada ciclo que entra (a curva acima)."""),

    md("""## 3. K-Means de território: com quem é justo comparar

As equipes são agrupadas por IDHM, saneamento e log da renda. Cada equipe é comparada com as de território parecido, não com a média da cidade (CP-FIT). O app usa **k = 4**, que é escolha de domínio: quatro níveis de vulnerabilidade que o gestor consegue ler. A silhueta mostra que essa estrutura é razoável."""),
    code("""km = R["prototipo"]["kmeans_territorio"]
print("Silhueta por k:", km["silhueta_por_k"])
print(f"k do app = {km['k_app']} (silhueta {km['silhueta_k_app']}) · maior silhueta em k = {km['k_maior_silhueta']}")
print("Este módulo reproduz exatamente os grupos do app:", km["reproduz_grupos_do_app"])
fig("05_kmeans_silhueta.png")"""),

    md("""## 4. Ponto fraco: só apontar o que se repete

O professor alertou que, na base comum, o item mais baixo de uma equipe muda de um ciclo para o outro em quase todos os casos. Medimos na nossa base tratada e aplicamos a regra **"mais baixo em 3 dos últimos 3 ciclos"**."""),
    code("""pf, regra = R["ponto_fraco_base_comum"], R["ponto_fraco_regra_base_comum"]
print(f"Base comum: o indicador mais baixo se repete em {pf['repete']:.0%} dos {pf['pares']} pares (muda em {pf['muda']:.0%}).")
print(f"Pela regra 3 de 3: {regra['com_ponto_fraco']} de {regra['equipes']} equipes têm ponto fraco defensável no último ciclo.")
print(f"Gerador do protótipo: se repete em {R['prototipo']['ponto_fraco']['repete']:.0%} (diferença do gerador, não da realidade).")
fig("06_ponto_fraco_estabilidade.png")"""),
    md("""**Leitura:** com a base comum, a resposta honesta é *"não há ponto fraco defensável"*. O app mostra os itens abaixo dos pares, mas não elege um "vilão" da equipe. Quando o motor for ligado à base comum ou à real, essa regra entra antes de qualquer frase do tipo "o ponto fraco é X"."""),

    md("""## 5. Régua: Manual × dicionário

O semáforo de ação (500/750) é do projeto. A zona de certificação tem duas versões, a do Manual (900/800/600/400) e a do dicionário de dados (850/700/550/400), e elas não batem."""),
    code("""print(f"Equipes-ciclo que mudam de zona entre as duas réguas: {R['regua']['mudam_de_zona']}")
pd.DataFrame(R["regua"]["manual_x_dicionario"]).fillna(0).astype(int)"""),

    md("""## Conclusões e limites

1. **O motor de ações é o produto.** Com as ações do pacto, o erro de previsão cai 17%, e o motor reencontra os efeitos verdadeiros do gerador.
2. **Prever a faixa não agrega.** A faixa é estável de um ciclo para o outro, e a regra "fica onde está" já acerta o que o Random Forest acerta. Ele fica documentado como evidência, fora do app.
3. **Ponto fraco só quando se repete.** Na base comum quase nunca se repete.
4. **Limites:** a base é sintética. A adesão das equipes é voluntária, então a ausência de uma equipe pode ser escolha dela, e isso gera viés de seleção. O teste temporal tem só 17 casos de Crítico. Com dado real, a avaliação deve ser repetida a cada ciclo rodando o mesmo comando."""),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.metadata["language_info"] = {"name": "python"}

if __name__ == "__main__":
    destino = RAIZ / "notebooks" / "04_modelagem.ipynb"
    NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(RAIZ / "notebooks")}}).execute()
    nbf.write(nb, destino)
    print("Notebook executado e salvo em", destino.relative_to(RAIZ))
