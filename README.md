# Vital Data Lab

**Pulso da Unidade — Índice Inteligente de Desempenho para a Atenção Básica do Recife**

Projeto 5 · Gestão de Tecnologia da Informação · CESAR School · 2026.2  
Desafio: Recife Monitora — SEAB / NIIMA, Secretaria de Saúde do Recife

> *o pulso do Recife em decisões que salvam*

🔗 **Site do projeto:** https://sites.google.com/cesar.school/vitaldatalab

---

## O que este projeto entrega

Um painel na web que dá uma nota de **0 a 100** para cada Unidade de Saúde da Família do Recife, diz em qual das três faixas ela está — **Crítico, Atenção ou Excelência** — e escreve, em uma linha, o que o gestor daquele território deve fazer primeiro.

A nota considera o contexto social do bairro, para que uma unidade em território vulnerável não seja penalizada por atender uma população mais difícil.

**O índice existe para direcionar recursos, nunca para punir equipes.**

### O que não é

- Não é um sistema de prontuário — não tocamos em dado de paciente.
- Não é um ranking para cobrar equipe — é uma fila de prioridade para a gestão.
- Não é um relatório em PDF — é uma aplicação que atualiza com a base.
- Não é substituto do Recife Monitora — é uma camada de inteligência construída sobre os dados do programa.

### O mecanismo

```text
Bases do projeto
      │
      ▼
Pipeline de dados
Extract → Transform → Integrate → Load
      │
      ▼
Base analítica
      │
      ▼
PULSO 0–100
      ├──► Classificação
      ├──► Agrupamento
      └──► Recomendação
                │
                ▼
              gestor
```

---

## Dados utilizados

O desenvolvimento atual utiliza as cinco bases fornecidas para o projeto:

- `equipes.csv`
- `resultados_ciclos.csv`
- `eixo3_indicadores.csv`
- `nps_atributos.csv`
- `planos_acao.csv`

As bases são **sintéticas e destinadas ao desenvolvimento acadêmico**. Nenhum número deve ser interpretado como resultado oficial ou desempenho real das equipes e unidades de saúde do Recife.

Os arquivos originais são preservados em:

```text
data/raw/
```

Após o tratamento e as validações, as bases processadas são armazenadas em:

```text
data/processed/
```

A integração das fontes gera:

```text
data/processed/base_analitica.csv
```

A base analítica mantém uma observação por combinação de **equipe e ciclo de avaliação**.

---

## Pipeline de dados

O pipeline está organizado em quatro responsabilidades:

```text
Extract
   ↓
Transform
   ↓
Integrate
   ↓
Load
```

### Extract

`src/etl/extract.py`

Realiza o carregamento das cinco bases originais presentes em `data/raw/`.

### Transform

`src/etl/transform.py`

Executa as rotinas de preparação e validação dos dados, incluindo:

- padronização;
- tratamento de duplicidades;
- tratamento de valores ausentes;
- tratamento de inconsistências;
- tratamento de valores fora dos domínios esperados;
- validação de integridade referencial;
- aplicação das regras de qualidade definidas para as bases.

### Integrate

`src/etl/integrate.py`

Relaciona as bases tratadas e constrói a base analítica utilizada pelas etapas posteriores do projeto.

### Load

`src/etl/load.py`

Realiza a persistência das bases tratadas e da base analítica em `data/processed/`.

### Pipeline

`src/etl/pipeline.py`

Orquestra as etapas do pipeline de dados.

---

## Como reproduzir

### 1. Clonar

```bash
git clone https://github.com/nayaalmeida/vital-data-lab.git
cd vital-data-lab
```

### 2. Ambiente e dependências

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

### 3. Pipeline de dados

```bash
python -m src.etl.pipeline
```

### 4. Dashboard

```bash
streamlit run app.py
```

O `requirements.txt` mantém as dependências necessárias para reprodução do ambiente.

As decisões relevantes de tratamento devem permanecer registradas no código e na documentação do projeto, garantindo rastreabilidade e reprodutibilidade.

---

## Notebooks

Os notebooks documentam o processo de entendimento, preparação, análise e modelagem dos dados.

```text
notebooks/
├── 01_entendimento_dados.ipynb
├── 02_preparacao_dados.ipynb
├── 03_analise_exploratoria.ipynb
└── 04_modelagem.ipynb
```

### 01 — Entendimento dos dados

Realiza a leitura inicial das cinco bases, análise estrutural, identificação das chaves e entendimento das relações entre as tabelas.

### 02 — Preparação dos dados

Documenta os problemas de qualidade identificados, as verificações realizadas e as decisões adotadas durante a preparação dos dados.

### 03 — Análise exploratória

Explora os dados tratados, incluindo participação ao longo dos ciclos, comportamento das pontuações e eixos, diferenças entre distritos, NPS e planos de ação.

### 04 — Modelagem

Destinado à documentação das etapas relacionadas ao Pulso da Unidade, classificação, agrupamento e demais componentes analíticos do produto.

