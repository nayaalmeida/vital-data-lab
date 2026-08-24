"""
Coleta dos dados brutos.

Cada fonte tem sua função. Nenhuma transformação acontece aqui:
extract apenas baixa e salva em data/raw/ exatamente como veio.

Responsável: Leônidas Carvalho (Engenheiro de Dados)
"""

from pathlib import Path

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"


def extrair_sisab():
    """
    Indicadores assistenciais do SISAB / e-SUS APS.

    Acesso: sisab.saude.gov.br — Relatórios > Indicadores de Desempenho.
    Export manual e paginado; documentar aqui o passo a passo exato usado,
    para que outra pessoa consiga repetir.

    Saída esperada: data/raw/sisab_<competencia>.csv
    """
    raise NotImplementedError("Documentar o passo a passo do export antes de automatizar.")


def extrair_cnes():
    """
    Cadastro Nacional de Estabelecimentos de Saúde.

    Acesso: cnes.datasus.gov.br e FTP DATASUS (arquivos mensais).
    É a chave de integração de todas as demais bases.

    Saída esperada: data/raw/cnes_<competencia>.csv
    """
    raise NotImplementedError


def extrair_ibge():
    """
    População, IDHM, saneamento e renda por bairro / setor censitário.

    Acesso: API SIDRA do IBGE (JSON).
    Camada de contexto social que torna a comparação entre unidades justa.

    Saída esperada: data/raw/ibge_<agregado>.json
    """
    raise NotImplementedError


def extrair_recife_em_dados():
    """
    Territorialização dos distritos sanitários e indicadores municipais.

    Acesso: portal de dados abertos da Prefeitura do Recife (CKAN).

    Saída esperada: data/raw/recife_distritos.geojson
    """
    raise NotImplementedError
