"""Tira os prints das telas do protótipo e monta um PDF e uma galeria em Markdown.

Com o app rodando em http://localhost:8501:
    .venv\\Scripts\\python scripts\\capturar_prints.py

Usa o Microsoft Edge instalado na máquina (não baixa navegador).
"""

import re
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import Page, sync_playwright

URL = "http://localhost:8501"
SAIDA = Path(__file__).resolve().parent.parent / "prints" / "v2"
LARGURA = 1440
ESCALA = 1.5
TITULO = "Pulso da Unidade · protótipo v2"
SUBTITULO = "Motor de sugestões de ações sobre os três eixos do Recife Monitora"

PIVO = ("Na v1, o protótipo criava uma régua própria: o Índice Pulso, de 0 a 100, com a classificação Crítico, "
        "Atenção ou Excelência. Na conversa com o Recife Monitora, ficou claro que a avaliação oficial continua sendo "
        "feita pelos três eixos (profissionais, cidadãos e desempenho) e que o que agrega valor é a recomendação de "
        "ações. Na v2, o índice e as faixas saíram, os três eixos passaram a ser a entrada do sistema, e o produto "
        "virou um motor de sugestões que aprende com os pactos e os resultados de cada ciclo.")

PRINTS = {
    "01-visao-do-ciclo-recife": ("Visão do ciclo · Gestão central",
                                 "Os três eixos do Recife Monitora por distrito e ao longo dos ciclos, os itens mais fracos "
                                 "de cada distrito, as ações com mais retorno e as equipes com maior potencial de avanço."),
    "02-visao-do-ciclo-distrito": ("Visão do ciclo · Gestão distrital",
                                   "O gestor distrital vê os eixos de cada equipe do seu distrito e onde estão os pontos fracos."),
    "03-sugestoes-da-equipe": ("Sugestões da equipe",
                               "Resultado da equipe nos três eixos, comparado com equipes de território parecido, e as "
                               "ações sugeridas para o próximo pacto, com o efeito esperado e a evidência do histórico."),
    "04-pacto-do-ciclo": ("Pacto do ciclo",
                          "As ações escolhidas para o pacto e a projeção dos três eixos no fim do ciclo. O resultado "
                          "real volta para a IA, que é treinada de novo."),
    "05-o-que-a-ia-aprendeu": ("O que a IA aprendeu",
                               "Quanto cada ação mudou cada item no histórico, a melhora da IA a cada ciclo, como o "
                               "motor funciona e o que mudou desde a v1."),
    "06-sugestoes-foco-cidadaos": ("Perfil de equipe · foco no Eixo 2",
                                   "No perfil de equipe, só a própria equipe aparece. Com o foco no Eixo 2 (cidadãos), "
                                   "a ordem das sugestões muda na hora."),
}

CSS_CAPTURA = """
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
"""


def aguardar(page: Page) -> None:
    page.wait_for_timeout(500)
    try:
        page.wait_for_selector('.stApp[data-test-script-state="notRunning"]', timeout=60_000)
    except Exception:
        pass
    page.wait_for_timeout(1500)


def barra_lateral(page: Page):
    return page.locator('[data-testid="stSidebar"]')


def escolher(page: Page, rotulo: str, opcao: str | re.Pattern) -> None:
    page.get_by_role("combobox", name=rotulo).click()
    page.get_by_role("option", name=opcao).first.click()
    aguardar(page)


def aba(page: Page, nome: str) -> None:
    page.get_by_role("tab", name=nome).click()
    aguardar(page)


def capturar(page: Page, nome: str) -> Path:
    page.evaluate("() => document.querySelector('[data-testid=\"stMain\"]').scrollTo(0, 0)")
    altura = page.evaluate(
        "() => Math.ceil(document.querySelector('[data-testid=\"stMainBlockContainer\"]').getBoundingClientRect().height) + 40")
    page.set_viewport_size({"width": LARGURA, "height": max(900, altura)})
    page.wait_for_timeout(1500)
    caminho = SAIDA / f"{nome}.png"
    page.screenshot(path=caminho, full_page=True)
    page.set_viewport_size({"width": LARGURA, "height": 900})
    page.wait_for_timeout(500)
    print("ok", caminho.name)
    return caminho


