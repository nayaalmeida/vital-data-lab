from pathlib import Path

import pandas as pd
import numpy as np

# =============================================================
# PADRONIZAÇÃO DOS DADOS
# =============================================================

def padronizar_dados(bases):
    """
    Padroniza formatos necessários para o tratamento das bases.

    Nesta etapa:
    - os ciclos são convertidos para o padrão AAAA.Q;
    - eixo2_total é convertido para formato numérico,
      considerando valores com vírgula decimal.

    Parameters
    ----------
    bases : dict
        Dicionário contendo os DataFrames do projeto.

    Returns
    -------
    dict
        Cópia das bases com os formatos padronizados.
    """

    bases_padronizadas = {
        nome: df.copy()
        for nome, df in bases.items()
    }

    # =========================================================
    # Padronização da base de equipes
    # =========================================================

    equipes = bases_padronizadas["equipes"]

    # Padronizar tipos de equipe
    mapa_tipo_equipe = {
        "eSF": "eSF",
        "e-SF": "eSF",
        "ESF": "eSF",
        "esf": "eSF",
        " eSF": "eSF",

        "eSB": "eSB",
        "e-SB": "eSB",
        "ESB": "eSB",
        "esb": "eSB",

        "eMulti": "eMulti",
        "EMULTI": "eMulti",
        "e-Multi": "eMulti"
    }

    equipes["tipo_equipe"] = (
    equipes["tipo_equipe"]
    .str.strip()
    .map(mapa_tipo_equipe)
)

    # Padronizar distritos sanitários
    mapa_distritos = {
        "Distrito Sanitário I": "Distrito Sanitário I",
        "DISTRITO SANITÁRIO I": "Distrito Sanitário I",

        "Distrito Sanitário II": "Distrito Sanitário II",
        "DS II": "Distrito Sanitário II",
        "ds ii": "Distrito Sanitário II",

        "Distrito Sanitário III": "Distrito Sanitário III",
        "DS III": "Distrito Sanitário III",

        "Distrito Sanitário IV": "Distrito Sanitário IV",
        "Distrito Sanitario IV": "Distrito Sanitário IV",

        "Distrito Sanitário V": "Distrito Sanitário V",
        "DISTRITO SANITÁRIO V": "Distrito Sanitário V",
        "Distrito Sanitario V": "Distrito Sanitário V",
        "ds v": "Distrito Sanitário V",

        "Distrito Sanitário VI": "Distrito Sanitário VI",
        "DISTRITO SANITÁRIO VI": "Distrito Sanitário VI",

        "Distrito Sanitário VII": "Distrito Sanitário VII",
        "DISTRITO SANITÁRIO VII": "Distrito Sanitário VII",
        "DS VII": "Distrito Sanitário VII",

        "Distrito Sanitário VIII": "Distrito Sanitário VIII"
    }

    equipes["distrito_sanitario"] = (
        equipes["distrito_sanitario"]
        .map(mapa_distritos)
    )

    bases_padronizadas["equipes"] = equipes

    # ---------------------------------------------------------
    # 1. Função auxiliar para padronização do ciclo
    # ---------------------------------------------------------

    def padronizar_ciclo(valor):
        if pd.isna(valor):
            return pd.NA

        ciclo = str(valor).strip()

        # Formato AAAA.Q
        if (
            len(ciclo) == 6
            and ciclo[4] == "."
        ):
            ano = ciclo[:4]
            periodo = ciclo[5]

        # Formato AAAA-Q
        elif (
            len(ciclo) == 6
            and ciclo[4] == "-"
        ):
            ano = ciclo[:4]
            periodo = ciclo[5]

        # Formato AAAAQ
        # Exemplo: 2024Q2
        elif (
            len(ciclo) == 6
            and ciclo[4].upper() == "Q"
        ):
            ano = ciclo[:4]
            periodo = ciclo[5]

        # Formato Q/AAAA
        # Exemplo: 2/2024
        elif (
            len(ciclo) == 6
            and ciclo[1] == "/"
        ):
            periodo = ciclo[0]
            ano = ciclo[2:]

        else:
            return pd.NA

        # Validação do ano e do quadrimestre
        if (
            ano.isdigit()
            and periodo in {"1", "2", "3"}
        ):
            return f"{ano}.{periodo}"

        return pd.NA

    # ---------------------------------------------------------
    # 2. Padronização do ciclo nas bases que possuem essa coluna
    # ---------------------------------------------------------

    for nome in [
        "resultados",
        "eixo3",
        "nps",
        "planos"
    ]:
        if "ciclo" in bases_padronizadas[nome].columns:
            bases_padronizadas[nome]["ciclo"] = (
                bases_padronizadas[nome]["ciclo"]
                .apply(padronizar_ciclo)
            )

    # ---------------------------------------------------------
    # 3. Padronização do eixo2_total
    # ---------------------------------------------------------

    resultados = bases_padronizadas["resultados"]

    resultados["eixo2_total"] = pd.to_numeric(
        resultados["eixo2_total"]
        .astype("string")
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )

    bases_padronizadas["resultados"] = resultados

    # =========================================================
    # Padronização da escala percentual do Eixo 3
    # =========================================================

    eixo3 = bases_padronizadas["eixo3"]

    eixo3["percentual_alcancado"] = pd.to_numeric(
        eixo3["percentual_alcancado"],
        errors="coerce"
    )

    # Valores acima de 1 estão representados na escala 0-100
    mascara_percentual = eixo3["percentual_alcancado"] > 1

    eixo3.loc[
        mascara_percentual,
        "percentual_alcancado"
    ] = (
        eixo3.loc[
            mascara_percentual,
            "percentual_alcancado"
        ] / 100
    )

    bases_padronizadas["eixo3"] = eixo3

    return bases_padronizadas
