# Papéis e responsabilidades

**Representantes eleitos:** Aynoã Naya Almeida (líder de processo / gestão de projeto)
e o líder técnico definido pela equipe.

| Papel | Quem | Responsabilidade | Artefatos que entrega |
|---|---|---|---|
| Gestão de Projeto | Aynoã (Naya) Almeida | Cronograma, alinhamento com a rubrica, interface com cliente e coordenação | Cronograma, atas, plano de execução, apresentações |
| Engenharia de Dados | Leônidas Carvalho | Coleta das fontes, integração pela chave CNES, anonimização na origem | `src/etl/*`, base analítica, tabela de-para do CNES |
| Análise de Dados | Marcela Santos | Qualidade do dado, tratamento, análise exploratória | `dicionario_dados.md`, `decisoes_limpeza.md`, notebooks |
| Ciência de Dados | Cauã Cabral | Índice, modelos, avaliação e explicabilidade | `src/indice/`, `src/modelos/`, relatório de métricas |
| Domínio e Conformidade | Danilo Brito | Sentido clínico dos indicadores, LGPD, ética das recomendações | Justificativa dos indicadores, `lgpd.md`, catálogo de recomendações |
| UI/UX Design | Beatriz | Wireframes, fluxo de navegação, identidade aplicada | Wireframes, protótipo, relatório de usabilidade |
| Desenvolvimento e Qualidade | Pedro Henrique Macêdo | Aplicação, deploy contínuo, reprodutibilidade | `app.py`, `requirements.txt`, ambiente publicado |

## Notas de gestão

**Sobre o papel de saúde.** Nenhum integrante atua profissionalmente na área da
saúde. O papel foi redefinido como **pesquisa de domínio**: estudo da documentação
do SUS, das fichas técnicas dos indicadores e da legislação de proteção de dados,
com as dúvidas remanescentes levadas ao parceiro.

**Sobre acúmulo de papéis.** A Gestora acumula gestão de projeto, produto e
direção de arte. A direção de arte deve ser transferida para a UI/UX Designer
**até 15/09** — o sistema visual já está documentado, então é transferência de
autoridade, não de criação. Ver risco R8 em `docs/imersao/riscos.md`.

## Como decidimos

- Cada dono de papel decide **como** fazer o que é seu.
- A gestão decide **prioridade e escopo**.
- Facilitação rotativa nas sessões de ideação.
- Decisões registradas em ata no Drive.
