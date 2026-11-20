# Dicionário de dados

**Dona:** Marcela Santos · atualizar sempre que uma coluna entrar ou sair · revisado em 20/11/2026

> ⚠️ **Base sintética.** Fornecida pela disciplina. Os valores não correspondem a equipes, unidades ou resultados reais da Secretaria de Saúde do Recife.

## Base analítica · `data/processed/base_analitica.csv`

- **Grão:** uma linha por **equipe × ciclo** (chave `codigo_ine` + `ciclo`, sem duplicidade).
- **Tamanho:** 1.363 linhas × 43 colunas · 132 equipes · 11 ciclos (2023.1 a 2026.2).
- **Gerada por:** `python -m src.etl.pipeline`, que integra as cinco bases de `data/raw/` aplicando as regras do programa (ver `decisoes_limpeza.md`).
- **Menor unidade de análise: a equipe.** Não há dado de paciente nem de profissional individual (`lgpd.md`).

### Identificação e cadastro · origem `equipes.csv`

| Coluna | Tipo | Domínio na base | O que é |
|---|---|---|---|
| `codigo_ine` | inteiro | 132 valores | Identificador Nacional de Equipe. Chave de integração |
| `ciclo` | decimal | 2023.1 a 2026.2 | Ciclo quadrimestral (três por ano) |
| `codigo_cnes` | inteiro | 7 dígitos | Unidade de saúde (CNES) |
| `nome_unidade` | texto | ex.: USF V-204 | Nome fictício da unidade |
| `nome_equipe` | texto | Equipe 001 a 132 | Rótulo fictício da equipe |
| `distrito_sanitario` | categórico | I a VIII | Distrito sanitário |
| `tipo_equipe` | categórico | eSF, eMulti | Tipo de equipe |
| `grupo` | inteiro | 1 a 4 | Grupo do programa: define quais indicadores do Eixo 3 valem e com que peso |
| `populacao_adscrita` | decimal | 900 a 10.847 · 8% vazio | População vinculada à equipe |
| `n_profissionais` | inteiro | 8 a 53 | Profissionais na equipe |

### Pontuação oficial · origem `resultados_ciclos.csv`

| Coluna | Tipo | Domínio na base | O que é |
|---|---|---|---|
| `eixo1_bloco_a` | decimal | 0 a 80 | Eixo 1 · percepção dos profissionais (instrumento anônimo). **Fica 0 quando o Bloco A não tem quórum** |
| `eixo1_bloco_b` | decimal | 0 a 60 | Eixo 1 · processos de trabalho |
| `eixo1_bloco_c` | decimal | 0 a 60 | Eixo 1 · estrutura e insumos |
| `eixo1_total` | decimal | 0 a 200 | Eixo 1 · autoavaliação da equipe |
| `taxa_resposta_bloco_a` | decimal | 0 a 1 | Proporção de profissionais que responderam o Bloco A |
| `bloco_a_valido` | booleano | True / False | **Regra 1:** falso quando a taxa de resposta é menor que 30% |
| `eixo2_total` | decimal | 0 a 200 · 16,5% vazio | Eixo 2 · satisfação do usuário (NPS convertido em pontos) |
| `eixo3_total` | decimal | 0 a 600 | Eixo 3 · desempenho assistencial |
| `pontuacao_final` | decimal | 0 a 1.000 · 4,3% vazio | Soma dos três eixos. **Vazia quer dizer desclassificada, nunca zero** |
| `zona_classificacao` | categórico | 5 zonas | Zona de certificação pela régua do dicionário (850/700/550/400). O Manual usa 900/800/600/400; a divergência foi levada ao NIIMA |
| `situacao_participacao` | categórico | Participante, Desclassificada | **Regra 2:** desclassificada não tem pontuação no ciclo |

As faixas de ação do projeto não estão na base. São calculadas em `src/indice/regua.py`: **Crítico** < 500 · **Atenção** 500–749 · **Excelência** ≥ 750.

### Eixo 3 por indicador · origem `eixo3_indicadores.csv` (pivotado)

Percentual alcançado, de 0 a 1. **Regra 3:** nem todo indicador vale para todo grupo. Por isso `IND03` e `IND08` têm 12,3% de vazios: o indicador não se aplica ao grupo da equipe, o que é diferente de dado faltante.

| Coluna | Indicador |
|---|---|
| `IND01` | Gestantes com 6 ou mais consultas de pré-natal |
| `IND02` | Gestantes com exames de sífilis e HIV |
| `IND03` | Gestantes com atendimento odontológico realizado |
| `IND04` | Cobertura de exame citopatológico do colo do útero |
| `IND05` | Cobertura vacinal de poliomielite e pentavalente em menores de 1 ano |
| `IND06` | Pessoas com hipertensão com pressão arterial aferida no semestre |
| `IND07` | Pessoas com diabetes com hemoglobina glicada solicitada |
| `IND08` | Cobertura de primeira consulta odontológica programática |
| `IND09` | Atendimentos de demanda espontânea resolvidos na APS |
| `IND10` | Visitas domiciliares realizadas por ACS |

### Eixo 2 por atributo · origem `nps_atributos.csv` (pivotado)

NPS de −100 a 100. Entre 3% e 4% de vazios, nos ciclos sem respondentes suficientes.

| Coluna | Atributo |
|---|---|
| `ATR1` | Acolhimento da equipe |
| `ATR2` | Tempo de espera para atendimento |
| `ATR3` | Resolutividade do atendimento |
| `ATR4` | Estrutura e limpeza da unidade |
| `ATR5` | Vínculo e confiança com a equipe |

### Plano de ação · origem `planos_acao.csv`

Cerca de 69% de vazios: nem toda equipe tem plano registrado em todo ciclo.

| Coluna | Tipo | Domínio na base | O que é |
|---|---|---|---|
| `id_plano` | texto | PA00001… | Identificador do plano |
| `texto_plano` | texto | livre | Texto escrito pela equipe. Usado só de forma agregada; não identifica pessoas |
| `dim_governanca` | decimal | 1 a 4 | Avaliação da governança do plano |
| `dim_smart` | decimal | 1 a 5 | O plano é específico, mensurável e tem prazo? |
| `dim_viabilidade` | decimal | 1 a 4 | Viabilidade do plano |
| `nivel_maturidade` | decimal | 1 a 3 | 1 Reformulação · 2 Ajustes · 3 Aprovado |
| `rotulo_maturidade` | categórico | Reformulação, Ajustes, Aprovado | Rótulo do nível de maturidade |

## Base do protótipo (app)

O app em `prototipo/` **não usa esta base**. Ele tem um gerador sintético próprio (`prototipo/pulso/dados.py`), com 193 equipes, 8 ciclos, 17 itens nos três eixos e um histórico de pactos com 16 ações possíveis. Os itens e as ações estão descritos em `prototipo/pulso/eixos.py`.
