"""Os três eixos do Recife Monitora, os itens de cada eixo e o catálogo de ações do pacto."""

import numpy as np
import pandas as pd

CICLOS = ["2024 Q1", "2024 Q2", "2024 Q3", "2025 Q1", "2025 Q2", "2025 Q3", "2026 Q1", "2026 Q2"]
PROXIMO_CICLO = "2026 Q3"

EIXOS = {
    "e1": {"titulo": "Eixo 1 · Profissionais", "curto": "Profissionais",
           "fonte": "Autoavaliação das equipes: relações de trabalho, ações e processos"},
    "e2": {"titulo": "Eixo 2 · Cidadãos", "curto": "Cidadãos",
           "fonte": "Pesquisa de satisfação enviada por WhatsApp após a consulta"},
    "e3": {"titulo": "Eixo 3 · Desempenho", "curto": "Desempenho",
           "fonte": "Indicadores de saúde da equipe (SISAB/e-SUS APS), em % da meta atingida"},
}

ITENS = {
    "relacoes": {"eixo": "e1", "nome": "Relações de trabalho"},
    "reuniao": {"eixo": "e1", "nome": "Reunião de equipe regular"},
    "agenda": {"eixo": "e1", "nome": "Agenda organizada"},
    "territorio": {"eixo": "e1", "nome": "Planejamento pelo território"},
    "educacao": {"eixo": "e1", "nome": "Educação permanente"},
    "insumos": {"eixo": "e1", "nome": "Condições de trabalho e insumos"},
    "acesso": {"eixo": "e2", "nome": "Facilidade para ser atendido"},
    "espera": {"eixo": "e2", "nome": "Tempo de espera"},
    "acolhimento": {"eixo": "e2", "nome": "Acolhimento e respeito"},
    "orientacao": {"eixo": "e2", "nome": "Explicações claras"},
    "resolutividade": {"eixo": "e2", "nome": "Problema resolvido"},
    "prenatal": {"eixo": "e3", "nome": "Pré-natal", "meta": 45,
                 "descricao": "Gestantes com 6+ consultas, a 1ª até a 12ª semana"},
    "sifilis_hiv": {"eixo": "e3", "nome": "Sífilis e HIV na gestação", "meta": 60,
                    "descricao": "Gestantes com exames de sífilis e HIV"},
    "vacinacao": {"eixo": "e3", "nome": "Vacinação infantil", "meta": 95,
                  "descricao": "Cobertura de pólio e pentavalente"},
    "hipertensao": {"eixo": "e3", "nome": "Hipertensão", "meta": 50,
                    "descricao": "Hipertensos com pressão aferida no semestre"},
    "diabetes": {"eixo": "e3", "nome": "Diabetes", "meta": 50,
                 "descricao": "Diabéticos com hemoglobina glicada solicitada"},
    "citopatologico": {"eixo": "e3", "nome": "Citopatológico", "meta": 40,
                       "descricao": "Mulheres de 25 a 64 anos com exame em dia"},
}

ITENS_DO_EIXO = {e: [i for i, cfg in ITENS.items() if cfg["eixo"] == e] for e in EIXOS}

