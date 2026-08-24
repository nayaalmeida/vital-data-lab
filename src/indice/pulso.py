"""
Cálculo do Pulso da Unidade — índice composto de 0 a 100.

MÉTODO, e a literatura que o sustenta
-------------------------------------
1. Normalização min-max de cada indicador para a escala 0-100. É o método
   predominante nos índices compostos de saúde revisados por Musau et al.
   (2025, Population Health Metrics).

2. Composição por eixos, com os MESMOS PESOS que o Recife Monitora já usa
   (20% / 20% / 60%). Não inventamos uma régua nova: respeitamos a que a
   Secretaria adota e acrescentamos o que ela não tem.

3. Ajuste por contexto socioterritorial, limitado a ±10 pontos. O teto
   existe para o ajuste corrigir a injustiça sem apagar o desempenho.

4. Verificação de correlação antes de compor. Austin et al. (2019, BMC Med
   Res Methodol) mostram que combinar indicadores fracamente correlacionados
   piora a capacidade de ranqueamento: só faz sentido somar indicadores que
   representam o mesmo conceito de qualidade.

LIMITAÇÃO ASSUMIDA: a agregação por média é compensatória — nota alta num
eixo encobre nota baixa em outro. Não eliminamos isso; contornamos com o
motor de recomendação, que aponta sempre a dimensão mais fraca.

Responsável: Cauã Cabral · validação clínica: Danilo Brito
"""

import pandas as pd

# Pesos por eixo — espelham a distribuição de pontos do Recife Monitora.
PESOS_EIXOS = {
    "indicadores_assistenciais": 0.60,
    "autoavaliacao_equipes":     0.20,
    "satisfacao_usuarios":       0.20,
}

INDICADORES_ASSISTENCIAIS = [
    "cobertura_pre_natal",
    "vacinacao_infantil",
    "hipertensos_acompanhados",
    "diabeticos_acompanhados",
    "saude_bucal_atendimentos",
    "citopatologico_coletado",
]

# Variáveis de contexto e o peso de cada uma no ajuste.
CONTEXTO = {"idhm_bairro": 0.6, "saneamento_pct": 0.4}

AJUSTE_MAXIMO = 10.0        # em pontos do índice, para cima ou para baixo

FAIXAS = {
    "Crítico":    (0, 50),
    "Atenção":    (50, 75),
    "Excelência": (75, 100),
}


def normalizar(serie: pd.Series, inverter: bool = False) -> pd.Series:
    """Leva uma métrica para a escala 0-100 por min-max."""
    minimo, maximo = serie.min(), serie.max()
    if maximo == minimo:
        return pd.Series(50.0, index=serie.index)
    normalizada = (serie - minimo) / (maximo - minimo) * 100
    return 100 - normalizada if inverter else normalizada


def verificar_correlacao(df: pd.DataFrame, colunas=None, minimo: float = 0.30):
    """
    Mede a correlação média entre os indicadores que vão compor o índice.

    Devolve (correlacao_media, matriz). Correlação baixa é sinal de alerta:
    ver Austin et al. (2019). O resultado deve ser registrado em
    docs/decisoes_limpeza.md antes de fixar a composição.
    """
    colunas = colunas or INDICADORES_ASSISTENCIAIS
    matriz = df[colunas].corr()
    mascara = pd.DataFrame(
        [[i == j for j in range(len(colunas))] for i in range(len(colunas))],
        index=matriz.index, columns=matriz.columns)
    fora_da_diagonal = matriz.mask(mascara)
    media = fora_da_diagonal.stack().mean()
    if media < minimo:
        print(f"[ALERTA] Correlação média entre indicadores: {media:.2f} "
              f"(abaixo de {minimo}). Ver Austin et al. (2019) — "
              f"compor o índice assim pode ranquear pior que os indicadores isolados.")
    return media, matriz


def ajustar_por_contexto(df: pd.DataFrame) -> pd.Series:
    """
    Devolve o ajuste em pontos, entre -AJUSTE_MAXIMO e +AJUSTE_MAXIMO.

    Territórios mais vulneráveis recebem ajuste positivo; territórios mais
    estruturados, ajuste negativo. O objetivo não é premiar pobreza nem punir
    riqueza: é comparar cada unidade com o que é razoável esperar no seu
    contexto.
    """
    vulnerabilidade = sum(
        normalizar(df[coluna], inverter=True) * peso
        for coluna, peso in CONTEXTO.items()
    )
    # vulnerabilidade vai de 0 (contexto mais favorável) a 100 (mais vulnerável)
    return ((vulnerabilidade - 50) / 50) * AJUSTE_MAXIMO


def classificar(pulso: float) -> str:
    for nome, (piso, teto) in FAIXAS.items():
        if piso <= pulso < teto:
            return nome
    return "Excelência"


def calcular_pulso(df: pd.DataFrame, verificar: bool = True) -> pd.DataFrame:
    """
    Devolve o dataframe com as colunas:
      desempenho_bruto · ajuste_contexto · pulso · classificacao · eixo_mais_fraco
    """
    resultado = df.copy()

    if verificar:
        verificar_correlacao(resultado)

    # Eixo 1 — indicadores assistenciais
    normalizados = pd.DataFrame(
        {c: normalizar(resultado[c]) for c in INDICADORES_ASSISTENCIAIS})
    resultado["eixo_indicadores_assistenciais"] = normalizados.mean(axis=1)

    # Eixos 2 e 3 — já vêm em escala 0-100, mas normalizamos para
    # que a régua seja a mesma dentro do conjunto avaliado.
    resultado["eixo_autoavaliacao_equipes"] = normalizar(resultado["autoavaliacao_equipes"])
    resultado["eixo_satisfacao_usuarios"] = normalizar(resultado["satisfacao_usuarios"])

    resultado["desempenho_bruto"] = sum(
        resultado[f"eixo_{eixo}"] * peso for eixo, peso in PESOS_EIXOS.items())

    resultado["ajuste_contexto"] = ajustar_por_contexto(resultado)
    resultado["pulso"] = (resultado["desempenho_bruto"] +
                          resultado["ajuste_contexto"]).clip(0, 100).round(1)
    resultado["desempenho_bruto"] = resultado["desempenho_bruto"].round(1)
    resultado["ajuste_contexto"] = resultado["ajuste_contexto"].round(1)
    resultado["classificacao"] = resultado["pulso"].apply(classificar)

    # Guarda da compensação: qual eixo puxa a unidade para baixo.
    eixos = [f"eixo_{e}" for e in PESOS_EIXOS]
    resultado["eixo_mais_fraco"] = resultado[eixos].idxmin(axis=1).str.replace("eixo_", "", regex=False)

    return resultado
