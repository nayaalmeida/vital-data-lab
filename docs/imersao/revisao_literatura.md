# Revisão de literatura e estado da arte

**Dono:** Cauã Cabral · **Apoio:** Danilo Brito
**Entregável da Semana 3** (17–21/08/2026) · cobrado no SR1 em *Soluções Existentes*

**Tema:** dashboards analíticos com IA aplicados à gestão pública de saúde, e
construção de índices compostos de desempenho.

---

## 1. Strings de busca

Mínimo exigido: 2 strings, aplicadas em ao menos 2 bases.

**String 1 — dashboards e IA na gestão de saúde**

```
("dashboard" OR "data visualization" OR "business intelligence")
AND ("primary health care" OR "public health management")
AND ("machine learning" OR "artificial intelligence")
```

**String 2 — índices compostos de desempenho**

```
("composite index" OR "composite indicator" OR "performance index")
AND ("health facility" OR "primary care" OR "health system")
AND ("weighting" OR "normalization" OR "ranking")
```

**String 3 — produção brasileira (SciELO, Google Scholar)**

```
("índice composto" OR "indicador sintético") AND ("atenção primária" OR "atenção básica")
AND ("desempenho" OR "avaliação")
```

**Registro da execução** — preencher ao aplicar:

| String | Base | Data da busca | Resultados | Selecionados |
|---|---|---|---|---|
| 1 | ACM Digital Library | | | |
| 1 | IEEE Xplore | | | |
| 2 | Scopus | | | |
| 3 | SciELO | | | |

---

## 2. Artigos selecionados

> **Estado da leitura.** Os resumos abaixo foram extraídos das páginas dos
> artigos. **A leitura integral é obrigatória antes de citar qualquer um deles**
> em apresentação — a coluna *Lido por* deve ser preenchida com o nome de quem leu.

### A1 — Ranking hospital performance based on individual indicators: can we increase reliability by creating composite indicators?

- **Autores:** Austin, P. C.; Ceyisakar, I. E.; Steyerberg, E. W.; Lingsma, H. F.; Marang-van de Mheen, P. J.
- **Ano:** 2019 · **Revista:** BMC Medical Research Methodology
- **Link:** https://link.springer.com/article/10.1186/s12874-019-0769-x
- **Lido por:** _______

**Achados.** Indicadores compostos só alcançam boa capacidade de ranqueamento
quando seus componentes são fortemente correlacionados entre si (correlação
intra-institucional de pelo menos 0,5). Quando os componentes são independentes
ou fracamente correlacionados, o índice composto ranqueia *pior* que os
indicadores isolados. Em 46% dos cenários simulados o composto superou os
componentes individuais.

**Relevância para o Vital Data Lab.** É o artigo que sustenta — e limita — a
decisão central do projeto. Ele diz que não basta somar indicadores: só faz
sentido combinar os que representam o mesmo conceito de qualidade. Isso deve
guiar a escolha de quais indicadores entram no Pulso da Unidade e justifica
medir a correlação entre eles antes de fixar os pesos.

---

### A2 — Methods for modelling composite indices of access to healthcare facilities: a systematic literature review

- **Autores:** Musau, M. M.; Njogu, A.; Maina, A.; Snow, R. W.; Beňová, L.; Okiro, E. A.; Linard, C.; Macharia, P. M.
- **Ano:** 2025 · **Revista:** Population Health Metrics
- **Link:** https://link.springer.com/article/10.1186/s12963-025-00432-7
- **Lido por:** _______

**Achados.** Revisão sistemática de 19 estudos (de 4.291 recuperados) sobre
índices compostos de acesso a serviços de saúde. A maioria usa **normalização
min-max** para colocar indicadores em escala comum. A ponderação varia entre
pesos iguais (13 estudos) e métodos mais complexos como Análise de Componentes
Principais e Processo Analítico Hierárquico. A agregação predominante é
aritmética e **totalmente compensatória** — um valor alto numa dimensão encobre
um valor baixo em outra, limitação reconhecida pelos próprios autores. Apenas
63% dos estudos validaram seus índices.

**Relevância para o Vital Data Lab.** Fornece o método concreto do nosso índice:
min-max para levar cada indicador à escala 0–100, e pesos justificados por
critério explícito. Também traz o alerta da compensação — se a cobertura de
pré-natal for péssima e a de vacinação ótima, a média esconde o problema. Nosso
motor de recomendação existe justamente para não deixar isso passar.

---

### A3 — Health system measurement: Harnessing machine learning to advance global health

- **Ano:** 2018 · **Revista:** PLOS ONE
- **Link:** https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0204958
- **Lido por:** _______

**Achados.** *Preencher após leitura.*

**Relevância esperada.** Uso de aprendizado de máquina para medição de
desempenho de sistemas de saúde — sustenta a escolha de IA como método, e não
como enfeite tecnológico.

---

### A4 — Aplicação da Inteligência Artificial na Atenção Primária à Saúde: revisão de escopo e avaliação crítica

- **Ano:** 2025 · **Revista:** Saúde em Debate
- **Link:** https://www.scielosp.org/article/sdeb/2025.v49n145/e10070/
- **Lido por:** _______

**Achados.** *Preencher após leitura.*

**Relevância esperada.** Revisão brasileira, recente, sobre IA na Atenção
Primária. É a referência que ancora o projeto na realidade do SUS, e não em
literatura de sistemas de saúde estrangeiros.

---

### A5 — Better Measurement for Performance Improvement in Low- and Middle-Income Countries: a experiência da PHCPI

- **Ano:** 2017 · **Base:** PubMed
- **Link:** https://pubmed.ncbi.nlm.nih.gov/29226448/
- **Lido por:** _______

**Achados.** *Preencher após leitura.*

**Relevância esperada.** Descreve como a Primary Health Care Performance
Initiative construiu um arcabouço conceitual e selecionou indicadores para
comparar desempenho da Atenção Primária em países de renda baixa e média.
É o precedente institucional do que estamos fazendo em escala municipal.

---

## 3. Candidatos adicionais

Lista completa de candidatos triados, com links, na planilha
`Revisao_Literatura_VitalDataLab.xlsx` no Drive (pasta `02_IMERSAO`).

---

## 4. O que esta revisão mudou no projeto

Esta seção é o que diferencia uma revisão de literatura de uma lista de links.
Preencher conforme a leitura avança.

| Decisão do projeto | Artigo que sustenta | O que mudou |
|---|---|---|
| Normalizar indicadores por min-max antes de compor o índice | A2 | Método definido com base em prática consolidada, não por conveniência |
| Verificar correlação entre indicadores antes de fixar pesos | A1 | Passo novo, incluído no plano de modelagem |
| Não usar média simples como resposta final | A1, A2 | Motor de recomendação passa a apontar a dimensão mais fraca, para evitar compensação |
| | A3 | |
| | A4 | |
| | A5 | |
