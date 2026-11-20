# Relatório dos modelos — Vital Data Lab (SR2)

> **Base sintética · não é dado real.** Gerado por `python -m src.modelos.treinar_avaliar` em 2026-11-19.
> Todo número abaixo sai deste comando. Não edite à mão: rode de novo.

## 1. Random Forest — faixa de ação no próximo ciclo (base comum)

**Pergunta:** olhando a equipe neste ciclo, em que faixa ela vai estar no próximo?
(Crítico < 500 · Atenção 500–749 · Excelência ≥ 750). Prever o *próximo* ciclo evita vazamento:
a faixa do ciclo atual é só a soma dos eixos.

- 1122 pares equipe×ciclo consecutivos, 132 equipes.
  Treino: 880 · Teste temporal (alvo em 2026.1 e 2026.2): 242
  (17 Crítico, 176 Atenção,
  49 Excelência).
- Hiperparâmetros escolhidos por validação cruzada **só no treino**: `min_samples_leaf=3`,
  `class_weight=balanced`, 400 árvores, semente 42.

| Teste temporal | Acurácia | F1 macro | Recall Crítico | Precisão Crítico |
|---|---|---|---|---|
| **Random Forest** | 0,826 | **0,729** | 0,529 | 0,692 |
| Regra "fica onde está" | 0,839 | 0,768 | 0,706 | 0,750 |
| Classe mais comum | 0,727 | 0,281 | 0,000 | 0,000 |

Validação cruzada agrupada por equipe (5 partes, mesma equipe nunca no treino e no teste):
Random Forest F1 macro **0,746** × regra "fica onde está" 0,751.

Matriz de confusão do Random Forest (linha = real, coluna = previsto; Crítico, Atenção, Excelência):
`[9, 8, 0]` · `[4, 155, 17]` · `[0, 13, 36]`.

**Leitura honesta.** O modelo supera com folga a classe mais comum, mas **empata com a regra "fica onde está"
na validação cruzada e perde para ela no teste temporal**. A faixa muda pouco de um ciclo para o outro:
das 242 equipes do teste, só 39 mudaram de faixa, e o modelo acertou
15% delas. A variável que ele mais usa é a pontuação atual.
**KPI 3 (F1 macro ≥ 0,80): não atingido (0,729).**

**Decisão:** o Random Forest **não entra no app**. Um alerta que não bate a regra mais simples não pode ser
vendido ao gestor como previsão (Rudin, 2019). O valor está em recomendar a ação — seção 2.

## 2. Motor de sugestões (Ridge) — o modelo que está no app

Base do protótipo: 193 equipes, 8 ciclos, 1351 transições.
Teste: os dois ciclos mais recentes.

- Erro médio da previsão do ciclo seguinte: **2,409 pp** com as ações do pacto ×
  2,910 pp sem elas → **17% menos erro**.
- Correlação entre o efeito que o motor aprendeu e o efeito usado para gerar os dados: **0,996**.
- O "mutirão de sábado", que as equipes escolhem achando que ajuda, rende em média só
  1,83 pp somados nos itens — o motor descobre isso sozinho.
- Limite: no protótipo os efeitos verdadeiros são conhecidos porque fomos nós que geramos os dados.
  Com dado real, essa conferência não existe; o que vale é o erro no ciclo seguinte, medido a cada ciclo.

## 3. K-Means de território — com quem é justo comparar

Variáveis: IDHM, saneamento e log da renda (padronizados). Silhueta por k: {2: 0.559, 3: 0.472, 4: 0.458, 5: 0.446, 6: 0.441, 7: 0.437}.
O app usa **k = 4** (silhueta 0,458): quatro níveis de vulnerabilidade,
legíveis pelo gestor. O maior valor é k = 2, mas dois grupos não separam o território o
bastante para comparar pares. Reproduz exatamente os grupos do app: sim.

## 4. Ponto fraco — só apontar o que se repete

O indicador mais baixo do Eixo 3 se repete no ciclo seguinte em **11%** dos
1122 pares da base comum (muda em 89%). Com a regra "mais baixo em 3 dos últimos 3 ciclos",
**0 de 129 equipes**
têm um ponto fraco defensável no último ciclo. No gerador do protótipo o item mais baixo se repete em
79% — diferença do gerador, não da realidade. Por isso a regra vale para quando o
app for ligado à base comum ou à real.

## 5. Régua

523 equipes-ciclo mudam de zona entre a régua do Manual (900/800/600/400) e a do
dicionário (850/700/550/400). O semáforo de ação (500/750) é do projeto e não depende dessa escolha.
Pendência levada ao NIIMA.
