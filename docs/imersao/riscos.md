# Matriz de riscos

**Dono:** Naya · publicado também na página *Problema* do site.

| # | Risco | Prob. | Impacto | Dono | Plano B |
|---|---|---|---|---|---|
| R1 | **Dados de autoavaliação e satisfação não chegam a tempo** | Alta | Crítico | Naya | Dataset sintético realista para os dois eixos, rotulado como simulado em todas as telas e slides. O índice e o pipeline seguem válidos; a troca por dado real é substituição de arquivo. Ofício formal à SEAB na semana do Kickoff. |
| R2 | Export do SISAB é manual e trabalhoso | Alta | Médio | Marcela | Recorte piloto de um distrito na primeira semana, para validar o formato antes de escalar. Extração dividida entre duas pessoas e documentada no README. |
| R3 | Chave CNES não casa entre as bases | Média | Alto | Leônidas | Tabela de-para para as divergências; auditar a taxa de casamento na primeira semana e reportá-la como métrica de qualidade. |
| R4 | Poucos ciclos: base pequena para treinar o classificador | Média | Alto | Cauã | Rotulagem por regra de negócio validada pelo analista de domínio, com validação cruzada estratificada. |
| R5 | Sobrecarga do time em novembro | Alta | Médio | Naya | Congelamento de escopo em 06/11. MVP mínimo defensável já definido. |
| R6 | Publicação do dashboard falha na véspera | Baixa | Crítico | Pedro | Primeiro deploy em outubro, com tela mínima. Versões travadas, cópia local e vídeo gravado como último recurso. |
| R7 | **Índice percebido como ranking punitivo** | Média | Alto | Danilo | Governança ética declarada no site e na apresentação. Nunca exibir ranking nominal sem contexto territorial ao lado. |
| R8 | Concentração de papéis na Gestora | Alta | Alto | Naya | Transferir a direção de arte até 15/09. |

## O risco que governa os outros

**R1.** Enquanto o dado real não chega, cada semana parada custa uma semana de
modelagem em novembro. Por isso o plano B do R1 não espera o risco se confirmar:
os dados sintéticos começam a ser preparados em paralelo.
