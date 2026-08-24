# Fontes de Dados

Responsável: Marcela Santos (Analista de Dados)

| # | Fonte | O que fornece | Formato | Granularidade | Acesso |
|---|---|---|---|---|---|
| 1 | SISAB / e-SUS APS | Indicadores assistenciais | CSV / XLS | Unidade e equipe | Público — sisab.saude.gov.br |
| 2 | CNES | Cadastro de unidades e equipes | CSV / FTP | Estabelecimento e equipe | Público — cnes.datasus.gov.br |
| 3 | IBGE | População, IDHM, saneamento, renda | CSV / API SIDRA | Bairro e setor censitário | Público — API SIDRA |
| 4 | Recife em Dados | Territorialização e indicadores locais | CSV / GeoJSON | Distrito e bairro | Público — dados abertos do Recife |
| 5 | Recife Monitora | Autoavaliação das equipes e satisfação | a definir | Unidade e equipe | Mediante disponibilização pela SEAB |

## Caminho de integração

```
SISAB (indicadores por INE/CNES)
   └──► CNES (unidade, equipe, endereço, bairro)
          └──► Recife em Dados (bairro → Distrito Sanitário)
                 └──► IBGE (bairro/setor → IDHM, renda, saneamento)
                        └──► PULSO DA UNIDADE (0–100)
```

Chave de junção: **código CNES**, complementado pelo **INE** no nível de equipe.

## Risco aberto

A fonte 5 é a única não pública. Enquanto não for disponibilizada, os dois
eixos correspondentes usam **dados sintéticos, rotulados como simulados em
todas as telas e slides**.
