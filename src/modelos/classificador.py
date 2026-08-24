"""
Classificação do semáforo: Crítico · Atenção · Excelência.

Técnica escolhida: Random Forest.

Por que não um modelo mais preciso e opaco: o gestor precisa entender
POR QUE sua unidade foi classificada como crítica. Modelo de caixa-preta
é inaceitável aqui — classificação sem justificativa vira instrumento de
punição, o oposto do propósito do projeto.

Responsável: Cauã Cabral (Cientista de Dados)
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, confusion_matrix

SEMENTE = 42   # fixa para que o resultado seja reproduzível


def treinar(X, y):
    """Treina o classificador e devolve o modelo ajustado."""
    raise NotImplementedError


def avaliar(modelo, X, y):
    """
    Avaliação com validação cruzada estratificada.

    Reportar: acurácia, precisão, recall, F1 e matriz de confusão.
    O relatório vai para docs/ e para os slides do SR2.
    """
    raise NotImplementedError


def importancia_variaveis(modelo, nomes_colunas):
    """
    Devolve o peso de cada variável na decisão do modelo.

    É esta função que torna a classificação explicável — e é o que o
    parceiro vai perguntar na validação.
    """
    raise NotImplementedError
