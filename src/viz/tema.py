"""
Paleta e template visual do Vital Data Lab.

Todo gráfico do projeto importa daqui. Nenhuma cor é escrita à mão
dentro de um notebook ou do app — se a identidade mudar, muda só aqui.

Responsável: Beatriz Amaral (UI/UX) e Marcela Santos (Analista de Dados)
"""

PALETA = {
    "ambar":     "#E8A23D",
    "terracota": "#D9543B",
    "marrom":    "#7A3B2E",
    "mostarda":  "#C9883A",
    "bege":      "#EDE6DA",
    "verde":     "#5A8A4A",
}

# Semáforo do Pulso da Unidade
SEMAFORO = {
    "Excelência": PALETA["verde"],
    "Atenção":    PALETA["ambar"],
    "Crítico":    PALETA["terracota"],
}

# Escala sequencial assinatura (bege -> marrom, passando por âmbar e terracota)
ESCALA_PULSO = ["#EDE6DA", "#C9883A", "#E8A23D", "#D9543B", "#7A3B2E"]

# Sequência categórica para séries múltiplas
SEQUENCIA = [
    PALETA["terracota"], PALETA["ambar"], PALETA["verde"],
    PALETA["marrom"], PALETA["mostarda"],
]


def aplicar_tema():
    """Registra o template do Vital Data Lab no Plotly e o define como padrão."""
    import plotly.graph_objects as go
    import plotly.io as pio

    pio.templates["vitaldatalab"] = go.layout.Template(
        layout=dict(
            font=dict(family="Montserrat, sans-serif", size=13, color=PALETA["marrom"]),
            paper_bgcolor=PALETA["bege"],
            plot_bgcolor=PALETA["bege"],
            colorway=SEQUENCIA,
            title=dict(font=dict(size=18, color="#3B1E17")),
            xaxis=dict(gridcolor="#D6C8B4", zerolinecolor="#D6C8B4"),
            yaxis=dict(gridcolor="#D6C8B4", zerolinecolor="#D6C8B4"),
            margin=dict(l=50, r=25, t=55, b=45),
        )
    )
    pio.templates.default = "vitaldatalab"
