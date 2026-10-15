# Como trabalhar neste repositório

Este documento reúne as regras básicas para manter o projeto reproduzível, organizado e auditável.

---

## Antes de começar

Clone o repositório:

```bash
git clone https://github.com/nayaalmeida/vital-data-lab.git
cd vital-data-lab
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

---

## Dados

As bases atualmente utilizadas em `data/raw/` são as bases sintéticas fornecidas para o desenvolvimento acadêmico do projeto.

Não altere manualmente os arquivos originais.

O fluxo esperado é:

```text
data/raw/
    ↓
Extract
    ↓
Transform
    ↓
Integrate
    ↓
Load
    ↓
data/processed/
```

Qualquer correção deve ser implementada no código de tratamento, e não diretamente no CSV original.

### Dados que nunca devem entrar no repositório

**Nunca envie dados individuais de pacientes**, informações pessoais sensíveis ou qualquer base não autorizada.

O projeto atual trabalha com dados sintéticos e agregados por equipe/unidade.

Qualquer nova fonte deve ter sua origem, finalidade e forma de utilização documentadas antes de ser incorporada ao projeto.

---

## Decisões de tratamento

Toda decisão relevante de tratamento deve estar registrada no código e, quando aplicável, na documentação do projeto.

Uma correção feita manualmente e não documentada não é considerada parte do pipeline reproduzível.

As bases originais devem permanecer preservadas em `data/raw/`.

---

## Pipeline

O pipeline principal pode ser executado com:

```bash
python -m src.etl.pipeline
```

Antes de enviar alterações relacionadas aos dados, execute o pipeline completo e confirme que ele termina sem erro.

Também confira se a base analítica mantém:

- uma observação por equipe e ciclo;
- ausência de duplicidades nessa chave;
- integridade entre as bases utilizadas na integração.

---

## Notebooks

Os notebooks oficiais são:

```text
01_entendimento_dados.ipynb
02_preparacao_dados.ipynb
03_analise_exploratoria.ipynb
04_modelagem.ipynb
```

Ao modificar um notebook:

1. reinicie o kernel;
2. execute todas as células em ordem;
3. confirme que nenhuma célula apresenta erro;
4. salve o notebook;
5. confira o `git status` antes do commit.

Um notebook não deve depender de variáveis criadas manualmente em uma execução anterior.

---

## Organização do código

As responsabilidades do pipeline estão separadas em:

```text
src/etl/extract.py
src/etl/transform.py
src/etl/integrate.py
src/etl/load.py
src/etl/pipeline.py
```

Evite duplicar responsabilidades entre módulos.

Por exemplo:

- leitura das bases → `extract.py`;
- tratamento e validação → `transform.py`;
- construção da base analítica → `integrate.py`;
- escrita dos arquivos processados → `load.py`;
- orquestração → `pipeline.py`.

---

## Branches

A branch `main` deve permanecer funcional.

Para alterações relevantes, crie uma branch específica antes de modificar o projeto.

Exemplos:

```bash
git switch -c feat/nova-funcionalidade
```

ou:

```bash
git switch -c refactor/nome-da-refatoracao
```

Antes do merge:

1. atualize sua branch quando necessário;
2. execute o pipeline;
3. execute os notebooks afetados;
4. confira o `git status`;
5. abra um Pull Request;
6. descreva o que foi alterado e como foi validado.

---

## Commits

Use mensagens curtas que descrevam a alteração realizada.

Exemplos:

```text
feat: adiciona análise dos indicadores por ciclo
fix: corrige tratamento de registros duplicados
refactor: separa integração e carga do pipeline
docs: atualiza documentação das bases utilizadas
```

Evite mensagens genéricas como:

```text
alterações
ajustes
teste
coisas novas
```

---

## Antes de fazer commit

Confira:

```bash
git status
```

e:

```bash
git diff
```

Garanta que arquivos temporários, ambientes virtuais, caches ou alterações não relacionadas não estejam sendo enviados.

---

## Definição de pronto

Uma alteração está pronta quando:

1. está implementada no código ou notebook correto;
2. roda do início ao fim;
3. não depende de estado anterior da máquina ou do notebook;
4. possui uma explicação clara do que recebe e do que entrega;
5. preserva os dados originais;
6. não introduz dados individuais ou não autorizados;
7. foi testada antes do Pull Request;
8. está documentada quando altera uma decisão metodológica ou de tratamento.

---

## Índice e modelagem

A metodologia do Pulso da Unidade e os componentes de classificação, agrupamento e recomendação estão em revisão para adequação às bases utilizadas no projeto.

Alterações nesses componentes devem ser feitas somente após a definição metodológica correspondente estar alinhada e documentada.

Não introduza variáveis, fontes externas, pesos ou regras que não estejam definidos e justificados na metodologia do projeto.