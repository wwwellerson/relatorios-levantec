# Arquivo: backend/os_generator.py (com novo formato de nome de arquivo)

from fpdf import FPDF
from datetime import datetime
import os
import sys

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDF_OS(FPDF):
    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, '_________________________', 0, 1, 'C')
        self.cell(0, 5, 'Assinatura do Técnico Responsável', 0, 0, 'C')
        

def gerar_os_pdf(dados_cliente, dados_motor, tipo_servico, descricao_servico):
    
    pdf = PDF_OS(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    # --- AQUI ESTÁ A CORREÇÃO ---
    # Ativamos a quebra de página automática com uma margem inferior de 2.5 cm
    pdf.set_auto_page_break(auto=True, margin=25) 

    # --- Cabeçalho com Logos ---
    logo_jw_path = resource_path('Logo2.png')
    logo_levantec_path = resource_path('Logo.png')
    if os.path.exists(logo_levantec_path):
        pdf.image(logo_levantec_path, x=13, y=12, h=25)
    if os.path.exists(logo_jw_path):
        pdf.image(logo_jw_path, x=135, y=15, h=15)

    pdf.set_font('Arial', '', 12)
    pdf.set_xy(10, 40)
    pdf.cell(0, 8, f"Data da Emissão: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.ln(10)

    # --- Título e Textos Dinâmicos ---
    if tipo_servico == 'instalacao':
        titulo = "Notificação de Instalação de Sistema de Automação"
        data_servico = dados_cliente.get('data_da_instalacao', datetime.now().strftime('%d/%m/%Y'))
        texto_padrao = (
            f"Prezado(a) {dados_cliente.get('nome_cliente', 'Cliente')},\n"
            f"Esta é uma notificação referente à *INSTALAÇÃO DE NOVO SISTEMA DE AUTOMAÇÃO* no motor denominado: {dados_motor.get('descricao_motor', 'N/A')}.\n\n"
            "Nosso sistema foi projetado para otimizar o controle e o desempenho do motor utilizado na irrigação de lavouras de arroz, garantindo maior eficiência energética, confiabilidade nas operações e redução da necessidade de intervenção manual.\n"
            "Durante esta instalação, foram realizados os seguintes procedimentos:"
        )
        texto_final = (
            "O sistema instalado conta com os seguintes recursos:\n"
            "- Monitoramento remoto do funcionamento do motor;\n"
            "- Controle automatizado de liga/desliga com base em horários ou sensores;\n"
            "- Proteção contra subtensão, sobretensão e falta de fase;\n"
            "- Registro de histórico de funcionamento e alertas em tempo real;\n"
            "- Interface amigável via aplicativo ou painel local.\n\n"
            "Certificamo-nos de que todos os testes de funcionamento foram realizados com sucesso e que o sistema está operando conforme os padrões técnicos exigidos para aplicações agrícolas de irrigação por motores trifásicos.\n\n"
            "Caso deseje treinamento adicional ou suporte técnico, nossa equipe está disponível para auxiliá-lo sempre que necessário.\n\n"
            "Agradecemos pela confiança depositada em nossos serviços e tecnologias. Estamos comprometidos em oferecer soluções eficazes para o seu dia a dia no campo.\n\n"
            "Atenciosamente,\nJW Automação de Sistemas\nWellerson Killian"
        )
        # Texto para o nome do arquivo
        tipo_servico_texto_arquivo = "NOVO_SISTEMA"
    else: # Manutenção
        titulo = "Notificação de Manutenção de Sistema de Automação"
        data_servico = datetime.now().strftime('%d/%m/%Y')
        texto_padrao = (
            f"Prezado(a) {dados_cliente.get('nome_cliente', 'Cliente')},\n\n"
            f"Esta é uma notificação referente à *MANUTENÇÃO TÉCNICA* no motor trifásico de irrigação,denominado: {dados_motor.get('descricao_motor', 'N/A')}, e no respectivo sistema de automação agrícola.\n\n"
            "Nosso time técnico executou uma vistoria completa no sistema com o objetivo de assegurar o funcionamento contínuo e eficiente do equipamento, minimizando o risco de falhas durante períodos críticos de irrigação.\n\n"
            "Durante o atendimento, foram realizados os seguintes procedimentos:\n"
            "- Manutenção do sistema de automação\n\n"
            "Todas as informações detalhadas da manutenção e eventuais recomendações seguem abaixo:"
        )
        texto_final = (
            "Agradecemos pela continuidade da parceria e reiteramos nosso compromisso com a confiabilidade e durabilidade do sistema que entregamos. Em caso de dúvidas, estamos à disposição para prestar o devido suporte.\n\n"
            "Atenciosamente,\nJW Automação"
        )
        # Texto para o nome do arquivo
        tipo_servico_texto_arquivo = "MANUTENCAO"
    
    # --- Desenha o Conteúdo do PDF ---
    pdf.set_font('Arial', 'B', 14)
    pdf.multi_cell(0, 8, titulo, 0, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, texto_padrao, 0, 'J')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Detalhes do Serviço Executado:", 0, 1, 'L')
    pdf.set_font('Arial', 'I', 11)
    pdf.multi_cell(0, 6, f'"{descricao_servico}"', 1, 'J')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, texto_final, 0, 'J')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f"Data do Serviço: {data_servico}", 0, 1, 'L')

    # --- GERAÇÃO DO NOME DO ARQUIVO ATUALIZADA ---
    nome_cliente_safe = dados_cliente.get('nome_cliente', 'Cliente',).replace(' ', '_')
    nome_arquivo = f"OS-{nome_cliente_safe}-{tipo_servico_texto_arquivo}.pdf"
    caminho_saida_pdf = os.path.join("reports_generated", nome_arquivo)
    # --- FIM DA ATUALIZAÇÃO ---
    
    pdf.output(caminho_saida_pdf)
    
    return caminho_saida_pdf