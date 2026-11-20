"""
Classificador de faixa de ação — Random Forest sobre a base comum do desafio.

PERGUNTA DO MODELO
    "Olhando a equipe NESTE ciclo, em que faixa ela vai estar no PRÓXIMO ciclo?"
    Faixas: Crítico < 500 · Atenção 500–749 · Excelência ≥ 750 (src/indice/regua.py).

POR QUE O PRÓXIMO CICLO
    A faixa do ciclo atual é só a soma dos três eixos cortada em 500 e 750. Um modelo
    treinado para "adivinhar" isso copiaria a soma — acerto de 100% sem valor nenhum
    (vazamento). Prevendo o ciclo seguinte, o modelo vira alerta antecipado: aponta
    quem tende a cair para Crítico antes de cair.

POR QUE RANDOM FOREST
    Dado tabular e pequeno (~1.100 pares equipe×ciclo), sem GPU, e importância das
    variáveis nativa. Rudin (2019): em decisão pública de alto impacto, modelo
    interpretável no lugar de caixa-preta.

COMO É AVALIADO (avaliar)
    1. Teste temporal: treina com os ciclos antigos e testa nos dois mais recentes
       (2026.1 e 2026.2), como seria em produção.
    2. Hiperparâmetros escolhidos por validação cruzada SÓ no treino — o teste não é
       usado para escolher nada.
    3. Validação cruzada agrupada por equipe (GroupKFold, 5 partes): a mesma equipe
       nunca aparece no treino e no teste ao mesmo tempo.
    4. Duas linhas de base honestas: "classe mais comum" e "a equipe fica onde está"
       (persistência). Modelo que não bate a persistência não pode ser vendido como
       previsão.

REGRAS DO PROGRAMA RESPEITADAS
    - Desclassificada não tem faixa (fica fora do treino), nunca vira zero.
    - Bloco A com menos de 30% de resposta não é computado: a nota do bloco vira
      ausente para o modelo, e a flag de validade entra como variável.

Responsável: Nicolas Soares (liderança técnica) · base: pipeline em src/etl/
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline

from src.indice.regua import ORDEM_FAIXAS, faixa_acao

SEMENTE = 42
CICLOS_TESTE = (2026.1, 2026.2)
N_ARVORES = 400

DISTRITOS = [f"Distrito Sanitário {r}" for r in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]]

# Só o que o gestor já tem em mãos no fim do ciclo atual.
VARIAVEIS = (
    ["eixo1_total", "eixo1_bloco_a", "eixo1_bloco_b", "eixo1_bloco_c",
     "taxa_resposta_bloco_a", "bloco_a_valido_num",
     "eixo2_total", "eixo3_total", "pontuacao_final", "delta_pontuacao",
     "grupo", "populacao_adscrita", "n_profissionais", "nivel_maturidade"]
    + [f"IND{i:02d}" for i in range(1, 11)]
    + [f"ATR{i}" for i in range(1, 6)]
)

# Grade pequena e explicável. Escolhida por F1 macro na validação cruzada do treino.
GRADE = [{"min_samples_leaf": folha, "class_weight": peso}
         for folha in (1, 3, 8) for peso in (None, "balanced")]


# ----------------------------------------------------------------------------- dados

def _flag_bloco_a(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.strip().str.lower().isin(["true", "1", "sim"]).astype(int)


def montar_pares(base: pd.DataFrame) -> pd.DataFrame:
    """
    Uma linha por equipe e ciclo, com a faixa do ciclo SEGUINTE como alvo.

    Só entram pares em ciclos consecutivos (2025.3 → 2026.1, por exemplo) em que a
    equipe tem pontuação nos dois. Equipe que pulou um ciclo ou foi desclassificada
    não gera par naquele ponto.
    """
    b = base.copy()
    ordem = {c: i for i, c in enumerate(sorted(b["ciclo"].dropna().unique()))}
    b["ciclo_idx"] = b["ciclo"].map(ordem)
    b = b.sort_values(["codigo_ine", "ciclo_idx"]).reset_index(drop=True)

    b["faixa_atual"] = b["pontuacao_final"].map(faixa_acao)
    b["bloco_a_valido_num"] = _flag_bloco_a(b["bloco_a_valido"])
    # Regra 1 do programa: Bloco A sem quórum não é computado.
    b.loc[b["bloco_a_valido_num"] == 0, "eixo1_bloco_a"] = np.nan

    g = b.groupby("codigo_ine")
    idx_seg, idx_ant = g["ciclo_idx"].shift(-1), g["ciclo_idx"].shift(1)
    b["ciclo_seguinte"] = g["ciclo"].shift(-1)
    b["alvo"] = g["faixa_atual"].shift(-1)
    b["delta_pontuacao"] = np.where(b["ciclo_idx"] - idx_ant == 1,
                                    b["pontuacao_final"] - g["pontuacao_final"].shift(1), np.nan)

    ok = b["faixa_atual"].notna() & b["alvo"].notna() & (idx_seg - b["ciclo_idx"] == 1)
    return b.loc[ok].reset_index(drop=True)


def matriz_X(pares: pd.DataFrame) -> pd.DataFrame:
    """Variáveis numéricas + distrito em colunas 0/1, sempre com as mesmas 8 colunas de distrito."""
    distrito = pd.Categorical(pares["distrito_sanitario"], categories=DISTRITOS)
    dummies = pd.get_dummies(distrito, prefix="ds", dtype=int)
    dummies.index = pares.index
    return pd.concat([pares[VARIAVEIS].astype(float), dummies], axis=1)


# ----------------------------------------------------------------------------- modelo

def novo_modelo(min_samples_leaf: int = 1, class_weight=None, semente: int = SEMENTE) -> Pipeline:
    """Random Forest com imputação pela mediana (o Bloco A sem quórum chega vazio)."""
    return Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("rf", RandomForestClassifier(n_estimators=N_ARVORES, min_samples_leaf=min_samples_leaf,
                                      class_weight=class_weight, random_state=semente, n_jobs=-1)),
    ])


def metricas(real, previsto) -> dict:
    """Acurácia, F1 macro e as duas métricas do erro mais caro: deixar um Crítico passar."""
    real, previsto = np.asarray(real), np.asarray(previsto)
    return {
        "acuracia": round(float(accuracy_score(real, previsto)), 3),
        "f1_macro": round(float(f1_score(real, previsto, average="macro",
                                         labels=ORDEM_FAIXAS, zero_division=0)), 3),
        "recall_critico": round(float(recall_score(real, previsto, labels=["Crítico"],
                                                   average="macro", zero_division=0)), 3),
        "precisao_critico": round(float(precision_score(real, previsto, labels=["Crítico"],
                                                        average="macro", zero_division=0)), 3),
    }


def escolher_hiperparametros(X: pd.DataFrame, y: pd.Series, grupos: pd.Series,
                             semente: int = SEMENTE) -> tuple[dict, pd.DataFrame]:
    """Validação cruzada agrupada por equipe, só com os dados de treino."""
    linhas = []
    for params in GRADE:
        prev = cross_val_predict(novo_modelo(semente=semente, **params), X, y,
                                 groups=grupos, cv=GroupKFold(n_splits=5))
        linhas.append({**params, **metricas(y, prev)})
    tabela = pd.DataFrame(linhas).sort_values(["f1_macro", "recall_critico"], ascending=False)
    melhor = tabela.iloc[0]
    peso = melhor["class_weight"]
    return ({"min_samples_leaf": int(melhor["min_samples_leaf"]),
             "class_weight": None if pd.isna(peso) else peso},
            tabela.reset_index(drop=True))


def treinar(base: pd.DataFrame, semente: int = SEMENTE, **params) -> tuple[Pipeline, list[str]]:
    """Treina com todo o histórico (uso no app). Devolve o modelo e os nomes das variáveis."""
    pares = montar_pares(base)
    X = matriz_X(pares)
    modelo = novo_modelo(semente=semente, **params).fit(X, pares["alvo"])
    return modelo, list(X.columns)


def importancia_variaveis(modelo: Pipeline, nomes: list[str]) -> pd.Series:
    """Importância por impureza (nativa do Random Forest), em ordem decrescente."""
    return (pd.Series(modelo.named_steps["rf"].feature_importances_, index=nomes)
              .sort_values(ascending=False))


# ----------------------------------------------------------------------------- avaliação

def avaliar(base: pd.DataFrame, ciclos_teste=CICLOS_TESTE, semente: int = SEMENTE) -> dict:
    """
    Avaliação completa. Devolve um dicionário com métricas, baselines, matriz de
    confusão, importâncias e os objetos usados (modelo, X e previsões de teste).
    """
    pares = montar_pares(base)
    X, y, grupos = matriz_X(pares), pares["alvo"], pares["codigo_ine"]
    teste = pares["ciclo_seguinte"].round(1).isin([round(c, 1) for c in ciclos_teste])
    if teste.sum() == 0 or (~teste).sum() == 0:
        raise ValueError("Split temporal vazio: confira os ciclos de teste.")

    params, grade = escolher_hiperparametros(X[~teste], y[~teste], grupos[~teste], semente)
    modelo = novo_modelo(semente=semente, **params).fit(X[~teste], y[~teste])
    previsto = modelo.predict(X[teste])
    real = y[teste]

    persistencia = pares.loc[teste, "faixa_atual"]
    classe_comum = np.full(len(real), y[~teste].mode()[0])

    cv_prev = cross_val_predict(novo_modelo(semente=semente, **params), X, y,
                                groups=grupos, cv=GroupKFold(n_splits=5))
    cv_persist = pares["faixa_atual"]

    perm = permutation_importance(modelo, X[teste], real, scoring="f1_macro",
                                  n_repeats=10, random_state=semente, n_jobs=-1)
    imp_perm = pd.Series(perm.importances_mean, index=X.columns).sort_values(ascending=False)

    mudou = persistencia.values != real.values
    return {
        "pergunta": "faixa de ação no próximo ciclo (Crítico < 500 · Atenção 500–749 · Excelência ≥ 750)",
        "n_pares": int(len(pares)),
        "n_equipes": int(pares["codigo_ine"].nunique()),
        "n_treino": int((~teste).sum()),
        "n_teste": int(teste.sum()),
        "ciclos_teste": [float(c) for c in ciclos_teste],
        "distribuicao_teste": real.value_counts().reindex(ORDEM_FAIXAS, fill_value=0).astype(int).to_dict(),
        "hiperparametros": {**params, "n_estimators": N_ARVORES, "random_state": semente},
        "grade_cv_treino": grade.to_dict(orient="records"),
        "random_forest_teste_temporal": metricas(real, previsto),
        "baseline_persistencia": metricas(real, persistencia),
        "baseline_classe_comum": metricas(real, classe_comum),
        "random_forest_cv_por_equipe": metricas(y, cv_prev),
        "persistencia_cv_mesmas_linhas": metricas(y, cv_persist),
        "equipes_que_mudaram_de_faixa_no_teste": int(mudou.sum()),
        "rf_acerto_entre_as_que_mudaram": round(float((previsto[mudou] == real.values[mudou]).mean()), 3)
                                          if mudou.any() else None,
        "matriz_confusao": {"linhas_real": ORDEM_FAIXAS, "colunas_previsto": ORDEM_FAIXAS,
                            "valores": confusion_matrix(real, previsto, labels=ORDEM_FAIXAS).tolist()},
        "matriz_confusao_persistencia": confusion_matrix(real, persistencia, labels=ORDEM_FAIXAS).tolist(),
        "importancia_permutacao_top10": imp_perm.head(10).round(4).to_dict(),
        "importancia_impureza_top10": importancia_variaveis(modelo, list(X.columns)).head(10).round(4).to_dict(),
        # objetos para o notebook (não vão para o JSON)
        "_modelo": modelo, "_X_teste": X[teste], "_real": real, "_previsto": previsto, "_pares": pares,
    }
