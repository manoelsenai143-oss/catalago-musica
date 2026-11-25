from pathlib import Path
from fpdf import FPDF
from io import BytesIO

FONT_DIR = Path("C:/Windows/Fonts")
FONT_NORMAL = FONT_DIR / "arial.ttf"
FONT_BOLD = FONT_DIR / "arialbd.ttf"

def criar_pdf_musicas_geral(musicas):
    pdf = FPDF(
        orientation='L',
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
        text="Relatorio Geral de Musicas",
        align='C',
        new_x="LMARGIN", new_y="NEXT"
    )

    pdf.ln(5)

    # Subtítulo com contagem
    pdf.set_font("Arial", size=12)
    pdf.cell(
        w=0, h=10,
        text=f"Total de musicas registadas: {len(musicas)}",
        new_x="LMARGIN", new_y="NEXT"
    )

    pdf.ln(5)

    # Cabeçalho da Tabela (Total exato de 277 mm em Paisagem)
    pdf.set_font("Arial", style="B", size=9)
    pdf.set_fill_color(220, 230, 241)

    pdf.cell(w=12, h=10, text="ID", border=1, align='C', fill=True)
    pdf.cell(w=52, h=10, text="Título", border=1, align='C', fill=True)
    pdf.cell(w=45, h=10, text="Artista", border=1, align='C', fill=True)
    pdf.cell(w=95, h=10, text="Álbum", border=1, align='C', fill=True)
    pdf.cell(w=55, h=10, text="Género", border=1, align='C', fill=True)
    pdf.cell(w=18, h=10, text="Dura.", border=1, align='C', fill=True, new_x="LMARGIN", new_y="NEXT")

    # Linhas de Dados com tamanho otimizado
    pdf.set_font("Arial", size=8.5)
    for m in musicas:
        pdf.cell(w=12, h=8, text=str(m['id']), border=1, align='C')
        pdf.cell(w=52, h=8, text=str(m['titulo']), border=1, align='L')
        pdf.cell(w=45, h=8, text=str(m['artista']), border=1, align='L')
        pdf.cell(w=95, h=8, text=str(m['album']), border=1, align='L')
        pdf.cell(w=55, h=8, text=str(m['genero']), border=1, align='L')
        pdf.cell(w=18, h=8, text=str(m['duracao']), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    return BytesIO(pdf_bytes)