# =============================================================
# TRATAMENTO DE DUPLICIDADES
# =============================================================

def tratar_duplicidades(bases):
    """
    Trata duplicidades na base de resultados considerando
    a chave lógica codigo_ine + ciclo.

    Quando existem dois registros para a mesma equipe e ciclo,
    é priorizado o registro que possui eixo2_total preenchido.

    Nos demais casos duplicados, mantém-se apenas um registro.

    A função pressupõe que os ciclos já foram padronizados
    anteriormente por padronizar_dados().

    Parameters
    ----------
    bases : dict
        Dicionário contendo os DataFrames do projeto.

    Returns
    -------
    dict
        Cópia das bases após tratamento das duplicidades.
    """

    bases_tratadas = {
        nome: df.copy()
        for nome, df in bases.items()
    }

    resultados = bases_tratadas["resultados"].copy()

    # ---------------------------------------------------------
    # 1. Indicador auxiliar de completude do eixo2_total
    # ---------------------------------------------------------

    resultados["_eixo2_preenchido"] = (
        resultados["eixo2_total"].notna()
    )

    # ---------------------------------------------------------
    # 2. Prioriza registros com eixo2_total preenchido
    # ---------------------------------------------------------

    resultados = resultados.sort_values(
        by=[
            "codigo_ine",
            "ciclo",
            "_eixo2_preenchido"
        ],
        ascending=[
            True,
            True,
            False
        ]
    )

    # ---------------------------------------------------------
    # 3. Remove duplicidades da chave equipe + ciclo
    # ---------------------------------------------------------

    resultados = resultados.drop_duplicates(
        subset=["codigo_ine", "ciclo"],
        keep="first"
    )

    # ---------------------------------------------------------
    # 4. Remove coluna auxiliar
    # ---------------------------------------------------------

    resultados = resultados.drop(
        columns="_eixo2_preenchido"
    )

    # Restaura ordenação pelo índice original
    resultados = resultados.sort_index()

    bases_tratadas["resultados"] = resultados

    return bases_tratadas

# =============================================================
# TRATAMENTO DE VALORES AUSENTES
# =============================================================

