# Como trabalhar neste repositório

## Antes de começar

```bash
git clone https://github.com/<usuario>/vital-data-lab.git
cd vital-data-lab
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Regras de convivência

**Nunca envie dados brutos para o repositório.** A pasta `data/raw/` está
ignorada pelo Git de propósito. Se o arquivo for necessário para o time, ele vai
para o Drive, e o caminho fica registrado em `docs/fontes_de_dados.md`.

**Nunca envie dado individual de paciente**, em nenhuma circunstância e em
nenhum formato. O tratamento remove colunas com informação pessoal antes de
qualquer análise — ver `src/etl/transform.py` e `docs/lgpd.md`.

**Toda decisão de limpeza vira linha em `docs/decisoes_limpeza.md`.** Correção
feita e não registrada é correção que ninguém consegue auditar.

## Mensagens de commit

Escreva no infinitivo, dizendo o que a mudança faz:

```
adicionar normalização min-max ao cálculo do índice
corrigir junção que perdia unidades sem código INE
documentar decisão de descartar registros sem CNES
```

## Ramos

- `main` — sempre funcional. O que está aqui deve rodar do zero.
- `dev/<seu-nome>` — trabalho em andamento.

Antes de juntar ao `main`, rode o pipeline inteiro e confirme que ele termina
sem erro.

## Definição de pronto

Uma entrega está pronta quando:

1. está no repositório;
2. roda na máquina de outra pessoa;
3. tem uma linha de explicação de o que recebe e o que entrega;
4. está marcada no cronograma, com data real e, se houve atraso, justificativa.
