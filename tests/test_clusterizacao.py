import pandas as pd

from src.modelos import clusterizacao


def test_reproduz_os_grupos_de_territorio_do_app():
    from pulso.dados import gerar_base
    from pulso.motor import GRUPOS, atribuir_grupos

    equipes, _, _ = gerar_base()
    app = atribuir_grupos(equipes)
    Z = clusterizacao.padronizar(equipes.assign(r=equipes["renda"]), ["idhm", "saneamento", "r"], em_log=("r",))
    nosso = clusterizacao.agrupar(Z, len(GRUPOS))
    tabela = pd.crosstab(nosso, app.to_numpy())
    assert (tabela.gt(0).sum(axis=1) == 1).all()  # cada grupo nosso cai em um único grupo do app


def test_silhueta_por_k_tem_valores_validos():
    from pulso.dados import gerar_base

    equipes, _, _ = gerar_base()
    Z = clusterizacao.padronizar(equipes, ["idhm", "saneamento"])
    sil = clusterizacao.silhuetas(Z, range(2, 5))
    assert set(sil) == {2, 3, 4} and all(-1 <= v <= 1 for v in sil.values())
