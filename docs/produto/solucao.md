# A solução

**Dono:** Naya · publicado também na página *Solução* do site.

## Em uma frase

> Um painel na web que dá uma nota de 0 a 100 para cada Unidade de Saúde da
> Família do Recife, diz em qual das três faixas ela está — Crítico, Atenção ou
> Excelência — e escreve, em uma linha, o que o gestor daquele território deve
> fazer primeiro.

A nota considera o contexto social do bairro, para que uma unidade em território
vulnerável não seja penalizada por atender uma população mais difícil. O índice
existe para **direcionar recursos, nunca para punir equipes**.

## O que não é

- **Não é** um sistema de prontuário — não tocamos em dado de paciente.
- **Não é** um ranking para cobrar equipe — é uma fila de prioridade para a gestão.
- **Não é** um relatório em PDF — é uma aplicação web que atualiza com a base.
- **Não é** substituto do Recife Monitora — é a camada que lê o que ele coleta.

## As três opções avaliadas

### Opção 1 — Painel descritivo
Automatizar a consolidação das planilhas em um painel com filtros.
**Descartada:** resolve um terço da dor. Ataca o esforço manual, mas mantém a
cegueira contextual e a ausência de prescrição. Não incorpora IA.

### Opção 2 — Modelo preditivo de risco
Estimar a trajetória futura dos indicadores de cada unidade.
**Descartada:** previsão confiável exige série histórica longa. O programa foi
implantado em 2023 e os ciclos disponíveis são poucos. Além disso, *"esta unidade
tende a piorar"* não responde o que fazer na segunda-feira.
**Guardada como evolução futura.**

### Opção 3 — Índice inteligente de desempenho ⭐ escolhida
O **Pulso da Unidade**, com classificação explicável, agrupamento de unidades
comparáveis e motor de recomendação prescritiva.

## Por que a Opção 3

| Dor declarada | Opção 1 | Opção 2 | Opção 3 |
|---|:---:|:---:|:---:|
| Dependência de análise manual | sim | parcial | **sim** |
| Cegueira contextual | não | não | **sim** |
| Ausência de prescrição | não | parcial | **sim** |
| Priorização entre muitas equipes | parcial | parcial | **sim** |

**Viabilidade.** Usa dado transversal, sem exigir série histórica longa.
**Explicabilidade.** A classificação vem acompanhada das variáveis que pesaram.
**Justiça algorítmica.** O contexto social entra na conta, e não como enfeite:
é o que torna a comparação entre territórios diferentes defensável.

## O mecanismo

```
SISAB ┐
CNES  ├─► ETL (chave CNES) ─► PULSO 0–100 ─┬─► Classificação ─┐
IBGE  │                                     └─► Agrupamento ───┴─► Recomendação ─► gestor
Recife em Dados ┘
```

Detalhe do cálculo em `indice_pulso.md`. Divisão do trabalho em `plano_execucao.md`.