def tratar_ausentes(bases):
    """
    Aplica regras relacionadas a valores ausentes e
    consistência das regras de negócio do Recife Monitora.

    As ausências são preservadas quando possuem significado
    dentro das regras de negócio, evitando substituições
    artificiais por zero, média ou mediana.

    Parameters
    ----------
    bases : dict
        Dicionário contendo os DataFrames do projeto.

    Returns
    -------
    dict
        Cópia das bases após aplicação das regras.
    """

    # Cria cópias para não alterar as bases originais
    bases_tratadas = {
        nome: df.copy()
        for nome, df in bases.items()
    }

    resultados = bases_tratadas["resultados"]

    # ---------------------------------------------------------
    # 1. Preparação dos tipos
    # ---------------------------------------------------------

    # Boolean anulável do pandas:
    # permite True, False e <NA>.
    resultados["bloco_a_valido"] = (
        resultados["bloco_a_valido"].astype("boolean")
    )

    # ---------------------------------------------------------
    # 2. Padronização da taxa de resposta do Bloco A
    # ---------------------------------------------------------

    resultados["taxa_resposta_bloco_a"] = pd.to_numeric(
        resultados["taxa_resposta_bloco_a"],
        errors="coerce"
    )

    # Taxas válidas devem estar entre 0 e 1.
    # Valores fora desse intervalo são tratados como ausentes.
    mascara_taxa_invalida = (
        resultados["taxa_resposta_bloco_a"].notna()
        & ~resultados["taxa_resposta_bloco_a"].between(0, 1)
    )

    resultados.loc[
        mascara_taxa_invalida,
        "taxa_resposta_bloco_a"
    ] = np.nan

    # ---------------------------------------------------------
    # 3. Regra de quórum do Bloco A
    # ---------------------------------------------------------
    taxa = resultados["taxa_resposta_bloco_a"]

    # Taxa abaixo de 30% -> Bloco A não válido
    resultados.loc[
        taxa.notna() & (taxa < 0.30),
        "bloco_a_valido"
    ] = False

    # Taxa abaixo de 30% -> Bloco A não recebe pontuação
    resultados.loc[
        taxa.notna()
        & (taxa < 0.30)
        & (resultados["situacao_participacao"] != "Desclassificada"),
        "eixo1_bloco_a"
    ] = 0.0

    # Taxa igual ou superior a 30% -> Bloco A válido
    resultados.loc[
        taxa.notna() & (taxa >= 0.30),
        "bloco_a_valido"
    ] = True

    # Taxa ausente ou inválida -> validade desconhecida
    resultados.loc[
        taxa.isna(),
        "bloco_a_valido"
    ] = pd.NA

    # ---------------------------------------------------------
    # 4. Regra das equipes desclassificadas
    # ---------------------------------------------------------

    mascara_desclassificada = (
        resultados["situacao_participacao"] == "Desclassificada"
    )

    colunas_pontuacao = [
        "eixo1_total",
        "eixo2_total",
        "eixo3_total",
        "pontuacao_final"
    ]

    # Equipes desclassificadas não devem receber nota zero.
    # As pontuações permanecem ausentes.
    resultados.loc[
        mascara_desclassificada,
        colunas_pontuacao
    ] = np.nan

    # ---------------------------------------------------------
    # 5. Classificação sem pontuação final
    # ---------------------------------------------------------

    # Sem pontuação final válida, não deve existir
    # classificação de desempenho.
    resultados.loc[
        resultados["pontuacao_final"].isna(),
        "zona_classificacao"
    ] = pd.NA

    bases_tratadas["resultados"] = resultados

    return bases_tratadas


# =============================================================
# TRATAMENTO DE VALORES INVÁLIDOS / OUTLIERS
# =============================================================

