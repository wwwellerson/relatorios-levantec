# Arquivo: backend/routers/relatorios_os.py (VERSÃO CORRIGIDA)

from fastapi import APIRouter, HTTPException, Response, File, UploadFile, Form, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from twilio.rest import Client
import uuid
import shutil
import os
import pandas as pd

from services import data_service
import pdf_generator
import os_generator

router = APIRouter(
    prefix="/api",
    tags=["Relatórios e OS"]
)

# --- Carrega variáveis de ambiente ---
load_dotenv()

# --- Configurações (E-mail e Twilio) ---
conf_email = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True, MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True, VALIDATE_CERTS=True
)
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")

# --- Modelos Pydantic ---
class OrdemServico(BaseModel):
    id_cliente: int
    id_motor: str
    tipo_servico: str
    descricao_servico: str

# --- Funções de Segurança ---
# AQUI ESTÁ A CORREÇÃO PRINCIPAL: `filename: str` foi mudado para `nome_arquivo: str`
def secure_path(nome_arquivo: str) -> Path:
    """Garante que o caminho do arquivo é seguro e dentro da pasta esperada."""
    caminho = Path("reports_generated") / Path(nome_arquivo).name
    if not caminho.resolve().parent.samefile(Path("reports_generated").resolve()):
        raise HTTPException(status_code=403, detail="Acesso ao arquivo negado.")
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return caminho

# --- Endpoints ---

@router.post("/relatorios")
async def gerar_relatorio_endpoint(id_motor: str = Form(...), arquivo_csv: UploadFile = File(...), tem_vazao: bool = Form(False), tem_nivel: bool = Form(False)):
    caminho_temp = f"uploads/{uuid.uuid4()}_{arquivo_csv.filename}"
    try:
        os.makedirs("uploads", exist_ok=True)
        with open(caminho_temp, "wb") as buffer:
            shutil.copyfileobj(arquivo_csv.file, buffer)
        
        df_brutos = pd.read_csv(caminho_temp, delimiter=';')
        df_registros = data_service.get_clientes_motores_df()
        
        dados_motor = df_registros[df_registros['id_motor'] == id_motor].to_dict('records')
        if not dados_motor:
            raise HTTPException(status_code=404, detail=f"Motor ID {id_motor} não encontrado.")
        
        checkboxes = {'tem_vazao': tem_vazao, 'tem_nivel': tem_nivel}
        caminho_pdf = pdf_generator.gerar_relatorio_final(df_brutos, dados_motor[0], checkboxes, id_motor)
        
        if os.path.exists(caminho_pdf):
            return FileResponse(path=caminho_pdf, media_type='application/pdf', filename=os.path.basename(caminho_pdf))
        else:
            raise HTTPException(status_code=500, detail="O PDF não foi gerado.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha crítica: {str(e)}")
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

