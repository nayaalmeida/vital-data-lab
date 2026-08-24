# Dicionário de dados

**Dona:** Marcela Santos · atualizar sempre que uma coluna entrar ou sair.

Base analítica: **uma linha por equipe de Saúde da Família**.
Arquivo real: `data/processed/base_analitica.csv`.
Arquivo simulado (plano B do risco R1): `data/processed/base_analitica_SIMULADA.csv`.

## Identificação

| Coluna | Tipo | Origem | O que é |
|---|---|---|---|
| `origem_dado` | texto | interno | `REAL` ou `SIMULADO`. Acompanha o dado até a tela. |
| `codigo_cnes` | texto | CNES | Código do estabelecimento. Chave de integração. |
| `codigo_ine` | texto | CNES | Código da equipe. Chave no nível de equipe. |
| `unidade` | texto | CNES | Nome da Unidade de Saúde da Família. |
| `equipe` | texto | CNES | Identificação da equipe. |
| `distrito` | texto | Recife em Dados | Distrito Sanitário. |

## Indicadores assistenciais — eixo de desempenho

Todos em percentual de 0 a 100. Fonte: SISAB / e-SUS APS.

| Coluna | O que mede |
|---|---|
| `cobertura_pre_natal` | Cobertura de acompanhamento pré-natal. |
| `vacinacao_infantil` | Cobertura vacinal das crianças cadastradas. |
| `hipertensos_acompanhados` | Hipertensos com acompanhamento em dia. |
| `diabeticos_acompanhados` | Diabéticos com acompanhamento em dia. |
| `saude_bucal_atendimentos` | Atendimentos de saúde bucal realizados. |
| `citopatologico_coletado` | Coleta de citopatológico na população-alvo. |

## Eixos do Recife Monitora

| Coluna | Tipo | Origem | O que é |
|---|---|---|---|
| `autoavaliacao_equipes` | 0–100 | Recife Monitora | Autoavaliação da equipe sobre seus processos. |
| `satisfacao_usuarios` | 0–100 | Recife Monitora | Satisfação de quem é atendido. |

⚠️ Estas duas colunas são as únicas **não públicas**. Enquanto não forem liberadas
pela SEAB, vêm da base simulada — ver risco R1.

## Contexto socioterritorial

| Coluna | Tipo | Origem | O que é |
|---|---|---|---|
| `idhm_bairro` | 0–1 | IBGE | Índice de Desenvolvimento Humano Municipal do bairro. |
| `saneamento_pct` | 0–100 | IBGE | Domicílios com saneamento adequado. |
| `populacao_adscrita` | inteiro | CNES / IBGE | População vinculada à equipe. |

## Colunas calculadas pelo pipeline

| Coluna | O que é | Onde nasce |
|---|---|---|
| `eixo_indicadores_assistenciais` | Média normalizada dos seis indicadores. | `src/indice/pulso.py` |
| `eixo_autoavaliacao_equipes` | Autoavaliação normalizada. | idem |
| `eixo_satisfacao_usuarios` | Satisfação normalizada. | idem |
| `desempenho_bruto` | Composição ponderada dos três eixos (60/20/20). | idem |
| `ajuste_contexto` | Correção pelo contexto, entre −10 e +10 pontos. | idem |
| `pulso` | **O índice, de 0 a 100.** | idem |
| `classificacao` | `Crítico` · `Atenção` · `Excelência`. | idem |
| `eixo_mais_fraco` | Dimensão que mais puxa a unidade para baixo. | idem |
| `grupo` | Grupo de unidades semelhantes. | `src/modelos/clusterizacao.py` |

## Colunas que nunca entram

`cpf`, `cns`, `nome`, `nome_paciente`, `nome_mae`, `data_nascimento`, `endereco`,
`telefone`, `email` — removidas em `src/etl/transform.py` antes de qualquer
análise. Ver `lgpd.md`.
