"""
Escrita da base analítica final em data/processed/.

Responsável: Leônidas Carvalho (Engenheiro de Dados)
"""

from pathlib import Path
import pandas as pd

PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"


def salvar_base_analitica(df: pd.DataFrame, nome: str = "base_analitica.parquet") -> Path:
    """Salva a base agregada e anonimizada, pronta para o índice e os modelos."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    destino = PROCESSED / nome
    df.to_parquet(destino, index=False)
    print(f"[OK] Base analítica salva em {destino} — {len(df)} linhas.")
    return destino
