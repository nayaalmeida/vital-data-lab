"""Base sintética no formato do Recife Monitora: três eixos por equipe, ciclo a ciclo, e os pactos de ações.

Nenhum número aqui representa uma equipe real: os bairros e distritos dão a
geografia, mas contexto, avaliações e pactos são gerados.

O efeito verdadeiro de cada ação (EFEITOS_REAIS) só é usado para gerar os
dados. O motor de sugestões não tem acesso a ele: precisa aprender tudo com o
histórico, como aconteceria com os dados reais.
"""

import numpy as np
import pandas as pd

from .eixos import ACOES, CICLOS, ITENS

SEED = 42

DISTRITOS = {
    "DS I": (0.55, ["Recife", "Santo Amaro", "Boa Vista", "Coelhos", "Ilha Joana Bezerra",
                    "São José", "Cabanga", "Soledade"]),
    "DS II": (0.62, ["Água Fria", "Beberibe", "Campina do Barreto", "Fundão", "Peixinhos", "Arruda",
                     "Bomba do Hemetério", "Alto Santa Terezinha", "Linha do Tiro", "Dois Unidos",
                     "Cajueiro", "Porto da Madeira"]),
    "DS III": (0.45, ["Casa Amarela", "Tamarineira", "Mangabeira", "Alto José do Pinho",
                      "Morro da Conceição", "Alto José Bonifácio", "Santana", "Poço", "Monteiro",
                      "Apipucos", "Dois Irmãos", "Sítio dos Pintos"]),
    "DS IV": (0.47, ["Cordeiro", "Iputinga", "Torrões", "Engenho do Meio", "Várzea", "Caxangá",
                     "Zumbi", "Cidade Universitária", "Madalena", "Prado"]),
    "DS V": (0.60, ["Afogados", "Mustardinha", "Mangueira", "San Martin", "Bongi",
                    "Jardim São Paulo", "Areias", "Barro", "Coqueiral", "Totó", "Curado",
                    "Tejipió", "Sancho", "Jiquiá"]),
    "DS VI": (0.38, ["Boa Viagem", "Pina", "Brasília Teimosa", "Imbiribeira", "Ipsep"]),
    "DS VII": (0.70, ["Vasco da Gama", "Nova Descoberta", "Macaxeira", "Brejo da Guabiraba",
                      "Brejo de Beberibe", "Córrego do Jenipapo", "Guabiraba", "Pau-Ferro",
                      "Alto do Mandu"]),
    "DS VIII": (0.74, ["Ibura", "Jordão", "Cohab"]),
}

UNIDADES_POR_BAIRRO = {
    "Ibura": 4, "Cohab": 4, "Jordão": 2, "Nova Descoberta": 2, "Vasco da Gama": 2,
    "Santo Amaro": 2, "Água Fria": 2, "Beberibe": 2, "Iputinga": 2, "Várzea": 2,
    "Afogados": 2, "Imbiribeira": 2, "Casa Amarela": 2, "Areias": 2, "Brejo da Guabiraba": 2,
}

AJUSTE_VULNERABILIDADE = {
    "Boa Viagem": -0.30, "Poço": -0.40, "Monteiro": -0.25, "Apipucos": -0.20, "Madalena": -0.30,
    "Tamarineira": -0.30, "Prado": -0.20, "Santana": -0.20, "Cidade Universitária": -0.10,
    "Coelhos": 0.30, "Ilha Joana Bezerra": 0.35, "Santo Amaro": 0.20, "Peixinhos": 0.20,
    "Brasília Teimosa": 0.25, "Recife": 0.10,
}

ROMANOS = ["I", "II", "III", "IV"]

# Nível típico de cada item e quanto ele piora em territórios mais vulneráveis.
PERFIL_ITEM = {
    "relacoes": (66, 6), "reuniao": (58, 8), "agenda": (54, 10), "territorio": (50, 10),
    "educacao": (47, 8), "insumos": (57, 14),
    "acesso": (61, 10), "espera": (54, 10), "acolhimento": (80, 4), "orientacao": (75, 6),
    "resolutividade": (69, 8),
    "prenatal": (44, 14), "sifilis_hiv": (58, 12), "vacinacao": (86, 12),
    "hipertensao": (40, 12), "diabetes": (38, 12), "citopatologico": (29, 12),
}

# Ganho verdadeiro (pp por ciclo) de cada ação sobre cada item, quando o item tem
# metade do espaço para crescer. O mutirão é o caso que parece bom e rende pouco.
EFEITOS_REAIS = {
    "busca_gestantes": {"prenatal": 6, "sifilis_hiv": 2},
    "teste_rapido": {"sifilis_hiv": 7, "prenatal": 1},
    "vacina_extramuros": {"vacinacao": 5, "acesso": 2},
    "lista_cronicos": {"hipertensao": 5, "diabetes": 6},
    "pa_todo_contato": {"hipertensao": 6},
    "cito_terceiro_turno": {"citopatologico": 7, "acesso": 2},
    "mutirao_sabado": {"citopatologico": 1.5, "vacinacao": 1},
    "acesso_avancado": {"acesso": 7, "espera": 6, "agenda": 6, "resolutividade": 2},
    "acolhimento_risco": {"espera": 4, "acolhimento": 4, "resolutividade": 2},
    "reuniao_indicadores": {"reuniao": 9, "territorio": 3, "relacoes": 2, "prenatal": 1,
                            "hipertensao": 1, "diabetes": 1},
    "educacao_permanente": {"educacao": 9, "orientacao": 3, "relacoes": 1},
    "mapa_territorio": {"territorio": 8, "prenatal": 2, "vacinacao": 2},
    "grupo_cronicos": {"diabetes": 3, "hipertensao": 2, "orientacao": 4},
    "retorno_pesquisa": {"acolhimento": 3, "orientacao": 3, "relacoes": 1},
    "reposicao_insumos": {"insumos": 10, "relacoes": 2, "resolutividade": 3},
    "mediacao_conflitos": {"relacoes": 9, "reuniao": 2},
}

