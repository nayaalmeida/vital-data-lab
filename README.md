# Vital Data Lab

**Pulso da Unidade — Índice Inteligente de Desempenho para a Atenção Básica do Recife**

Projeto 5 · Gestão de Tecnologia da Informação · CESAR School · 2026.2
Desafio: Recife Monitora — SEAB / NIIMA, Secretaria de Saúde do Recife

> *o pulso do Recife em decisões que salvam*

🔗 **Site do projeto:** https://sites.google.com/cesar.school/vitaldatalab

---

## O que este projeto entrega

Um painel na web que dá uma nota de **0 a 100** para cada Unidade de Saúde da
Família do Recife, diz em qual das três faixas ela está — **Crítico, Atenção ou
Excelência** — e escreve, em uma linha, o que o gestor daquele território deve
fazer primeiro.

A nota considera o contexto social do bairro, para que uma unidade em território
vulnerável não seja penalizada por atender uma população mais difícil.
**O índice existe para direcionar recursos, nunca para punir equipes.**

### O que não é

- Não é um sistema de prontuário — não tocamos em dado de paciente.
- Não é um ranking para cobrar equipe — é uma fila de prioridade para a gestão.
- Não é um relatório em PDF — é uma aplicação que atualiza com a base.
- Não é substituto do Recife Monitora — é a camada que lê o que ele coleta.

### O mecanismo

```
SISAB ┐
CNES  ├─► ETL (chave CNES) ─► PULSO 0–100 ─┬─► Classificação ─┐
IBGE  │                                     └─► Agrupamento ───┴─► Recomendação ─► gestor
Recife em Dados ┘
```

---

## Como reproduzir

```bash
# 1. Clonar
git clone https://github.com/<usuario>/vital-data-lab.git
cd vital-data-lab

# 2. Ambiente e dependências
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Pipeline de dados
python src/etl/pipeline.py

# 4. Dashboard
streamlit run app.py
```

O `requirements.txt` traz versões travadas: o ambiente fica idêntico ao nosso,
não apenas parecido. Cada decisão de tratamento está registrada em
`docs/decisoes_limpeza.md` — nenhum tratamento acontece fora do código versionado.

### ⚠️ Sobre os dados

Enquanto a Secretaria não disponibiliza os eixos de autoavaliação e satisfação, o
pipeline roda sobre uma **base simulada** de 182 equipes, gerada com semente fixa
por `src/dados_sinteticos/gerar.py`. Nenhum número representa o desempenho real da
rede: a marca `SIMULADO` acompanha o dado da geração até a tela do painel.

Quando o dado real chegar, basta colocá-lo em `data/processed/base_analitica.csv` —
o pipeline passa a usá-lo sozinho. **É substituição de arquivo, não retrabalho.**

---

## Estrutura

```
vital-data-lab/
├── README.md                   este arquivo
├── CONTRIBUTING.md             como trabalhar aqui
├── requirements.txt            dependências com versões travadas
├── app.py                      aplicação Streamlit
├── src/
│   ├── dados_sinteticos/       gerador da base simulada (plano B do risco R1)
│   ├── etl/                    extração, limpeza, anonimização e integração
│   ├── indice/                 cálculo do Pulso da Unidade
│   ├── modelos/                classificação e agrupamento
│   ├── recomendacao/           regras prescritivas
│   └── viz/                    paleta e template dos gráficos
├── notebooks/                  entendimento, limpeza, EDA e modelagem
├── data/
│   ├── raw/                    bruto, nunca editado, fora do Git
│   └── processed/              base agregada e anonimizada
└── docs/                       toda a documentação — ver docs/README.md
```

---

## Documentação

O índice completo está em **[docs/README.md](docs/README.md)**. Os documentos
mais consultados:

| Quero entender… | Leia |
|---|---|
| o problema do cliente | [docs/imersao/problema.md](docs/imersao/problema.md) |
| o que se sabe do Recife Monitora | [docs/imersao/pesquisa_publica_recife_monitora.md](docs/imersao/pesquisa_publica_recife_monitora.md) |
| por que essa solução e não outra | [docs/produto/solucao.md](docs/produto/solucao.md) |
| como o índice é calculado | [docs/produto/indice_pulso.md](docs/produto/indice_pulso.md) |
| quem faz o quê e até quando | [docs/produto/plano_execucao.md](docs/produto/plano_execucao.md) |
| a fundamentação acadêmica | [docs/imersao/revisao_literatura.md](docs/imersao/revisao_literatura.md) |
| os riscos e os planos B | [docs/imersao/riscos.md](docs/imersao/riscos.md) |
| conformidade com a LGPD | [docs/lgpd.md](docs/lgpd.md) |

---

## Privacidade por construção

Trabalhamos **exclusivamente com dados agregados por unidade e por equipe**.
Nenhum dado individual de paciente entra no pipeline. A remoção de informação
pessoal acontece em `src/etl/transform.py`, **antes de qualquer análise**.
Parecer completo em [docs/lgpd.md](docs/lgpd.md).

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

Responsabilidades detalhadas em [docs/gestao/papeis.md](docs/gestao/papeis.md).

---

## Estado do projeto

**O que já funciona hoje:** o pipeline roda ponta a ponta sobre a base simulada —
calcula o Pulso da Unidade, classifica nas três faixas com Random Forest
(acurácia média de 0,87 em validação cruzada estratificada), agrupa unidades
semelhantes com K-Means e gera recomendações prescritivas comparando cada unidade
com o seu grupo. O painel Streamlit exibe as três telas.

| Marco | Data | Situação |
|---|---|---|
| Kickoff | 27/08/2026 | previsto |
| SR1 — Status Report 1 | 24/09/2026 | previsto |
| Congelamento de escopo | 06/11/2026 | previsto |
| SR2 — Entrega final | 23/11/2026 | previsto |

Cronograma completo, com planejado x realizado, em
[docs/gestao/calendario.md](docs/gestao/calendario.md) e na planilha do Drive.
