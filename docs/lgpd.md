# Conformidade com a LGPD

Responsável: Danilo Brito (Analista de Domínio e Conformidade)
Última atualização: —

## Princípio

O Vital Data Lab trabalha exclusivamente com **dados agregados por unidade
e equipe**. Nenhum dado individual de paciente é coletado, processado ou
armazenado.

A conformidade não é um controle adicionado depois: é consequência da
unidade de análise escolhida no desenho da solução.

## Base legal

- **Finalidade** (Art. 7º e Art. 11) — gestão pública em saúde e tutela da
  saúde coletiva.
- **Minimização** (Art. 6º, III) — só entra no pipeline o que é necessário
  para calcular o índice.

## Controles implementados

| Controle | Onde está | Situação |
|---|---|---|
| Remoção de PII antes de qualquer análise | `src/etl/transform.py` → `remover_pii()` | Implementado |
| Lista de colunas proibidas | `src/etl/transform.py` → `COLUNAS_PROIBIDAS` | Implementado |
| Dados brutos fora do versionamento | `.gitignore` → `data/raw/` | Implementado |
| Controle de acesso por perfil no dashboard | `app.py` | Previsto |
| Registro de acessos | — | Previsto |

## Governança ética

O índice existe para **apoiar equipes e direcionar recursos**. Não é
instrumento de avaliação de pessoas.

Nenhum ranking nominal de equipes é exibido sem o contexto territorial ao
lado. Esta é uma regra de projeto, não uma recomendação.
