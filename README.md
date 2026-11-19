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

### 4. Modelos e avaliação (SR2)

```bash
python -m src.modelos.treinar_avaliar
```

Leva cerca de 1 minuto, sem GPU, sem chave de API e sem internet. Avalia todos os modelos e grava em `reports/` a fonte única dos números do deck e do site: `metricas_modelos.json`, `RELATORIO_MODELOS.md` e os gráficos de `figuras/`. O notebook `04_modelagem.ipynb` roda o mesmo comando e explica o resultado.

### 5. Testes

```bash
python -m pytest -q tests                      # régua, classificador, ponto fraco, K-Means
cd prototipo && python -m pytest -q tests      # agente local e app (no ambiente do protótipo)
```

Os testes também rodam sozinhos no GitHub a cada push (`.github/workflows/testes.yml`).

### 6. App (MVP)

O app do MVP é o **motor de sugestões**, em `prototipo/`. Ele tem o próprio ambiente: veja `prototipo/README.md`.

```bash
cd prototipo
streamlit run app.py
```

> O `app.py` da raiz é a v1 (Índice Pulso 0–100), descontinuada desde a virada para os três eixos. Fica no repositório como histórico e não é o app publicado.

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

### 04 — Modelagem e avaliação

Avalia os quatro modelos do projeto, cada um contra uma linha de base honesta: o motor de sugestões (Ridge) e o K-Means de território, que estão no app; o Random Forest de faixa no próximo ciclo, que foi avaliado e ficou fora do app; e a regra de ponto fraco. Resumo em `reports/RELATORIO_MODELOS.md`.

---

## Tripé de Ação

O Vital Data Lab organiza a pontuação oficial do Recife Monitora, de **0 a 1.000 pontos**, nos seus três eixos e coloca as recomendações em primeiro lugar:

1. **Ações desta semana:** o que o gestor deve fazer primeiro em cada equipe, com o motivo de cada ação;
2. **Três eixos:** autoavaliação (até 200), satisfação do usuário (até 200) e desempenho assistencial (até 600), cada um com status Crítico, Atenção ou Excelência;
3. **Regras do programa aplicadas:** quórum de 30% no Bloco A, desclassificada tratada como ausente (nunca zero) e Eixo 3 comparado só dentro do mesmo grupo de equipes.

> **Régua no código (fechado em 19/11/2026):** `src/indice/regua.py` aplica as faixas de ação (500/750) e as duas versões da zona de certificação. O `src/indice/pulso.py` (0 a 100) é da v1 e fica só como histórico.

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

## Modelos e resultados (SR2)

| Pergunta | Técnica | Resultado na base sintética | No app? |
|---|---|---|---|
| Quanto cada ação muda cada item? | Ridge, um modelo por item | erro 2,41 pp com as ações × 2,91 sem (−17%); reencontra os efeitos do gerador (correlação 0,996) | **sim** |
| Com quem é justo comparar? | K-Means de território, k = 4 | silhueta 0,46; k = 4 é escolha de domínio (4 níveis de vulnerabilidade) | **sim** |
| Em que faixa a equipe vai estar no próximo ciclo? | Random Forest | F1 macro 0,73 × 0,77 da regra "fica onde está" (teste 2026.1–2026.2) | não: não supera a regra simples |
| Qual é o ponto fraco da equipe? | regra de estabilidade (3 de 3 ciclos) | na base comum o item mais baixo se repete em só 11% dos casos | regra pronta para a base comum |

Números gerados por `python -m src.modelos.treinar_avaliar`. Detalhes e limites em `reports/RELATORIO_MODELOS.md`.

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
│   │   ├── regua.py          (faixas 500/750 e zonas Manual × dicionário)
│   │   └── pulso.py          (v1, 0–100: histórico)
│   │
│   ├── modelos/
│   │   ├── classificador.py  (Random Forest, avaliação temporal)
│   │   ├── clusterizacao.py  (K-Means, silhueta)
│   │   └── treinar_avaliar.py (um comando → reports/)
│   │
│   ├── recomendacao/
│   │   ├── motor.py
│   │   └── ponto_fraco.py    (só aponta o que se repete)
│   │
│   └── viz/
│       └── tema.py
│
├── reports/                  (métricas, relatório e figuras gerados)
├── tests/
├── prototipo/                (app do MVP: motor de sugestões + IA local opcional)
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
| como a pontuação é calculada | `src/indice/regua.py` · `docs/produto/indice_pulso.md` (v1) |
| o que os modelos entregam, com números | `reports/RELATORIO_MODELOS.md` |
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

| O que falta | Situação | Responsável |
|---|---|---|
| Modelos de classificação e agrupamento, com avaliação | **Fechado em 19/11/2026** (previsto 23/10): `src/modelos/`, notebook 04, `reports/` | Nicolas |
| Régua oficial no código | **Fechado em 19/11/2026** (previsto 18/10): `src/indice/regua.py`; `pulso.py` (0–100) fica como histórico | Nicolas |
| Ligar o motor de sugestões à base comum (132 equipes) e à régua 0–1.000 | Depois do SR2: o app roda na base sintética própria do protótipo | Nicolas |
| Zona de certificação: Manual (900/800/600/400) × dicionário (850/700/550/400), 523 equipes-ciclo mudam | Levado ao NIIMA; o projeto usa o dicionário até a resposta | Naya |
| Comparação do Eixo 3 por grupo como coluna do pipeline | Em aberto (previsto 18/10) | Marcela |
| Guia de Reprodutibilidade atualizado para o pipeline novo | Em aberto (previsto 22/10); o README já cobre os comandos | Pedro |

---

## Observação sobre os dados

Este é um projeto acadêmico.

As bases utilizadas nesta etapa são sintéticas e os resultados produzidos não representam avaliações oficiais da rede municipal de saúde do Recife.
