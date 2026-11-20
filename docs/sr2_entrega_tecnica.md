# SR2 · Entrega técnica de IA — o que está pronto e o que falta

Branch `feat/sr2-ia-avaliacao` · 19/11/2026 · **base sintética: nenhum número aqui é dado real**

## O que esta branch entrega

| Rubrica (Técnico SR2) | Pts | Evidência |
|---|---|---|
| IA · Seleção da técnica | 0,75 | `src/modelos/classificador.py`, `clusterizacao.py`, docstrings com Rudin (2019) e CP-FIT |
| IA · Implementação | 1,25 | motor Ridge e K-Means no app (`prototipo/pulso/motor.py`) + Random Forest (`src/modelos/classificador.py`) |
| IA · Avaliação do modelo | 1,0 | `notebooks/04_modelagem.ipynb` executado, `reports/RELATORIO_MODELOS.md`, 6 gráficos em `reports/figuras/` |
| Reprodutibilidade | 1,0 | um comando gera tudo; 28 testes; GitHub Actions roda a cada push |

## Como conferir (10 minutos)

Na raiz, com o ambiente da raiz ativado:

```bash
pip install -r requirements.txt
python -m src.etl.pipeline                 # base_analitica.csv (sai idêntica à do repositório)
python -m src.modelos.treinar_avaliar      # ~1 min → reports/
python -m pytest -q tests                  # 18 testes
```

No protótipo, com o ambiente do protótipo (Python 3.12+):

```bash
cd prototipo
pip install -r requirements.txt pytest
python -m pytest -q tests                  # 10 testes (agente + app)
streamlit run app.py                       # sem Ollama, o app fica igual ao publicado
```

O resumo que deve aparecer no fim do `treinar_avaliar`:

```
Random Forest (teste 2026.1–2026.2): F1 macro 0.729 · recall Crítico 0.529
Regra 'fica onde está':              F1 macro 0.768 · recall Crítico 0.706
Motor do app: erro 2.409 pp com ações × 2.91 sem (17% menos) · correlação efeitos 0.996
K-Means do app: k=4 silhueta 0.458
Ponto fraco se repete: 11% (base comum) · régua: 523 mudam de zona
```

Os números batem exatamente com as versões travadas no `requirements.txt` da raiz. Com versões mais novas do scikit-learn, o Random Forest varia um pouco (por exemplo, F1 0,732 e recall do Crítico 0,647), mas a conclusão não muda: ele continua abaixo da regra "fica onde está".

## O que os números dizem (para a banca)

1. **O motor de ações é o produto.** Com as ações do pacto, o erro de previsão cai 17%, e o motor reencontra os efeitos usados para gerar os dados.
2. **O Random Forest foi avaliado e ficou fora do app.** Ele bate a classe mais comum, mas não bate a regra "fica onde está". A faixa quase não muda de um ciclo para o outro. **KPI 3 (F1 ≥ 0,80) não foi atingido (0,73)**, e isso fica declarado com a decisão tomada.
3. **Ponto fraco só quando se repete.** Na base comum, o indicador mais baixo se repete em só 11% dos casos. Pela regra "3 de 3 ciclos", nenhuma equipe tem ponto fraco defensável hoje.
4. **Régua:** 523 equipes-ciclo mudam de zona entre o Manual e o dicionário. A pendência foi levada ao NIIMA.

## O que mudou no código

- `src/modelos/classificador.py` e `clusterizacao.py` foram **reescritos**. Os anteriores usavam colunas que não existem na base (`cobertura_pre_natal`, `idhm_bairro`…) e não rodavam.
- Novos: `src/indice/regua.py`, `src/recomendacao/ponto_fraco.py`, `src/modelos/treinar_avaliar.py`, `tests/`, `reports/`, `.github/workflows/testes.yml`.
- `prototipo/pulso/agente.py` + 30 linhas no `prototipo/app.py`: redação por IA local, que **só liga se o Ollama estiver rodando na máquina**. No Streamlit Cloud nada muda.

## O que falta (por ordem de importância)

| # | Tarefa | Obrigatório? | Quem | Até |
|---|---|---|---|---|
| 1 | Rodar os comandos acima, conferir o resumo e abrir o PR | **sim** | Nicolas | 20/11 |
| 2 | Conferir o deploy do Streamlit Cloud depois do merge (o app deve abrir igual) | **sim** | Nicolas | 20/11 |
| 3 | Gravar a demo **com** a IA local: `ollama pull qwen2.5:7b`, ligar a chave, clicar em "Redigir para o pacto" em 1 sugestão | não, é bônus | Nicolas | 21/11 |
| 4 | Ligar o motor à base comum (132 equipes) | não: pós-SR2, declarado | Nicolas | depois |

Se o item 3 não der tempo, o vídeo usa a justificativa calculada ("Por quê: …"), que já está em toda sugestão. O deck já fala do catálogo como reserva.