# O que as equipes acham que cada ação melhora (é o que guia a escolha no pacto).
ALVOS_PERCEBIDOS = {
    **{a: [i for i, v in efeitos.items() if v >= 3] for a, efeitos in EFEITOS_REAIS.items()},
    "mutirao_sabado": ["citopatologico", "vacinacao"],
}

DEPENDE_DE_ACS = {"busca_gestantes", "vacina_extramuros", "mapa_territorio"}


def _unidades(rng) -> pd.DataFrame:
    registros = []
    for distrito, (vuln_distrito, bairros) in DISTRITOS.items():
        for bairro in bairros:
            vuln = float(np.clip(vuln_distrito + AJUSTE_VULNERABILIDADE.get(bairro, 0)
                                 + rng.normal(0, 0.08), 0.02, 0.98))
            idhm = float(np.clip(0.94 - 0.30 * vuln + rng.normal(0, 0.015), 0.58, 0.96))
            saneamento = float(np.clip(96 - 55 * vuln + rng.normal(0, 5), 25, 99))
            renda = float(300 + 4200 * np.exp(-3.0 * vuln) * rng.lognormal(0, 0.12))
            n = UNIDADES_POR_BAIRRO.get(bairro, 1)
            for k in range(n):
                registros.append({
                    "unidade": f"USF {bairro}" + (f" {ROMANOS[k]}" if n > 1 else ""),
                    "bairro": bairro, "distrito": distrito,
                    "idhm": round(idhm, 3), "saneamento": round(saneamento, 1), "renda": round(renda, -1),
                    "vuln": vuln,
                })
    unidades = pd.DataFrame(registros)
    unidades.insert(0, "cnes", [f"99{100 + i * 37:05d}" for i in range(len(unidades))])
    return unidades


def gerar_base(seed: int = SEED) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Retorna (equipes, painel, pactos).

    painel: uma linha por equipe e ciclo, com os itens dos três eixos.
    pactos: as ações que cada equipe assumiu para cada ciclo (a partir do 2º).
    """
    rng = np.random.default_rng(seed)
    unidades = _unidades(rng)

    linhas = []
    for u in unidades.itertuples():
        n_equipes = int(rng.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1]))
        acs_unidade = rng.normal(86 - 28 * u.vuln, 8)
        for k in range(1, n_equipes + 1):
            linhas.append({
                "equipe": f"{u.cnes}-{k:02d}",
                "nome": f"{u.unidade} · Equipe {k}",
                "cnes": u.cnes, "unidade": u.unidade, "bairro": u.bairro, "distrito": u.distrito,
                "idhm": u.idhm, "saneamento": u.saneamento, "renda": u.renda,
                "cobertura_acs": round(float(np.clip(acs_unidade + rng.normal(0, 6), 35, 100)), 1),
                "pessoas_cadastradas": round(float(np.clip(rng.normal(3200 + 1400 * u.vuln, 450), 2000, 5600)), -1),
                "vuln": u.vuln,
            })
    equipes = pd.DataFrame(linhas)
    n = len(equipes)
    itens = list(ITENS)
    acoes = list(ACOES)

    qualidade = rng.normal(0, 1, n)
    nivel = np.column_stack([
        PERFIL_ITEM[i][0] - 2 * PERFIL_ITEM[i][1] * (equipes["vuln"].to_numpy() - 0.5)
        + 5 * qualidade + rng.normal(0, 5, n)
        for i in itens
    ])
    valores = np.clip(nivel + rng.normal(0, 5, nivel.shape), 2, 100)
    acs_mod = 0.5 + (equipes["cobertura_acs"].to_numpy() - 35) / 65

    registros, pactos = [], []
    for t, ciclo in enumerate(CICLOS):
        df = pd.DataFrame(valores.round(1), columns=itens)
        df.insert(0, "t", t)
        df.insert(0, "ciclo", ciclo)
        df.insert(0, "equipe", equipes["equipe"])
        df["respostas_eixo2"] = rng.poisson(55, n)
        registros.append(df)
        if t == len(CICLOS) - 1:
            break

        # Pacto para o próximo ciclo: equipes tendem a escolher ações para os itens mais fracos.
        efeito = np.zeros_like(valores)
        for e in range(n):
            lacuna = np.array([
                np.mean([(PERFIL_ITEM[i][0] - valores[e, itens.index(i)]) / 15 for i in ALVOS_PERCEBIDOS[a]])
                for a in acoes
            ])
            pesos = np.exp(1.2 * lacuna)
            escolhidas = rng.choice(len(acoes), size=int(rng.choice([2, 3, 4], p=[0.35, 0.4, 0.25])),
                                    replace=False, p=pesos / pesos.sum())
            for ia in escolhidas:
                a = acoes[ia]
                pactos.append({"equipe": equipes.at[e, "equipe"], "ciclo": CICLOS[t + 1], "acao": a})
                execucao = rng.uniform(0.5, 1.2) * (acs_mod[e] if a in DEPENDE_DE_ACS else 1.0)
                for i, ganho in EFEITOS_REAIS[a].items():
                    j = itens.index(i)
                    folga = np.clip((100 - valores[e, j]) / 50, 0.2, 1.6)
                    efeito[e, j] += ganho * folga * execucao

        valores = np.clip(valores + 0.35 * (nivel - valores) + efeito + rng.normal(0, 2.5, valores.shape), 2, 100)

    painel = pd.concat(registros, ignore_index=True)
    return equipes.drop(columns="vuln"), painel, pd.DataFrame(pactos)