@router.post("/ordens-servico")
def criar_ordem_de_servico(os_data: OrdemServico):
    try:
        df_registros = data_service.get_clientes_motores_df()
        filtro = (df_registros['id_cliente'] == os_data.id_cliente) & (df_registros['id_motor'] == os_data.id_motor)
        registro_selecionado = df_registros[filtro].to_dict('records')

        if not registro_selecionado:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
        
        caminho_pdf = os_generator.gerar_os_pdf(
            dados_cliente=registro_selecionado[0],
            dados_motor=registro_selecionado[0],
            tipo_servico=os_data.tipo_servico,
            descricao_servico=os_data.descricao_servico
        )
        return {"mensagem": "OS gerada com sucesso!", "nome_arquivo": os.path.basename(caminho_pdf)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao gerar OS: {str(e)}")

@router.get("/relatorios-salvos")
def get_relatorios_salvos():
    pasta = "reports_generated"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        return []
    
    relatorios = []
    for nome_arquivo_loop in os.listdir(pasta):
        if nome_arquivo_loop.endswith(".pdf"):
            try:
                partes = os.path.splitext(nome_arquivo_loop)[0].split('_')
                info = {"nome_arquivo": nome_arquivo_loop, "tamanho_mb": f"{os.path.getsize(os.path.join(pasta, nome_arquivo_loop)) / (1024*1024):.2f} MB"}
                if partes[0] == 'RELATORIO' and len(partes) > 3:
                    info.update({"tipo": "Relatório Técnico", "cliente": partes[2].replace("-", " "), "motor": partes[3].replace("-", " ")})
                elif partes[0] == 'OS' and len(partes) > 2:
                    info.update({"tipo": "Ordem de Serviço", "cliente": partes[1].replace("-", " "), "motor": "N/A"})
                else:
                    info.update({"tipo": "Documento", "cliente": "Desconhecido", "motor": "N/A"})
                relatorios.append(info)
            except Exception:
                relatorios.append({"nome_arquivo": nome_arquivo_loop, "cliente": "Erro ao ler nome", "motor": ""})
    
    return sorted(relatorios, key=lambda x: x.get('nome_arquivo'), reverse=True)

@router.get("/relatorios-salvos/{nome_arquivo}")
def get_relatorio_especifico(caminho: Path = Depends(secure_path)):
    return FileResponse(path=caminho, media_type='application/pdf', filename=caminho.name)

@router.delete("/relatorios-salvos/{nome_arquivo}")
def excluir_relatorio_especifico(caminho: Path = Depends(secure_path)):
    try:
        os.remove(caminho)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Não foi possível excluir: {e}")

@router.post("/relatorios-salvos/{nome_arquivo}/enviar-email")
async def enviar_relatorio_por_email(caminho_arquivo: Path = Depends(secure_path)):
    try:
        id_motor_extraido = caminho_arquivo.name.split('_')[1]
        df = data_service.get_clientes_motores_df()
        dados_cliente = df[df['id_motor'] == id_motor_extraido].to_dict('records')
        
        if not dados_cliente or not dados_cliente[0].get('email_responsavel'):
            raise HTTPException(status_code=404, detail="E-mail do responsável não encontrado para este registro.")
        
        email_destinatario = dados_cliente[0]['email_responsavel']
        nome_cliente = dados_cliente[0]['nome_cliente']
        
        message = MessageSchema(
            subject=f"Seu Documento Técnico: {caminho_arquivo.name}",
            recipients=[email_destinatario],
            body=f"Olá, {nome_cliente}.\n\nSegue em anexo o documento solicitado.\n\nAtenciosamente,\nSistema de Relatórios.",
            attachments=[str(caminho_arquivo)],
            subtype="plain"
        )
        fm = FastMail(conf_email)
        await fm.send_message(message)
        return {"message": f"Enviado com sucesso para {email_destinatario}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao enviar e-mail: {str(e)}")

@router.post("/relatorios-salvos/{nome_arquivo}/enviar-whatsapp")
async def enviar_relatorio_por_whatsapp(request: Request, caminho_arquivo: Path = Depends(secure_path)):
    try:
        id_motor_extraido = caminho_arquivo.name.split('_')[1]
        df = data_service.get_clientes_motores_df()
        dados_registro = df[df['id_motor'] == id_motor_extraido].to_dict('records')

        if not dados_registro or not dados_registro[0].get('telefone_contato'):
            raise HTTPException(status_code=404, detail="Telefone de contato não encontrado.")

        numero_original = str(dados_registro[0]['telefone_contato']).strip().replace('.0', '')
        telefone_destinatario = f"whatsapp:+55{numero_original}"
        
        nome_cliente = dados_registro[0]['nome_cliente']
        link_download = f"{BACKEND_PUBLIC_URL}/api/relatorios-salvos/{caminho_arquivo.name}"

        corpo_mensagem = (f"Olá, {nome_cliente}! Segue o seu documento técnico.\n\n"
                          f"Acesse o link para visualizar ou baixar:\n{link_download}\n\n"
                          "Atenciosamente,\nEquipe de Relatórios")
        
        twilio_client.messages.create(from_=twilio_number, body=corpo_mensagem, to=telefone_destinatario)
        return {"message": f"WhatsApp enviado para o número finalizado em {telefone_destinatario[-4:]}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao enviar WhatsApp: {str(e)}")