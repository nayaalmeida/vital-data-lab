"""
Classificação do semáforo: Crítico · Atenção · Excelência.

Técnica: Random Forest.

Por que não um modelo mais preciso e opaco: o gestor precisa entender POR QUE
sua unidade foi classificada como crítica. Modelo de caixa-preta é inaceitável
aqui — classificação sem justificativa vira instrumento de punição, o oposto do
propósito do projeto.

Como o alvo é gerado: as faixas do índice, validadas por regra de negócio
(ver docs/produto/indice_pulso.md). O modelo aprende a reproduzir E A EXPLICAR
a regra — é essa explicação que é o produto. Estratégia adotada por causa do
risco R4: poucos ciclos de avaliação disponíveis para rotulagem manual.

Responsável: Cauã Cabral
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

SEMENTE = 42

VARIAVEIS = [
    "cobertura_pre_natal", "vacinacao_infantil", "hipertensos_acompanhados",
    "diabeticos_acompanhados", "saude_bucal_atendimentos", "citopatologico_coletado",
    "autoavaliacao_equipes", "satisfacao_usuarios",
    "idhm_bairro", "saneamento_pct",
]


def preparar(df: pd.DataFrame):
    """Separa variáveis explicativas e alvo."""
    return df[VARIAVEIS], df["classificacao"]


def treinar(X, y, semente: int = SEMENTE) -> RandomForestClassifier:
    modelo = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",     # as faixas são desbalanceadas por natureza
        random_state=semente,
    )
    modelo.fit(X, y)
    return modelo


def avaliar(X, y, semente: int = SEMENTE) -> dict:
    """
    Avaliação honesta: validação cruzada estratificada em 5 partes,
    mais um relatório sobre um conjunto de teste separado.

    O relatório vai para docs/ e para os slides do SR2.
    """
    particoes = StratifiedKFold(n_splits=5, shuffle=True, random_state=semente)
    modelo = RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=3,
        class_weight="balanced", random_state=semente)

    acuracias = cross_val_score(modelo, X, y, cv=particoes, scoring="accuracy")
    f1 = cross_val_score(modelo, X, y, cv=particoes, scoring="f1_macro")

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=semente)
    ajustado = treinar(X_treino, y_treino, semente)
    predito = ajustado.predict(X_teste)

    return {
        "acuracia_media": round(float(acuracias.mean()), 3),
        "acuracia_desvio": round(float(acuracias.std()), 3),
        "f1_macro_medio": round(float(f1.mean()), 3),
        "relatorio": classification_report(y_teste, predito, zero_division=0),
        "matriz_confusao": confusion_matrix(y_teste, predito, labels=sorted(y.unique())),
        "rotulos": sorted(y.unique()),
    }


def importancia_variaveis(modelo, nomes=None) -> pd.Series:
    """
    Peso de cada variável na decisão do modelo, em ordem decrescente.

    É esta função que torna a classificação explicável — e é o que o parceiro
    vai perguntar na validação.
    """
    nomes = nomes or VARIAVEIS
    return (pd.Series(modelo.feature_importances_, index=nomes)
              .sort_values(ascending=False))


def explicar_unidade(modelo, linha: pd.Series, top: int = 3) -> pd.Series:
    """
    Devolve as variáveis que mais pesaram, com o valor da unidade ao lado.

    Serve para a tela de detalhe: o gestor vê o rótulo e, embaixo, o porquê.
    """
    pesos = importancia_variaveis(modelo).head(top)
    return pd.Series({nome: linha[nome] for nome in pesos.index})