---

## Pulso da Unidade

O Pulso da Unidade é um índice de **0 a 100** criado pelo projeto para sintetizar informações de desempenho e apoiar a priorização da gestão.

Ele **não substitui a pontuação existente do Recife Monitora**. A proposta é acrescentar uma camada de inteligência que permita:

1. considerar o contexto em que a unidade atua;
2. explicar quais dimensões influenciam sua situação;
3. identificar pontos de maior atenção;
4. transformar os resultados em recomendações acionáveis para a gestão.

A metodologia completa está documentada em:

```text
docs/produto/indice_pulso.md
```

Parâmetros metodológicos que dependem de validação de domínio devem permanecer identificados na documentação e no código.

---

## Classificação

O produto propõe três faixas de interpretação do Pulso:

- **Crítico**
- **Atenção**
- **Excelência**

A camada de modelagem busca também fornecer explicabilidade sobre as variáveis relacionadas à classificação.

---

## Agrupamento

Unidades com perfis semelhantes podem ser agrupadas para permitir comparações mais adequadas entre contextos próximos.

A proposta é evitar que toda unidade seja comparada simplesmente com a média geral, permitindo análises entre unidades com características semelhantes.

---

## Recomendação

O motor de recomendação transforma os resultados analíticos em ações priorizadas para a gestão.

As recomendações seguem regras determinísticas e auditáveis, permitindo identificar por que determinada ação foi sugerida.

As regras e parâmetros utilizados nessa camada devem passar por validação de domínio antes de serem considerados definitivos.

---

## Estrutura

```text
vital-data-lab/
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_entendimento_dados.ipynb
│   ├── 02_preparacao_dados.ipynb
│   ├── 03_analise_exploratoria.ipynb
│   └── 04_modelagem.ipynb
│
├── src/
│   ├── etl/
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── integrate.py
│   │   ├── load.py
│   │   └── pipeline.py
│   │
│   ├── indice/
│   │   └── pulso.py
│   │
│   ├── modelos/
│   │   ├── classificador.py
│   │   └── clusterizacao.py
│   │
│   ├── recomendacao/
│   │   └── motor.py
│   │
│   └── viz/
│       └── tema.py
│
└── docs/
```

---

## Documentação

A documentação completa está disponível em `docs/`.

Os documentos mais consultados incluem:

| Quero entender… | Leia |
|---|---|
| o problema do cliente | `docs/imersao/problema.md` |
| o que se sabe do Recife Monitora | `docs/imersao/pesquisa_publica_recife_monitora.md` |
| por que essa solução e não outra | `docs/produto/solucao.md` |
| como o índice é calculado | `docs/produto/indice_pulso.md` |
| quem faz o quê e até quando | `docs/produto/plano_execucao.md` |
| a fundamentação acadêmica | `docs/imersao/revisao_literatura.md` |
| os riscos e planos de contingência | `docs/imersao/riscos.md` |
| conformidade com a LGPD | `docs/lgpd.md` |

---

## Privacidade por construção

O projeto trabalha com **dados sintéticos e agregados por equipe/unidade**, sem registros individuais de pacientes.

Os identificadores necessários ao relacionamento das bases, como `codigo_ine` e `codigo_cnes`, são preservados para permitir a integração correta das informações.

Nenhum dado individual de paciente deve entrar no pipeline ou no repositório.

---

## Equipe

| Papel | Quem |
|---|---|
| Gestão de Projeto | Aynoã (Naya) Almeida |
| Engenharia de Dados | Leônidas Carvalho |
| Análise de Dados | Marcela Santos |
| Ciência de Dados | Cauã Cabral |
| Domínio e Conformidade | Danilo Brito |
| UI/UX Design | Beatriz |
| Desenvolvimento e Qualidade | Pedro Henrique Macêdo |

Responsabilidades detalhadas em `docs/gestao/papeis.md`.

---

## Estado do projeto

### Pipeline de dados

O pipeline atualmente:

- carrega as cinco bases fornecidas;
- executa tratamento e validações;
- verifica integridade entre as fontes;
- salva as bases tratadas;
- constrói a base analítica integrada.

A base analítica resultante possui atualmente **1.363 observações e 43 variáveis**, sem duplicidade na combinação de equipe e ciclo.

### Análise de dados

Os notebooks de:

- entendimento dos dados;
- preparação dos dados;
- análise exploratória;

estão implementados e executáveis do início ao fim.

### Pulso, modelos e recomendação

O Pulso da Unidade, a classificação, o agrupamento e o motor de recomendação fazem parte da proposta central do Vital Data Lab.

Esses componentes estão sendo adequados à estrutura das bases atualmente utilizadas no projeto, preservando a proposta metodológica documentada e os parâmetros que ainda dependem de validação de domínio.

---

## Observação sobre os dados

Este é um projeto acadêmico.

As bases utilizadas nesta etapa são sintéticas e os resultados produzidos não representam avaliações oficiais da rede municipal de saúde do Recife.