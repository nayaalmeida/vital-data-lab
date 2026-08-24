# Plano de execução

**Dono:** Naya · publicado também na página *Solução* do site.
As datas são as mesmas do cronograma. Não existe plano paralelo.

## A primeira tarefa de cada um

Nenhuma delas depende do dado real chegar.

| Quem | O que faz | O que entrega |
|---|---|---|
| Leônidas | baixar recorte piloto do SISAB de um distrito e conferir o formato | arquivo em `data/raw/` e o passo a passo no README |
| Marcela | listar todo problema encontrado no recorte piloto | primeiras linhas de `docs/decisoes_limpeza.md` |
| Cauã | testar a fórmula do índice em dez unidades fictícias | primeira versão de `src/indice/pulso.py` |
| Danilo | ler as fichas técnicas dos indicadores e escrever uma frase sobre cada | justificativa clínica dos indicadores |
| Beatriz | desenhar as três telas no papel | foto dos rascunhos no Drive |
| Pedro | clonar, rodar os quatro comandos e publicar uma tela mínima | link de um dashboard vazio, mas no ar |
| Naya | enviar o pedido formal de dados e manter o cronograma | ofício enviado, cronograma sem linha vencida em branco |

## Os cinco blocos

### Bloco 1 · Dados na mão — até 11/09
- Obtenção do conjunto de dados — *Marcela + Leônidas*
- Limpeza com decisões documentadas — *Marcela*
- Integração pela chave CNES, com taxa de casamento medida — *Leônidas*

### Bloco 2 · Entender e mostrar — até 18/09
- Análise exploratória — *Marcela + Cauã*
- Protótipo interativo exploratório — *Pedro + Beatriz*
- Backlog em épicos e histórias — *Naya + Beatriz*

### Marco · SR1 — 24/09

### Bloco 3 · A inteligência — até 23/10
- Seleção e justificativa da técnica — *Cauã*
- Implementação e treino do modelo — *Cauã*
- Avaliação com métricas — *Cauã + Marcela*
- Telas em média fidelidade — *Beatriz*
- Primeiro deploy de validação — *Pedro*

### Bloco 4 · O produto — até 06/11
- Dashboard navegável com as três telas — *Pedro + Beatriz*
- Motor de recomendações — *Cauã + Danilo*
- Teste com usuário e coleta de feedback — *Beatriz + Naya*
- Congelamento de escopo — *Naya*

### Bloco 5 · Fechamento — até 20/11
- Teste de reprodutibilidade ponta a ponta — *Leônidas + Marcela*
- Gestão de custos e fechamento do cronograma — *Naya*
- Ensaio geral e divisão de falas — *time completo*

### Marco · Entrega final — 23/11

## As três telas do dashboard

| Tela | Pergunta que responde |
|---|---|
| Visão geral | onde ir primeiro |
| Detalhe da unidade | por que está assim |
| Recomendações | o que fazer agora |

Ideia que não responde a uma dessas três perguntas não entra no MVP.

## Critério de pronto

1. Está no repositório.
2. Roda na máquina de outra pessoa.
3. Tem uma linha de explicação do que recebe e do que entrega.
4. Está marcada no cronograma, com data real e justificativa se houve atraso.
