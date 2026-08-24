"""
Motor de recomendação prescritiva.

Regras de negócio determinísticas sobre a saída do modelo. Sem LLM,
de propósito: recomendação em saúde pública precisa ser auditável,
reprodutível e alinhada aos protocolos do SUS — e não pode alucinar.

Toda regra aqui é validada por Danilo Brito antes de entrar.

Responsáveis: Cauã Cabral (implementação) e Danilo Brito (validação)
"""

from dataclasses import dataclass


@dataclass
class Recomendacao:
    unidade: str
    prioridade: str        # "alta" | "média" | "baixa"
    acao: str              # o que fazer, em linguagem de gestão
    motivo: str            # o dado que disparou a recomendação
    indicador: str         # qual indicador está em desvio


# Catálogo de regras. Cada entrada precisa de:
#   - condição objetiva sobre o dado
#   - ação concreta que o gestor consegue executar
#   - justificativa clínica validada
#
# Exemplo do formato esperado (preencher com Danilo Brito):
# {
#   "indicador": "cobertura_pre_natal",
#   "condicao": "abaixo de 20 pontos da mediana do cluster",
#   "prioridade": "alta",
#   "acao": "Priorizar busca ativa de gestantes no território da unidade.",
#   "motivo": "Cobertura de pré-natal {valor}% contra {referencia}% do grupo semelhante.",
# }
REGRAS = []


def gerar(df) -> list[Recomendacao]:
    """Aplica o catálogo de regras e devolve as recomendações por unidade."""
    raise NotImplementedError
