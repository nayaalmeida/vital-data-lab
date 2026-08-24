"""
Motor de recomendação prescritiva.

Regras de negócio determinísticas sobre a saída do modelo. Sem modelo
generativo, de propósito: recomendação em saúde pública precisa ser auditável,
reprodutível e alinhada aos protocolos do SUS — e não pode alucinar.

A comparação é sempre feita DENTRO DO GRUPO de unidades semelhantes, nunca
contra a média do município. É isso que torna a recomendação justa.

Toda regra aqui precisa de validação de Danilo Brito antes de entrar em
produção. As ações abaixo são propostas iniciais da equipe.

Responsáveis: Cauã Cabral (implementação) · Danilo Brito (validação)
"""

from dataclasses import dataclass, asdict

import pandas as pd

# Desvio, em pontos percentuais abaixo da mediana do grupo, que dispara
# cada nível de prioridade.
LIMIAR_ALTA = 15
LIMIAR_MEDIA = 8


@dataclass
class Recomendacao:
    unidade: str
    distrito: str
    indicador: str
    prioridade: str      # "alta" | "média" | "baixa"
    acao: str
    motivo: str

    def como_dict(self):
        return asdict(self)


# Catálogo de regras: para cada indicador, a ação concreta que o gestor
# consegue executar. O texto é lido pelo gestor — precisa ser acionável.
CATALOGO = {
    "cobertura_pre_natal": {
        "rotulo": "Cobertura de pré-natal",
        "acao": "Priorizar busca ativa de gestantes no território da unidade, "
                "com apoio dos agentes comunitários de saúde.",
    },
    "vacinacao_infantil": {
        "rotulo": "Vacinação infantil",
        "acao": "Organizar campanha de atualização vacinal e revisar as faltas "
                "no calendário das crianças cadastradas.",
    },
    "hipertensos_acompanhados": {
        "rotulo": "Acompanhamento de hipertensos",
        "acao": "Reagendar as consultas de acompanhamento em atraso e revisar "
                "o cadastro de hipertensos da área.",
    },
    "diabeticos_acompanhados": {
        "rotulo": "Acompanhamento de diabéticos",
        "acao": "Revisar o cadastro de diabéticos e organizar grupo de "
                "acompanhamento no território.",
    },
    "saude_bucal_atendimentos": {
        "rotulo": "Atendimentos de saúde bucal",
        "acao": "Verificar disponibilidade de equipe de saúde bucal e "
                "reprogramar a agenda da unidade.",
    },
    "citopatologico_coletado": {
        "rotulo": "Coleta de citopatológico",
        "acao": "Organizar mutirão de coleta e busca ativa das mulheres com "
                "exame em atraso.",
    },
}

EIXOS_NAO_ASSISTENCIAIS = {
    "autoavaliacao_equipes": (
        "Autoavaliação da equipe",
        "Conduzir roda de conversa com a equipe sobre processos de trabalho "
        "antes do próximo ciclo de avaliação.",
    ),
    "satisfacao_usuarios": (
        "Satisfação do usuário",
        "Revisar acolhimento e tempo de espera com a equipe, e ouvir os "
        "usuários sobre o que mais incomoda.",
    ),
}


def _prioridade(desvio: float) -> str | None:
    if desvio >= LIMIAR_ALTA:
        return "alta"
    if desvio >= LIMIAR_MEDIA:
        return "média"
    return None


def gerar(df: pd.DataFrame, max_por_unidade: int = 2) -> pd.DataFrame:
    """
    Devolve as recomendações por unidade, ordenadas por prioridade.

    Exige que o dataframe já tenha as colunas `grupo` (do agrupamento) e
    `eixo_mais_fraco` (do cálculo do índice).
    """
    if "grupo" not in df.columns:
        raise ValueError("Rode src.modelos.clusterizacao.agrupar antes de gerar recomendações.")

    recomendacoes: list[Recomendacao] = []
    medianas = df.groupby("grupo")[list(CATALOGO)].median()

    for _, linha in df.iterrows():
        referencia = medianas.loc[linha["grupo"]]
        desvios = {ind: referencia[ind] - linha[ind] for ind in CATALOGO}
        piores = sorted(desvios.items(), key=lambda item: item[1], reverse=True)

        geradas = 0
        for indicador, desvio in piores:
            if geradas >= max_por_unidade:
                break
            prioridade = _prioridade(desvio)
            if prioridade is None:
                continue
            regra = CATALOGO[indicador]
            recomendacoes.append(Recomendacao(
                unidade=linha["unidade"],
                distrito=linha["distrito"],
                indicador=regra["rotulo"],
                prioridade=prioridade,
                acao=regra["acao"],
                motivo=(f"{regra['rotulo']} em {linha[indicador]:.0f}%, "
                        f"{desvio:.0f} pontos abaixo da mediana das unidades "
                        f"de contexto semelhante ({referencia[indicador]:.0f}%)."),
            ))
            geradas += 1

        # Guarda da compensação: se o índice geral está bom mas um eixo
        # não assistencial é o mais fraco, a recomendação sai mesmo assim.
        eixo = linha.get("eixo_mais_fraco")
        if geradas == 0 and eixo in EIXOS_NAO_ASSISTENCIAIS:
            rotulo, acao = EIXOS_NAO_ASSISTENCIAIS[eixo]
            recomendacoes.append(Recomendacao(
                unidade=linha["unidade"], distrito=linha["distrito"],
                indicador=rotulo, prioridade="baixa", acao=acao,
                motivo=f"{rotulo} é a dimensão mais fraca desta unidade, "
                       f"mesmo com o índice geral em {linha['pulso']:.0f}.",
            ))

    ordem = {"alta": 0, "média": 1, "baixa": 2}
    resultado = pd.DataFrame([r.como_dict() for r in recomendacoes])
    if resultado.empty:
        return resultado
    return (resultado.assign(_o=resultado["prioridade"].map(ordem))
                     .sort_values(["_o", "unidade"])
                     .drop(columns="_o")
                     .reset_index(drop=True))
