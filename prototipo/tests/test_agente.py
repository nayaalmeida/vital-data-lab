from pulso import agente

FATOS, PERMITIDOS = agente.fatos_da_sugestao(
    "Teste rápido na 1ª consulta de pré-natal", "Sífilis e HIV na gestação",
    valor_atual=52.4, efeito_pp=6.3, n_com=41, media_com=5.84, media_sem=1.21)


def test_le_numeros_em_portugues_e_ingles():
    assert agente.numeros_do_texto("subiu de 52% para 58,7%, em 1.234 casos e -2.5 pp") == [52, 58.7, 1234, -2.5]
    assert agente.numeros_do_texto("sem números aqui") == []


def test_fatos_e_numeros_permitidos():
    assert FATOS["valor de hoje"] == "52%" and FATOS["valor esperado no fim do próximo ciclo"] == "59%"
    assert set(PERMITIDOS) == {52, 59, 6.3, 41, 5.8, 1.2}


def test_aprova_texto_que_so_usa_numeros_dos_dados():
    ok, intrusos = agente.verificar("Pode levar o item de 52% para 59% (+6,3 pp), como em 41 equipes.", PERMITIDOS)
    assert ok and intrusos == []


def test_rejeita_numero_inventado():
    ok, intrusos = agente.verificar("A meta é chegar a 80% em 3 meses.", PERMITIDOS)
    assert not ok and intrusos == [80, 3]


def test_redigir_devolve_texto_aprovado():
    texto = "Com o teste rápido na 1ª consulta, sífilis e HIV pode ir de 52% para 59%."
    r = agente.redigir(FATOS, PERMITIDOS, gerar=lambda prompt: texto)
    assert r.ok and r.texto == texto  # o "1" de "1ª consulta" vem do título da ação e é aceito


def test_redigir_descarta_texto_com_numero_inventado():
    r = agente.redigir(FATOS, PERMITIDOS, gerar=lambda prompt: "Isso deve dobrar o indicador para 90%.")
    assert not r.ok and r.texto is None and r.numeros_rejeitados == [90]


def test_redigir_sobrevive_a_modelo_fora_do_ar(monkeypatch):
    monkeypatch.setattr(agente, "OLLAMA_URL", "http://127.0.0.1:9")  # porta fechada
    assert agente.ollama_disponivel() is False
    r = agente.redigir(FATOS, PERMITIDOS)
    assert not r.ok and "indisponível" in r.motivo


def test_conversa_http_com_o_ollama(ollama_falso):
    ollama_falso["resposta"] = "Vale pactuar: o item pode sair de 52% para 59%."
    assert agente.ollama_disponivel() is True
    r = agente.redigir(FATOS, PERMITIDOS)
    assert r.ok
    prompt = ollama_falso["prompts"][0]
    assert "SOMENTE os números" in prompt and "52%" in prompt
