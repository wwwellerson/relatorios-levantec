# Arquivo: backend/pdf_estoque_generator.py

from fpdf import FPDF
from datetime import datetime
import os

class PDF_Estoque(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório de Estoque de Componentes', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_pdf_estoque(dados_estoque: list):
    pdf = PDF_Estoque()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 8)

    # Definição dos cabeçalhos da tabela e suas larguras
    cabecalhos = {
        'modelo_componente': 40,
        'nome_componente': 50,
        'especificacao': 50,
        'quantidade': 20,
        'localizacao': 30
    }

    # Escreve os cabeçalhos
    for campo, largura in cabecalhos.items():
        pdf.cell(largura, 8, campo.replace('_', ' ').title(), 1, 0, 'C')
    pdf.ln()

    # Escreve os dados do estoque
    pdf.set_font('Arial', '', 8)
    for item in dados_estoque:
        for campo, largura in cabecalhos.items():
            valor = str(item.get(campo, ''))
            pdf.cell(largura, 7, valor, 1, 0, 'L')
        pdf.ln()

    # Define o nome e o caminho do arquivo de saída
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"Estoque_Componentes_{timestamp}.pdf"
    caminho_saida_pdf = os.path.join("reports_generated", nome_arquivo)
    os.makedirs("reports_generated", exist_ok=True)
    
    pdf.output(caminho_saida_pdf)
    return caminho_saida_pdf