# Vital Data Lab

**Tripé de Ação — apoio à decisão para a Atenção Básica do Recife**

Projeto 5 · Gestão de Tecnologia da Informação · CESAR School · 2026.2  
Desafio: Recife Monitora — SEAB / NIIMA, Secretaria de Saúde do Recife

> *o pulso do Recife em decisões que salvam*

🔗 **Site do projeto:** https://sites.google.com/cesar.school/vitaldatalab

---

## O que este projeto entrega

Um painel na web que organiza a pontuação oficial do Recife Monitora, de **0 a 1.000**, para cada equipe de Saúde da Família do Recife, mostra em qual das três faixas de ação ela está — **Crítico (abaixo de 500), Atenção (500 a 749) ou Excelência (750 ou mais)** — e escreve, em uma linha, o que o gestor daquele território deve fazer primeiro.

A comparação é justa: cada equipe é comparada apenas com equipes do mesmo grupo, como o próprio Recife Monitora determina, para que uma equipe em território vulnerável não seja penalizada por atender uma população mais difícil.

**O painel existe para direcionar recursos, nunca para punir equipes.**

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
TRIPÉ 0–1.000
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
- aplicação das regras do programa: Bloco A só pontua com 30% ou mais de resposta, e equipe desclassificada fica sem nota (dado ausente), nunca com zero.

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

Explora os dados tratados, incluindo participação ao longo dos ciclos, comportamento das pontuações e eixos, diferenças entre distritos, indicadores do Eixo 3 por grupo de equipes, NPS e planos de ação.

### 04 — Modelagem

Previsto para o SR2: classificação da faixa de ação (Random Forest) e agrupamento de equipes comparáveis (K-Means), sobre a `base_analitica.csv`. Prazo: 23/10/2026. Responsável: Nicolas.

---

## Tripé de Ação

O Vital Data Lab organiza a pontuação oficial do Recife Monitora, de **0 a 1.000 pontos**, nos seus três eixos e coloca as recomendações em primeiro lugar:

1. **Ações desta semana:** o que o gestor deve fazer primeiro em cada equipe, com o motivo de cada ação;
2. **Três eixos:** autoavaliação (até 200), satisfação do usuário (até 200) e desempenho assistencial (até 600), cada um com status Crítico, Atenção ou Excelência;
3. **Regras do programa aplicadas:** quórum de 30% no Bloco A, desclassificada tratada como ausente (nunca zero) e Eixo 3 comparado só dentro do mesmo grupo de equipes.

> **Em transição (declarado em 15/10/2026):** o `src/indice/pulso.py` ainda calcula a versão anterior, de 0 a 100. Ele será substituído pelo cálculo dos três eixos na régua oficial até **18/10/2026** (responsável: Nicolas). O app continua no ar durante a troca.

---

## Classificação

Cada equipe recebe uma faixa de ação na régua oficial:

- **Crítico:** abaixo de 500 pontos
- **Atenção:** de 500 a 749 pontos
- **Excelência:** 750 pontos ou mais

Equipes desclassificadas aparecem como **Sem envio**, e não como nota zero. Equipes sem quórum no Bloco A aparecem como **Sem dado suficiente** nesse bloco.

A camada de modelagem busca também fornecer explicabilidade sobre as variáveis relacionadas à classificação.

---

## Agrupamento

O Eixo 3 é comparado apenas entre equipes do mesmo grupo, como o programa determina.

Além disso, equipes com perfis semelhantes podem ser agrupadas para permitir comparações mais adequadas entre contextos próximos, evitando que toda equipe seja comparada simplesmente com a média geral.

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
│   │   └── pulso.py          (em transição até 18/10/2026)
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
| como a pontuação é calculada (em revisão até 18/10/2026) | `docs/produto/indice_pulso.md` |
| quem faz o quê e até quando | `docs/produto/plano_execucao.md` |
| a fundamentação acadêmica | `docs/imersao/revisao_literatura.md` |
| os riscos e planos de contingência | `docs/imersao/riscos.md` |
| conformidade com a LGPD | `docs/lgpd.md` |

---

## Privacidade por construção

O projeto trabalha com **dados sintéticos e agregados por equipe**, sem registros individuais de pacientes ou de profissionais.

Os identificadores necessários ao relacionamento das bases, como `codigo_ine` e `codigo_cnes`, são preservados para permitir a integração correta das informações.

Nenhum dado individual de paciente deve entrar no pipeline ou no repositório.

---

## Equipe

| Papel | Quem |
|---|---|
| Gestão de Projeto | Aynoã (Naya) Almeida |
| Liderança Técnica: cálculo, modelos e deploy | Nicolas Soares da Silva Miguel |
| Análise de Dados | Marcela Santos |
| UI/UX e Product Owner | Beatriz Amaral |
| Direção de Arte | Cauã Cabral |
| Domínio, Conformidade e Processo | Danilo Brito |
| Desenvolvimento e Qualidade | Pedro Henrique Macêdo |

Leônidas Carvalho (Engenharia de Dados) participou do projeto até setembro de 2026; suas tarefas foram redistribuídas na equipe.

Responsabilidades detalhadas em `docs/gestao/papeis.md`.

---

## Estado do projeto

### Pipeline de dados

O pipeline atualmente:

- carrega as cinco bases fornecidas;
- executa tratamento e validações;
- aplica as regras do programa (quórum do Bloco A e desclassificada como ausente);
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

### Pendências declaradas

| O que falta | Quando fecha | Responsável |
|---|---|---|
| Substituir o cálculo antigo (0 a 100) pelo dos três eixos na régua oficial | 18/10/2026 | Nicolas |
| Comparação do Eixo 3 por grupo como coluna do pipeline | 18/10/2026 | Marcela |
| Modelos de classificação e agrupamento, com avaliação | 23/10/2026 | Nicolas |
| Guia de Reprodutibilidade atualizado para o pipeline novo | 22/10/2026 | Pedro |

---

## Observação sobre os dados

Este é um projeto acadêmico.

As bases utilizadas nesta etapa são sintéticas e os resultados produzidos não representam avaliações oficiais da rede municipal de saúde do Recife.
