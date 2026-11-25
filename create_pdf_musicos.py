from pathlib import Path
from fpdf import FPDF
from io import BytesIO

FONT_DIR = Path("C:/Windows/Fonts")
FONT_NORMAL = FONT_DIR / "arial.ttf"
FONT_BOLD = FONT_DIR / "arialbd.ttf"

def criar_pdf_musicos(musicos):
    pdf = FPDF(
        orientation='P',
        unit='mm',
        format='A4'
    )

    if not FONT_NORMAL.exists() or not FONT_BOLD.exists():
        raise FileNotFoundError("Não foi possível encontrar as fontes do sistema.")

    pdf.add_font(family="Arial", style='', fname=str(FONT_NORMAL))
    pdf.add_font(family="Arial", style='B', fname=str(FONT_BOLD))

    pdf.add_page()

    # Título do Relatório
    pdf.set_font("Arial", style='B', size=18)
    pdf.cell(
        w=0, h=15,
        text="Relatorio de Musicos Cadastrados",
        align='C',
        new_x="LMARGIN", new_y="NEXT"
    )

    pdf.ln(5)

    # Subtítulo com contagem
    pdf.set_font("Arial", size=12)
    pdf.cell(
        w=0, h=10,
        text=f"Total de musicas registadas: {len(musicos)}", # ou músicos registados
        new_x="LMARGIN", new_y="NEXT"
    )

    pdf.ln(5)

    # Cabeçalho da Tabela
    pdf.set_font("Arial", style="B", size=10)
    pdf.set_fill_color(220, 230, 241)

    pdf.cell(w=20, h=10, text="ID", border=1, align='C', fill=True)
    pdf.cell(w=100, h=10, text="Nome", border=1, align='C', fill=True)
    pdf.cell(w=70, h=10, text="CPF", border=1, align='C', fill=True, new_x="LMARGIN", new_y="NEXT")

    # Linhas de Dados
    pdf.set_font("Arial", size=10)
    for m in musicos:
        pdf.cell(w=20, h=9, text=str(m['id']), border=1, align='C')
        pdf.cell(w=100, h=9, text=str(m['nome']), border=1, align='L')
        pdf.cell(w=70, h=9, text=str(m['cpf']), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    return BytesIO(pdf_bytes)