"""Configuração comum dos testes: raiz do repositório e protótipo no caminho de import."""
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
for caminho in (RAIZ, RAIZ / "prototipo"):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

BASE = RAIZ / "data" / "processed" / "base_analitica.csv"


@pytest.fixture(scope="session")
def base():
    if not BASE.exists():
        pytest.skip("Rode antes: python -m src.etl.pipeline")
    return pd.read_csv(BASE)
