"""
Orquestrador do ETL. É este arquivo que o README manda executar.

    python src/etl/pipeline.py

Ordem: extrair -> anonimizar -> limpar -> integrar -> salvar.
A anonimização vem antes da limpeza de propósito: nenhum dado pessoal
deve existir em memória além do estritamente necessário.

Responsável: Leônidas Carvalho (Engenheiro de Dados)
"""

from . import extract, transform, load


def executar():
    print("[1/5] Coletando fontes...")
    # sisab = extract.extrair_sisab()
    # cnes  = extract.extrair_cnes()
    # ibge  = extract.extrair_ibge()
    # terr  = extract.extrair_recife_em_dados()

    print("[2/5] Removendo PII...")
    print("[3/5] Limpando...")
    print("[4/5] Integrando pela chave CNES...")
    print("[5/5] Salvando base analítica...")

    raise NotImplementedError("Implementar conforme as fontes forem liberadas.")


if __name__ == "__main__":
    executar()
