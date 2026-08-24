"""
Gerador de base sintética — PLANO B DO RISCO R1.

Enquanto a SEAB não disponibiliza os dados dos eixos de autoavaliação e
satisfação, o projeto trabalha com uma base SIMULADA. Nada aqui é dado
real: os valores são sorteados a partir de distribuições plausíveis, com
semente fixa para que todo mundo gere exatamente a mesma base.

A troca por dado real é substituição de arquivo, não retrabalho: a base
gerada aqui tem exatamente as mesmas colunas que a base analítica real
terá ao fim do ETL.

    python -m src.dados_sinteticos.gerar

Responsável: Cauã Cabral · validação das faixas: Danilo Brito
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEMENTE = 42
N_EQUIPES = 182          # nº de eSF que participaram dos ciclos de 2023
SAIDA = Path("data/processed/base_analitica_SIMULADA.csv")

DISTRITOS = [f"Distrito Sanitário {n}" for n in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]]

# Indicadores assistenciais e a faixa plausível de cobertura (%).
# As faixas foram escolhidas para produzir variação suficiente para
# testar o índice — NÃO representam o desempenho real da rede.
INDICADORES = {
    "cobertura_pre_natal":          (35, 95),
    "vacinacao_infantil":           (45, 98),
    "hipertensos_acompanhados":     (25, 90),
    "diabeticos_acompanhados":      (25, 88),
    "saude_bucal_atendimentos":     (20, 85),
    "citopatologico_coletado":      (30, 92),
}


def gerar(semente: int = SEMENTE, n: int = N_EQUIPES) -> pd.DataFrame:
    """Devolve a base analítica simulada, uma linha por equipe."""
    rng = np.random.default_rng(semente)

    # Contexto socioterritorial (fonte real seria o IBGE).
    idhm = np.clip(rng.normal(0.68, 0.09, n), 0.42, 0.92)
    saneamento = np.clip(idhm * 100 + rng.normal(0, 8, n), 25, 99)

    # Territórios mais vulneráveis tendem a ter desempenho menor —
    # é justamente esse efeito que o ajuste por contexto neutraliza.
    efeito_contexto = (idhm - idhm.mean()) * 40

    # Qualidade latente da equipe: uma equipe bem organizada tende a ir bem
    # em VÁRIOS indicadores ao mesmo tempo. Sem esse fator os indicadores
    # ficariam independentes entre si, e Austin et al. (2019) mostram que
    # compor um índice com indicadores não correlacionados ranqueia pior
    # que os indicadores isolados. A base simulada precisa reproduzir essa
    # correlação para ser um teste honesto do índice.
    qualidade_equipe = rng.normal(0, 14, n)

    dados = {
        "codigo_cnes": [f"{2000000 + i * 7:07d}" for i in range(n)],
        "codigo_ine":  [f"{9000000 + i * 3:07d}" for i in range(n)],
        "unidade":     [f"USF {i + 1:03d}" for i in range(n)],
        "equipe":      [f"eSF {i + 1:03d}" for i in range(n)],
        "distrito":    rng.choice(DISTRITOS, n),
        "idhm_bairro": np.round(idhm, 3),
        "saneamento_pct": np.round(saneamento, 1),
        "populacao_adscrita": rng.integers(2200, 4800, n),
    }

    for nome, (piso, teto) in INDICADORES.items():
        centro = (piso + teto) / 2
        amplitude = (teto - piso) / 2
        ruido = rng.normal(0, amplitude / 3, n)          # variação própria do indicador
        base = centro + qualidade_equipe + efeito_contexto + ruido
        dados[nome] = np.round(np.clip(base, 0, 100), 1)

    # Eixos que só existem dentro do Recife Monitora.
    dados["autoavaliacao_equipes"] = np.round(np.clip(
        70 + qualidade_equipe * 0.7 + efeito_contexto * 0.4 + rng.normal(0, 7, n), 0, 100), 1)
    dados["satisfacao_usuarios"] = np.round(np.clip(
        74 + qualidade_equipe * 0.5 + efeito_contexto * 0.3 + rng.normal(0, 8, n), 0, 100), 1)

    df = pd.DataFrame(dados)
    df.insert(0, "origem_dado", "SIMULADO")     # marca que acompanha o dado até a tela
    return df


def salvar(df: pd.DataFrame, caminho: Path = SAIDA) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8")
    return caminho


if __name__ == "__main__":
    df = gerar()
    destino = salvar(df)
    print(f"[SIMULADO] {len(df)} equipes geradas em {destino}")
    print(df.head(3).to_string(index=False))
