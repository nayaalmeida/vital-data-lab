"""
Orquestrador do pipeline de dados do projeto.

Fluxo:
1. Carregamento das bases brutas
2. Tratamento e validação
3. Salvamento das bases tratadas
4. Integração
5. Salvamento da base analítica
"""

from src.etl.extract import carregar_dados
from src.etl.transform import (
    executar_tratamento,
    salvar_bases_tratadas,
)
from src.etl.integrate import (
    integrar,
    salvar_base_analitica,
)


def executar():
    """
    Executa o pipeline completo de preparação dos dados.
    """

    print("[1/5] Carregando bases...")
    bases = carregar_dados()

    for nome, df in bases.items():
        print(f"       {nome}: {df.shape}")

    print("\n[2/5] Tratando bases...")
    bases_tratadas = executar_tratamento(bases)

    for nome, df in bases_tratadas.items():
        print(f"       {nome}: {df.shape}")

    print("\n[3/5] Salvando bases tratadas...")
    salvar_bases_tratadas(bases_tratadas)
    print("       Bases tratadas salvas em data/processed/")

    print("\n[4/5] Construindo base analítica...")
    base_analitica = integrar(bases_tratadas)

    print(f"       Shape: {base_analitica.shape}")
    print(
        "       Duplicados equipe+ciclo:",
        base_analitica.duplicated(
            ["codigo_ine", "ciclo"]
        ).sum()
    )

    print("\n[5/5] Salvando base analítica...")
    caminho = salvar_base_analitica(base_analitica)

    print(f"       Base salva em: {caminho}")

    print("\nPipeline concluído com sucesso.")

    return base_analitica


if __name__ == "__main__":
    executar()