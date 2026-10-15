# Protótipo · motor de sugestões de ações

Protótipo navegável do **Vital Data Lab** (Projeto 5, Gestão de TI, CESAR School, 2026.2), feito para o desafio da SEAB/NIIMA, da Secretaria de Saúde do Recife.

**Versão 2: motor de sugestões de ações.** A partir dos três eixos do Recife Monitora, a IA aprende com o histórico de pactos quais ações melhoram cada item e sugere, para cada equipe, o que colocar no pacto do próximo ciclo.

> **Protótipo independente.** Esta pasta não usa o pipeline nem as bases de `data/`: tem o próprio gerador de dados sintéticos e o próprio `requirements.txt`, com versões mais novas que as da raiz. Serve para validar a experiência e a ideia do motor; a ligação com as bases do projeto está em [Ligar às bases do projeto](#ligar-às-bases-do-projeto).

> **Dados sintéticos.** Os bairros e distritos sanitários dão a geografia. Os eixos, os pactos e os efeitos das ações foram gerados e não representam nenhuma equipe real.

## O que mudou desde a v1

Na v1 o protótipo criava uma régua própria: o Índice Pulso, de 0 a 100, com a classificação Crítico, Atenção ou Excelência. Na conversa com o Recife Monitora, ficou claro que a avaliação oficial continua sendo feita pelos **três eixos** e que o que agrega valor é a **recomendação de ações**.

| | v1 | v2 |
|---|---|---|
| Entrada | 6 indicadores de desempenho | Os 3 eixos do Recife Monitora (profissionais, cidadãos e desempenho) e os pactos de cada ciclo |
| Nota | Índice Pulso 0–100 | Nenhuma nota própria: usa as pontuações dos eixos |
| IA | Classificava a unidade (Crítico, Atenção, Excelência) | Aprende o efeito de cada ação e sugere o que fazer |
| Grão | Unidade (USF) | Equipe de saúde da família |
| Ciclo de aprendizado | Não havia | O resultado de cada pacto volta para o treino |

Os prints da v1 estão em [prints/v1](prints/v1/README.md) e os da v2 em [prints/v2](prints/v2/README.md), cada pasta com um PDF compilado.

## Como rodar

Requer Python 3.11 ou mais recente. Use um ambiente virtual só para esta pasta, porque as versões diferem das da raiz.

```bash
cd prototipo
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O app abre em http://localhost:8501. A primeira carga treina o motor e leva alguns segundos.

## Telas

| Tela | Para quem | O que mostra |
|---|---|---|
| **Visão do ciclo** | Gestão central e distrital | Os três eixos por distrito (ou por equipe), a evolução por ciclo, um mapa dos itens mais fracos, as ações com mais retorno no recorte e as equipes com maior potencial de avanço |
| **Sugestões** | Todos | Os três eixos da equipe comparados com equipes de território parecido e as 5 ações sugeridas para o pacto, com o efeito esperado em cada item, a evidência do histórico e os botões "Incluir no pacto" e "Não se aplica" |
| **Pacto do ciclo** | Todos | As ações escolhidas, a projeção dos eixos no fim do ciclo e como o resultado volta para a IA |
| **O que a IA aprendeu** | Todos | O efeito médio de cada ação em cada item, a melhora da previsão a cada ciclo, como o motor funciona, o que mudou desde a v1, fontes e privacidade |

Na barra lateral ficam o perfil de acesso (central, distrital ou equipe), o ciclo, o distrito, a equipe e o **foco das sugestões**: um eixo ou os três. Qualquer mudança recalcula as sugestões na hora.

## Como o motor funciona

1. **Junta os dados.** Para cada equipe e ciclo de quatro meses: os itens dos três eixos e as ações do pacto que ela assumiu para o ciclo seguinte.
2. **Aprende.** Para cada item, uma regressão regularizada (`Ridge`, scikit-learn) explica a variação entre um ciclo e o seguinte a partir do ponto de partida, do território e das ações pactuadas. Interações deixam o efeito de cada ação variar com o espaço que o item tem para crescer e com a cobertura de ACS. Assim o motor separa o efeito da ação da tendência natural do item de voltar à média.
3. **Sugere.** Para cada equipe, calcula o ganho esperado de cada ação em cada item, converte para pontos nos três eixos e ordena pelo foco escolhido. Cada sugestão mostra a evidência direta do histórico: quanto variaram as equipes que partiram de um valor parecido com e sem a ação.
4. **Reaprende.** No fim do ciclo, o resultado do pacto entra no histórico e o motor é treinado de novo. As sugestões marcadas como "não se aplica" deixam de aparecer para a equipe.

Nos dados sintéticos, os efeitos aprendidos batem com os efeitos usados para gerar os dados (correlação de 0,99). O motor também descobre que o "mutirão de sábado", que as equipes escolhem achando que ajuda, rende pouco. Considerar as ações reduz em 17% o erro de previsão do ciclo seguinte.

## Estrutura

```
app.py                     telas e filtros (Streamlit + Plotly)
pulso/eixos.py             os três eixos, os itens, as metas e o catálogo de ações
pulso/dados.py             base sintética: equipes, eixos por ciclo e pactos
pulso/motor.py             aprendizado dos efeitos, sugestões e evidência
pulso/estilo.py            identidade visual (cores e fonte do site)
scripts/capturar_prints.py prints das telas, PDF e galeria em Markdown
prints/v1, prints/v2       prints de cada versão
```

## Ligar às bases do projeto

A função `gerar_base()` em `pulso/dados.py` é a única fonte de dados do protótipo. Ela devolve três tabelas:

- `equipes`: uma linha por equipe, com `equipe` (INE), `nome`, `cnes`, `unidade`, `bairro`, `distrito`, `idhm`, `saneamento`, `renda`, `cobertura_acs` e `pessoas_cadastradas`.
- `painel`: uma linha por equipe e ciclo, com `equipe`, `ciclo`, `t` e os itens dos três eixos, em %.
- `pactos`: uma linha por ação pactuada, com `equipe`, `ciclo` e `acao` (chave do catálogo em `pulso/eixos.py`).

Para usar as bases de `data/processed/` no lugar da base sintética:

| Protótipo | Base do projeto |
|---|---|
| `equipes` | `equipes_tratado.csv` (INE, CNES, distrito, grupo, população adscrita) |
| itens do Eixo 1 | `resultados_ciclos_tratado.csv` (blocos A, B e C do Eixo 1) |
| itens do Eixo 2 | `nps_atributos_tratado.csv` (NPS por atributo) |
| itens do Eixo 3 | `eixo3_indicadores_tratado.csv` (percentual alcançado por indicador) |
| `pactos` | `planos_acao_tratado.csv` (texto do plano a classificar no catálogo de ações) |

Pontos em aberto para essa ligação:

- **Régua oficial.** O protótipo mostra cada eixo de 0 a 100. A régua oficial vai até 1.000 (Eixo 1 até 200, Eixo 2 até 200, Eixo 3 até 600), com as faixas oficiais. A tela precisa passar a usar essa régua.
- **Planos de ação em texto.** O motor precisa saber qual ação cada plano contém. É preciso classificar o `texto_plano` nas ações do catálogo, por regra ou por modelo, e validar com o grupo.
- **Catálogo de ações e itens.** Os de `pulso/eixos.py` são exemplos e devem seguir a metodologia do projeto (ver `CONTRIBUTING.md`, seção "Índice e modelagem").

## Prints

Com o app rodando, `.venv\Scripts\python scripts\capturar_prints.py` gera os prints em `prints/v2`, um PDF com todas as telas e uma galeria em Markdown. O script precisa do Playwright (`pip install playwright`) e usa o Microsoft Edge instalado na máquina, sem baixar navegador.