def tirar_prints() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge")
        page = navegador.new_page(viewport={"width": LARGURA, "height": 900}, device_scale_factor=ESCALA)
        page.goto(URL)
        page.wait_for_selector(".pulso-hero", timeout=180_000)
        page.add_style_tag(content=CSS_CAPTURA)
        aguardar(page)

        capturar(page, "01-visao-do-ciclo-recife")
        aba(page, "Sugestões da equipe")
        capturar(page, "03-sugestoes-da-equipe")
        for _ in range(3):
            page.get_by_role("button", name="Incluir no pacto").first.click()
            aguardar(page)
        aba(page, "Pacto do ciclo")
        capturar(page, "04-pacto-do-ciclo")
        aba(page, "O que a IA aprendeu")
        capturar(page, "05-o-que-a-ia-aprendeu")

        barra_lateral(page).get_by_text("Gestão distrital", exact=True).click()
        aguardar(page)
        escolher(page, "Distrito sanitário", re.compile(r"^DS VIII$"))
        aba(page, "Visão do ciclo")
        capturar(page, "02-visao-do-ciclo-distrito")

        barra_lateral(page).get_by_text("Equipe", exact=True).click()
        aguardar(page)
        escolher(page, "Foco das sugestões", "Eixo 2 · Cidadãos")
        aba(page, "Sugestões")
        capturar(page, "06-sugestoes-foco-cidadaos")
        navegador.close()


def fonte(negrito: bool, tamanho: int):
    nome = "segoeuib.ttf" if negrito else "segoeui.ttf"
    try:
        return ImageFont.truetype(str(Path("C:/Windows/Fonts") / nome), tamanho)
    except OSError:
        return ImageFont.load_default(size=tamanho)


def quebrar(desenho: ImageDraw.ImageDraw, texto: str, f, largura: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        tentativa = f"{atual} {palavra}".strip()
        if desenho.textlength(tentativa, font=f) <= largura:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = palavra
    return linhas + [atual]


def pagina(titulo: str, descricao: str, imagem: Image.Image | None, numero: str = "") -> Image.Image:
    largura = int(LARGURA * ESCALA)
    margem = 90
    rascunho = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f_titulo, f_texto = fonte(True, 60), fonte(False, 34)
    linhas = quebrar(rascunho, descricao, f_texto, largura - 2 * margem)
    altura_cabecalho = 90 + 80 + len(linhas) * 48 + 70
    altura = altura_cabecalho + (imagem.height if imagem else 0)
    pg = Image.new("RGB", (largura, altura), "#F7F3EC")
    d = ImageDraw.Draw(pg)
    d.rectangle([0, 0, largura, altura_cabecalho], fill="#1C1C1C")
    d.rectangle([0, altura_cabecalho - 10, largura, altura_cabecalho], fill="#D9543B")
    if numero:
        d.text((margem, 50), numero, font=fonte(True, 30), fill="#D9543B")
    d.text((margem, 90), titulo, font=f_titulo, fill="#F9F9F9")
    for i, linha in enumerate(linhas):
        d.text((margem, 180 + i * 48), linha, font=f_texto, fill="#EDE6DA")
    if imagem:
        pg.paste(imagem.convert("RGB"), (0, altura_cabecalho))
    return pg


def montar_compilado() -> None:
    hoje = date.today().strftime("%d/%m/%Y")
    capa = pagina(TITULO,
                  f"{SUBTITULO}. Vital Data Lab · Projeto 5, Gestão de TI · CESAR School 2026.2 · prints de {hoje}. "
                  "Dados sintéticos: os números não representam nenhuma equipe real.", None)
    lista = Image.new("RGB", (capa.width, 120 + 70 * len(PRINTS)), "#F7F3EC")
    d = ImageDraw.Draw(lista)
    for i, (titulo, _) in enumerate(PRINTS.values(), start=1):
        d.text((90, 60 + 70 * i), f"{i}.  {titulo}", font=fonte(False, 40), fill="#1C1C1C")
    capa_completa = Image.new("RGB", (capa.width, capa.height + lista.height), "#F7F3EC")
    capa_completa.paste(capa, (0, 0))
    capa_completa.paste(lista, (0, capa.height))

    paginas = [capa_completa, pagina("O que mudou desde a v1", PIVO, None)]
    for i, (nome, (titulo, descricao)) in enumerate(PRINTS.items(), start=1):
        paginas.append(pagina(titulo, descricao, Image.open(SAIDA / f"{nome}.png"), f"{i:02d}"))
    pdf = SAIDA / "pulso-da-unidade-v2-prints.pdf"
    paginas[0].save(pdf, save_all=True, append_images=paginas[1:], resolution=150)
    print("ok", pdf.name)

    galeria = [f"# Prints do protótipo · v2 (motor de sugestões)\n",
               f"Capturados em {hoje} a partir do app rodando localmente. "
               "**Dados sintéticos**: os números não representam nenhuma equipe real.\n",
               f"**O que mudou desde a v1.** {PIVO} Os prints da v1 estão em [`../v1`](../v1/README.md).\n",
               f"O compilado em PDF está em [`{pdf.name}`]({pdf.name}).\n"]
    for i, (nome, (titulo, descricao)) in enumerate(PRINTS.items(), start=1):
        galeria.append(f"## {i}. {titulo}\n\n{descricao}\n\n![{titulo}]({nome}.png)\n")
    (SAIDA / "README.md").write_text("\n".join(galeria), encoding="utf-8")
    print("ok README.md")


if __name__ == "__main__":
    tirar_prints()
    montar_compilado()
