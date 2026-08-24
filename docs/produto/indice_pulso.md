# Pulso da Unidade — como o índice é calculado

**Dono:** Cauã Cabral · fundamentação em `docs/imersao/revisao_literatura.md`

---

## 1. O que o índice é

Um número de **0 a 100** por unidade de Saúde da Família, que resume o desempenho
e é **ajustado pelo contexto socioterritorial** do bairro onde a unidade atua.

## 2. Por que 0–100 e não a pontuação já existente

O Recife Monitora já possui uma pontuação de 1.000 pontos, distribuída em três
eixos, e classifica equipes em zonas (ver `docs/imersao/pesquisa_publica_recife_monitora.md`).
O Pulso da Unidade **não substitui essa pontuação** — ele acrescenta três coisas
que a pontuação atual não tem:

1. ajuste pelo contexto social do território;
2. explicação de quais variáveis determinaram a classificação;
3. tradução da classificação em uma ação priorizada.

## 3. Método

### 3.1 Normalização

Cada indicador é levado à escala 0–100 por **normalização min-max**, método
predominante na literatura de índices compostos em saúde (A2). Indicadores em que
"menos é melhor" são invertidos antes da normalização.

### 3.2 Seleção dos indicadores

A literatura alerta que combinar indicadores fracamente correlacionados **piora**
a capacidade de ranqueamento em relação aos indicadores isolados (A1). Portanto,
antes de fixar a composição:

1. calcular a matriz de correlação entre os indicadores candidatos;
2. manter no índice apenas os que representam o mesmo conceito de qualidade;
3. registrar em `decisoes_limpeza.md` o que entrou, o que saiu e por quê.

### 3.3 Ponderação

Pesos definidos por critério explícito e validados pelo analista de domínio.
A literatura registra desde pesos iguais até métodos como Análise de Componentes
Principais (A2). Nossa escolha inicial: **pesos justificados clinicamente**, mais
defensáveis diante do gestor do que pesos estatísticos que ninguém sabe explicar.

### 3.4 Ajuste por contexto

Sobre o desempenho bruto aplica-se um ajuste derivado de variáveis sociais do
território (IDHM, saneamento, renda), de modo que uma unidade em território
vulnerável não seja penalizada por atender uma população mais difícil.

### 3.5 Limitação assumida

A agregação por média é **compensatória**: um valor alto em uma dimensão pode
encobrir um valor baixo em outra (A2). Não eliminamos essa limitação — a
contornamos: o motor de recomendação aponta sempre a **dimensão mais fraca**,
mesmo quando o índice geral está satisfatório.

## 4. Classificação

Três faixas — Crítico, Atenção, Excelência — atribuídas por modelo supervisionado
que expõe a importância de cada variável na decisão. Sem explicação, não sai daqui.

## 5. Agrupamento

Unidades de perfil semelhante são agrupadas, para que a comparação seja feita
dentro do grupo e não contra a média do município.