def tratar_outliers(bases):
    """
    Trata valores inválidos de acordo com os limites definidos
    pelas regras de negócio do Recife Monitora.

    Valores apenas estatisticamente extremos não são removidos
    automaticamente. O tratamento é aplicado somente quando
    existem limites conhecidos para a variável.

    Quando a pontuação final é inválida, ela é recalculada
    somente se os três eixos necessários estiverem disponíveis.

    A classificação é recalculada a partir da pontuação final
    válida, garantindo consistência entre os dois campos.

    Parameters
    ----------
    bases : dict
        Dicionário contendo os DataFrames do projeto.

    Returns
    -------
    dict
        Cópia das bases após o tratamento dos valores inválidos.
    """

    bases_tratadas = {
        nome: df.copy()
        for nome, df in bases.items()
    }

    resultados = bases_tratadas["resultados"]

    # ---------------------------------------------------------
    # 1. Conversão das pontuações para formato numérico
    # ---------------------------------------------------------

    colunas_numericas = [
        "eixo1_total",
        "eixo2_total",
        "eixo3_total",
        "pontuacao_final"
    ]

    for coluna in colunas_numericas:
        resultados[coluna] = pd.to_numeric(
            resultados[coluna],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # 2. Identificação de pontuações finais inválidas
    # ---------------------------------------------------------

    # A pontuação final deve estar entre 0 e 1000.
    mascara_pontuacao_invalida = (
        resultados["pontuacao_final"].notna()
        & ~resultados["pontuacao_final"].between(0, 1000)
    )

    # ---------------------------------------------------------
    # 3. Verificação da disponibilidade dos três eixos
    # ---------------------------------------------------------

    eixos_completos = resultados[
        [
            "eixo1_total",
            "eixo2_total",
            "eixo3_total"
        ]
    ].notna().all(axis=1)

    # Registros inválidos que podem ser reconstruídos
    mascara_recalculavel = (
        mascara_pontuacao_invalida
        & eixos_completos
    )

    # ---------------------------------------------------------
    # 4. Recálculo da pontuação final
    # ---------------------------------------------------------

    resultados.loc[
        mascara_recalculavel,
        "pontuacao_final"
    ] = (
        resultados.loc[
            mascara_recalculavel,
            "eixo1_total"
        ]
        + resultados.loc[
            mascara_recalculavel,
            "eixo2_total"
        ]
        + resultados.loc[
            mascara_recalculavel,
            "eixo3_total"
        ]
    )

    # ---------------------------------------------------------
    # 5. Casos que não podem ser reconstruídos
    # ---------------------------------------------------------

    mascara_nao_recalculavel = (
        mascara_pontuacao_invalida
        & ~eixos_completos
    )

    resultados.loc[
        mascara_nao_recalculavel,
        "pontuacao_final"
    ] = np.nan

    # ---------------------------------------------------------
    # 6. Recálculo da classificação
    # ---------------------------------------------------------

    pontuacao = resultados["pontuacao_final"]

    # Limpa a classificação existente para reconstruí-la
    # exclusivamente a partir da pontuação final válida.
    resultados["zona_classificacao"] = pd.NA

    resultados.loc[
        pontuacao.notna() & (pontuacao < 400),
        "zona_classificacao"
    ] = "Insuficiente"

    resultados.loc[
        pontuacao.between(400, 549.999999),
        "zona_classificacao"
    ] = "Crítica"

    resultados.loc[
        pontuacao.between(550, 699.999999),
        "zona_classificacao"
    ] = "Aperfeiçoamento"

    resultados.loc[
        pontuacao.between(700, 849.999999),
        "zona_classificacao"
    ] = "Qualidade"

    resultados.loc[
        pontuacao.notna() & (pontuacao >= 850),
        "zona_classificacao"
    ] = "Excelência"

    bases_tratadas["resultados"] = resultados

    return bases_tratadas

def tratar_integridade_referencial(bases):
    """
    Remove registros sem correspondência na base de equipes.

    A base equipes é utilizada como referência para codigo_ine.
    Registros das demais bases com codigo_ine inexistente em equipes
    são considerados violações de integridade referencial.
    """

    bases_tratadas = {
        nome: df.copy()
        for nome, df in bases.items()
    }

    equipes = bases_tratadas["equipes"]

    ines_validos = set(
        equipes["codigo_ine"].dropna()
    )

    # Bases que possuem codigo_ine
    for nome in ["resultados", "eixo3", "nps", "planos"]:

        df = bases_tratadas[nome]

        if "codigo_ine" in df.columns:
            bases_tratadas[nome] = df.loc[
                df["codigo_ine"].isin(ines_validos)
            ].copy()

    return bases_tratadas

def executar_tratamento(bases):
    """
    Executa o pipeline completo de tratamento das bases.
    """

    bases_tratadas = padronizar_dados(bases)
    bases_tratadas = tratar_duplicidades(
        bases_tratadas
    )

    bases_tratadas = tratar_ausentes(
        bases_tratadas
    )

    bases_tratadas = tratar_outliers(
        bases_tratadas
    )

    bases_tratadas = tratar_integridade_referencial(
        bases_tratadas
    )

    return bases_tratadas
