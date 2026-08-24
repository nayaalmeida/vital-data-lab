# Como trabalhamos

**Dono:** Naya · publicado também na página *Processo* do site.

## Dois trilhos que se cruzam

**Trilho de descoberta — Design Thinking.** Imersão, ideação, prototipação e
validação. Impede a equipe de construir uma solução elegante para a dor errada.

**Trilho técnico — pipeline de dados.** Coleta, limpeza, análise exploratória,
modelagem e entrega. Transforma a hipótese em número reproduzível.

Nenhuma decisão técnica é tomada sem passar pela descoberta, e nenhum artefato de
descoberta é considerado pronto até virar dado ou código.

## As cinco etapas

| # | Etapa | Quando | O que sai daqui |
|---|---|---|---|
| 1 | Imersão | ago–set | descrição formal do problema, riscos e stakeholders |
| 2 | Ideação | set | solução selecionada e o que ficou de fora |
| 3 | Preparação dos dados | set–out | base analítica: uma linha por unidade |
| 4 | Modelagem | out | índice calculado, classificação explicável |
| 5 | Entrega e validação | nov | MVP e registro do que o cliente disse |

## Ferramentas, e por que cada uma

| Ferramenta | Justificativa |
|---|---|
| Python + Pandas | tratamento reexecutável e auditável; planilha manual não é reprodutível |
| Scikit-Learn | modelos explicáveis que cabem no semestre e permitem dizer *por que* |
| Plotly | gráficos interativos que o gestor explora sem depender de nós |
| Streamlit + nuvem | aplicação real, com link público, sem custo de infraestrutura |
| GitHub | fonte única da verdade e histórico de versões |
| Google Sites e Drive | vitrine pública e repositório de documentos, sem instalar nada |

## O que não abrimos mão

1. **Dado agregado, sempre.** Nenhum dado individual de paciente entra no pipeline.
2. **O índice não pune.** Existe para direcionar recurso e apoio.
3. **Toda decisão é explicável.** Número sem porquê não sai daqui.
4. **Contexto conta.** Comparação dentro de grupos de perfil semelhante.
5. **Atraso se registra, não se apaga.**