ACOES = {
    "busca_gestantes": {
        "titulo": "Busca ativa de gestantes pelos ACS",
        "detalhe": "ACS identificam gestantes no território e garantem a 1ª consulta até a 12ª semana.",
        "responsavel": "Equipe + ACS",
    },
    "teste_rapido": {
        "titulo": "Teste rápido na 1ª consulta de pré-natal",
        "detalhe": "Kits de sífilis e HIV em todos os consultórios e checklist de exames na caderneta.",
        "responsavel": "Enfermagem",
    },
    "vacina_extramuros": {
        "titulo": "Vacinação extramuros e horário estendido",
        "detalhe": "Lista nominal de crianças em atraso, visitas com vacina e sala aberta no fim da tarde.",
        "responsavel": "Sala de vacina + ACS",
    },
    "lista_cronicos": {
        "titulo": "Revisão da lista nominal de crônicos",
        "detalhe": "Revisar hipertensos e diabéticos sem consulta ou exame no semestre e agendar.",
        "responsavel": "Medicina + enfermagem",
    },
    "pa_todo_contato": {
        "titulo": "Aferir a pressão em todo contato",
        "detalhe": "Aferição no acolhimento e nas visitas domiciliares, com registro no e-SUS.",
        "responsavel": "Equipe + ACS",
    },
    "cito_terceiro_turno": {
        "titulo": "Coleta de citopatológico em 3º turno",
        "detalhe": "Horário fixo à noite para mulheres que trabalham, com busca ativa das que estão sem exame.",
        "responsavel": "Enfermagem + ACS",
    },
    "mutirao_sabado": {
        "titulo": "Mutirão de sábado",
        "detalhe": "Dia de mutirão com vacinação e coleta de exames num sábado do ciclo.",
        "responsavel": "Equipe",
    },
    "acesso_avancado": {
        "titulo": "Acesso avançado na agenda",
        "detalhe": "Reservar vagas para o mesmo dia e reduzir agendamentos com semanas de antecedência.",
        "responsavel": "Equipe",
    },
    "acolhimento_risco": {
        "titulo": "Acolhimento com classificação de risco",
        "detalhe": "Escuta inicial em todos os turnos para priorizar quem precisa ser atendido primeiro.",
        "responsavel": "Enfermagem",
    },
    "reuniao_indicadores": {
        "titulo": "Reunião semanal com pauta de indicadores",
        "detalhe": "Encontro fixo da equipe para olhar os dados do ciclo e dividir tarefas.",
        "responsavel": "Equipe",
    },
    "educacao_permanente": {
        "titulo": "Educação permanente com apoio matricial",
        "detalhe": "Encontro mensal de capacitação com o NASF ou especialistas do distrito.",
        "responsavel": "Equipe + distrito",
    },
    "mapa_territorio": {
        "titulo": "Atualizar o mapa do território",
        "detalhe": "ACS revisam famílias e microáreas e marcam no mapa as situações de risco.",
        "responsavel": "ACS",
    },
    "grupo_cronicos": {
        "titulo": "Grupo de educação em saúde para crônicos",
        "detalhe": "Encontros quinzenais com hipertensos e diabéticos sobre alimentação, remédios e exames.",
        "responsavel": "Equipe",
    },
    "retorno_pesquisa": {
        "titulo": "Discutir a pesquisa de satisfação com a equipe",
        "detalhe": "Ler os comentários dos usuários na reunião e combinar uma melhoria por ciclo.",
        "responsavel": "Equipe",
    },
    "reposicao_insumos": {
        "titulo": "Reposição de insumos e manutenção",
        "detalhe": "Levantar o que falta (materiais, equipamentos, estrutura) e pedir ao distrito com prazo.",
        "responsavel": "Gestão distrital",
    },
    "mediacao_conflitos": {
        "titulo": "Rodas de conversa sobre o trabalho em equipe",
        "detalhe": "Encontros mediados pelo apoio institucional para tratar conflitos e divisão de tarefas.",
        "responsavel": "Apoio institucional",
    },
}


def pontuacao_eixo(df: pd.DataFrame, eixo: str) -> pd.Series:
    """Pontuação de 0 a 100 do eixo, como o painel do Recife Monitora devolveria.

    Eixos 1 e 2: média dos itens. Eixo 3: média do percentual da meta atingido (limitado a 100%).
    """
    itens = ITENS_DO_EIXO[eixo]
    if eixo != "e3":
        return df[itens].mean(axis=1)
    partes = [np.minimum(df[i] / ITENS[i]["meta"], 1.0) * 100 for i in itens]
    return sum(partes) / len(partes)


def pontuacoes(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({e: pontuacao_eixo(df, e) for e in EIXOS}, index=df.index)
