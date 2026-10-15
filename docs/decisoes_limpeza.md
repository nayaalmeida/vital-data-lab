# Decisões de tratamento de dados

**Dona:** Marcela Santos
Regra: **toda decisão de tratamento vira uma linha aqui.** Correção feita e não
registrada é correção que ninguém consegue auditar — e é o que o critério de
Limpeza dos Dados procura.

Formato: data · o que foi encontrado · o que foi feito · por quê · quem decidiu.

---

## 24/08/2026 · Base de desenvolvimento simulada

**Encontrado.** Os dois eixos do Recife Monitora (autoavaliação e satisfação) não
estão em base pública, e o acesso ao detalhe por equipe ainda não foi confirmado
pela SEAB.

**Feito.** Criado `src/dados_sinteticos/gerar.py`, que produz 182 linhas — mesmo
número de equipes que participaram dos ciclos de 2023 — com as **mesmas colunas**
que a base real terá. Semente fixa em 42: todo mundo gera exatamente a mesma base.
Toda linha carrega `origem_dado = SIMULADO`, e a marca aparece na tela do painel.

**Por quê.** Plano B do risco R1. Permite desenvolver índice, modelo e painel sem
esperar o dado real. A troca depois é substituição de arquivo, não retrabalho.

**Quem.** Naya e Cauã.

---

## 24/08/2026 · Correlação entre indicadores antes de compor o índice

**Encontrado.** Na primeira versão da base simulada, os seis indicadores foram
sorteados de forma independente. A correlação média entre eles ficou em **0,02**,
e a função de verificação disparou o alerta.

**Feito.** Introduzido na geração um fator de **qualidade latente da equipe**: uma
equipe bem organizada tende a ir bem em vários indicadores ao mesmo tempo. Com ele,
a correlação passou a patamar compatível com a composição do índice.

**Por quê.** Austin et al. (2019, *BMC Medical Research Methodology*) mostram que
combinar indicadores fracamente correlacionados produz um índice que ranqueia
**pior** que os indicadores isolados. A verificação ficou permanente em
`src/indice/pulso.py::verificar_correlacao` e roda a cada execução do pipeline —
inclusive quando o dado real chegar.

**Quem.** Cauã.

---

## 24/08/2026 · Teto do ajuste por contexto

**Encontrado.** Sem limite, o ajuste socioterritorial poderia dominar o índice e
esconder o desempenho real da equipe.

**Feito.** Ajuste limitado a **±10 pontos** (`AJUSTE_MAXIMO` em `src/indice/pulso.py`).

**Por quê.** O ajuste existe para corrigir injustiça de comparação, não para
substituir a medição. Valor a validar com a SEAB no Kickoff.

**Quem.** Cauã, a validar com Danilo.

---

## 15/10/2026 · Limpeza da base comum do SR1

**Encontrado.** A tabela `resultados_ciclos` chegou com 1.392 registros, com repetições de equipe + ciclo; 58 registros sem pontuação nos eixos (equipes desclassificadas) e 230 sem nota no Eixo 2. Valores ausentes também em `equipes` (11), `nps_atributos` (260) e `planos_acao` (10).

**Feito.** Tratamento em código (`src/etl/transform.py`): padronização, remoção de duplicidades (1.392 → 1.363 registros, sem repetição de equipe + ciclo), tratamento de ausentes e outliers e checagem de integridade entre as cinco tabelas. Regras do programa aplicadas: Bloco A só pontua com 30% ou mais de resposta; equipe desclassificada fica sem nota (ausente), nunca com zero.

**Por quê.** Regras do Manual do Recife Monitora. Dar zero a quem não enviou dados confundiria "não avaliada" com "desempenho ruim" e geraria recomendação errada.

**Quem.** Marcela Santos.

**Substitui.** A base simulada de 24/08 (`src/dados_sinteticos/gerar.py`) foi substituída pela base comum disponibilizada pelo professor; o gerador foi removido do repositório em 15/10. O teto do ajuste por contexto (24/08) saiu do escopo em 15/10, com a adoção da régua oficial do Recife Monitora organizada nos três eixos.

---
## Modelo a preencher

```
## DD/MM/AAAA · <título curto>

**Encontrado.**
**Feito.**
**Por quê.**
**Quem.**
```
