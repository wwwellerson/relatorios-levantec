# Arquivo: backend/main.py (Versão estável completa, sem login e sem roteadores)

from fastapi import FastAPI, HTTPException, Response, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from twilio.rest import Client
import pandas as pd
import uuid
from typing import Optional, List
from datetime import datetime
import shutil
import os
import io
import numpy as np

# Importa nossos módulos de lógica
import analises
import pdf_generator
import pdf_estoque_generator
import os_generator

# Carrega as variáveis do arquivo .env
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

# --- INICIALIZAÇÃO DO FASTAPI ---
app = FastAPI(title="API do Sistema de Relatórios", version="2.0")

# --- Configuração do CORS ---
origins = ["http://localhost:3000", "http://192.168.1.9:3000"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"], expose_headers=["Content-Disposition"],
)

# --- MODELOS DE DADOS Pydantic ---
DTYPE_MAP = {
    'id_cliente': 'Int64', 'nome_cliente': 'str', 'id_motor': 'str', 'descricao_motor': 'str',
    'local_instalacao': 'str', 'corrente_nominal': 'float64', 'potencia_cv': 'float64',
    'tipo_conexao': 'str', 'tensao_nominal_v': 'float64', 'grupo_tarifario': 'str',
    'telefone_contato': 'str', 'email_responsavel': 'str', 'data_da_instalacao': 'str',
    'id_esp32': 'str', 'observacoes': 'str'
}
class Motor(BaseModel):
    id_cliente: int; nome_cliente: str; descricao_motor: str
    local_instalacao: Optional[str] = None; corrente_nominal: Optional[float] = None; potencia_cv: Optional[float] = None
    tipo_conexao: Optional[str] = None; tensao_nominal_v: Optional[float] = None; grupo_tarifario: Optional[str] = None
    telefone_contato: Optional[str] = None; email_responsavel: Optional[str] = None
    data_da_instalacao: Optional[str] = None; id_esp32: Optional[str] = None; observacoes: Optional[str] = None

class Componente(BaseModel):
    modelo_componente: str; nome_componente: str
    especificacao: Optional[str] = None; quantidade: int; localizacao: Optional[str] = None

class OrdemServico(BaseModel):
    id_cliente: int; id_motor: str; tipo_servico: str; descricao_servico: str

# --- ENDPOINTS DA API ---

@app.get("/")
def ler_raiz():
    return {"mensagem": "Servidor do sistema de relatórios está online!"}

# --- Módulo de Estoque ---
@app.post("/api/estoque", tags=["Estoque"])
def adicionar_ou_atualizar_estoque(componente: Componente):
    arquivo_estoque = "estoque_componentes.csv"
    try:
        try: df = pd.read_csv(arquivo_estoque)
        except FileNotFoundError: df = pd.DataFrame(columns=['modelo_componente', 'nome_componente', 'especificacao', 'quantidade', 'localizacao', 'data_ultima_atualizacao'])
        df['modelo_componente'] = df['modelo_componente'].astype(str)
        componente_existente = df[df['modelo_componente'] == componente.modelo_componente]
        if not componente_existente.empty:
            indice = componente_existente.index[0]
            df.loc[indice, 'quantidade'] += componente.quantidade
            df.loc[indice, 'data_ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mensagem = f"Estoque do componente '{componente.modelo_componente}' atualizado."
        else:
            novo_componente_dict = componente.dict()
            novo_componente_dict['data_ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            novo_df = pd.DataFrame([novo_componente_dict])
            df = pd.concat([df, novo_df], ignore_index=True)
            mensagem = f"Novo componente '{componente.modelo_componente}' adicionado ao estoque."
        df.to_csv(arquivo_estoque, index=False)
        return {"mensagem": mensagem}
    except Exception as e: raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

@app.get("/api/estoque", tags=["Estoque"])
def get_estoque():
    try:
        df = pd.read_csv("estoque_componentes.csv")
        return df.fillna("").to_dict('records')
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/estoque/{modelo_original}", tags=["Estoque"])
def atualizar_componente(modelo_original: str, componente_editado: Componente):
    arquivo_estoque = "estoque_componentes.csv"
    try:
        df = pd.read_csv(arquivo_estoque)
        df['modelo_componente'] = df['modelo_componente'].astype(str)
        indice = df.index[df['modelo_componente'] == modelo_original].tolist()
        if not indice: raise HTTPException(status_code=404, detail="Componente original não encontrado.")
        indice = indice[0]
        dados_novos = componente_editado.dict()
        for chave, valor in dados_novos.items():
            df.loc[indice, chave] = valor
        df.loc[indice, 'data_ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.to_csv(arquivo_estoque, index=False)
        return {"mensagem": f"Componente '{modelo_original}' atualizado com sucesso."}
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Arquivo de estoque não encontrado.")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/estoque/{modelo_componente}", tags=["Estoque"])
def remover_componente(modelo_componente: str):
    arquivo_estoque = "estoque_componentes.csv"
    try:
        df = pd.read_csv(arquivo_estoque)
        df['modelo_componente'] = df['modelo_componente'].astype(str)
        if modelo_componente not in df['modelo_componente'].values: raise HTTPException(status_code=404, detail="Componente não encontrado")
        df_atualizado = df[df['modelo_componente'] != modelo_componente]
        df_atualizado.to_csv(arquivo_estoque, index=False)
        return Response(status_code=204)
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Arquivo de estoque não encontrado")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/estoque/exportar-pdf", tags=["Estoque"])
def exportar_estoque_pdf():
    try:
        df = pd.read_csv("estoque_componentes.csv")
        dados_lista = df.to_dict('records')
        caminho_pdf = pdf_estoque_generator.gerar_pdf_estoque(dados_lista)
        if os.path.exists(caminho_pdf):
            return FileResponse(path=caminho_pdf, media_type='application/pdf', filename=os.path.basename(caminho_pdf))
        else: raise HTTPException(status_code=500, detail="O arquivo PDF de estoque não foi gerado.")
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Arquivo de estoque não encontrado.")
    except Exception as e: raise HTTPException(status_code=500, detail=f"Falha crítica: {str(e)}")

# --- Módulo de Clientes e Motores ---
@app.get("/api/clientes", tags=["Clientes e Motores"])
def get_clientes():
    try:
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP, sep=None, engine='python')
        return df[['id_cliente', 'nome_cliente']].dropna().drop_duplicates(subset=['id_cliente']).to_dict('records')
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/registros", tags=["Clientes e Motores"])
def get_todos_os_registros():
    try:
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP, sep=None, engine='python')
        return df.fillna("").to_dict('records')
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clientes/{id_cliente}/motores", tags=["Clientes e Motores"])
def get_motores_por_cliente(id_cliente: int):
    try:
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP, sep=None, engine='python')
        return df[df['id_cliente'] == id_cliente][['id_motor', 'descricao_motor']].to_dict('records')
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/motores", tags=["Clientes e Motores"])
def adicionar_motor(motor: Motor):
    try:
        novo_motor_dict = motor.dict()
        novo_motor_dict['id_motor'] = str(uuid.uuid4())[:8]
        try: df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP, sep=None, engine='python')
        except FileNotFoundError: df = pd.DataFrame(columns=list(DTYPE_MAP.keys()) + ['id_motor'])
        novo_df = pd.DataFrame([novo_motor_dict])
        df_atualizado = pd.concat([df, novo_df], ignore_index=True)
        df_atualizado.to_csv("clientes_motores.csv", index=False)
        return {"mensagem": "Registro adicionado com sucesso!", "dados": novo_motor_dict}
    except Exception as e: raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

@app.put("/api/motores/{id_motor}", tags=["Clientes e Motores"])
def atualizar_motor(id_motor: str, motor_atualizado: Motor):
    try:
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP, sep=None, engine='python')
        df['id_motor'] = df['id_motor'].astype(str)
        if id_motor not in df['id_motor'].values: raise HTTPException(status_code=404, detail="Motor não encontrado")
        indice = df.index[df['id_motor'] == id_motor].tolist()[0]
        for chave, valor in motor_atualizado.dict().items():
            if (valor is None or valor == '') and pd.api.types.is_numeric_dtype(df[chave]): df.loc[indice, chave] = pd.NA
            else: df.loc[indice, chave] = valor
        df.to_csv("clientes_motores.csv", index=False)
        return {"mensagem": "Registro atualizado com sucesso!", "dados": motor_atualizado.dict()}
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/motores/{id_motor}", tags=["Clientes e Motores"])
def remover_motor(id_motor: str):
    try:
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP, sep=None, engine='python')
        if id_motor not in df['id_motor'].values: raise HTTPException(status_code=404, detail="Motor não encontrado")
        df_atualizado = df[df['id_motor'] != id_motor]
        df_atualizado.to_csv("clientes_motores.csv", index=False)
        return Response(status_code=204)
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Módulo de Relatórios e OS ---
@app.post("/api/relatorios", tags=["Relatórios e OS"])
async def gerar_relatorio_endpoint(id_motor: str=Form(...), arquivo_csv: UploadFile=File(...), tem_vazao: bool=Form(False), tem_nivel: bool=Form(False)):
    caminho_temp = f"uploads/{uuid.uuid4()}_{arquivo_csv.filename}"
    try:
        with open(caminho_temp, "wb") as buffer: shutil.copyfileobj(arquivo_csv.file, buffer)
        df_brutos = pd.read_csv(caminho_temp, delimiter=';')
        df_registros = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP)
        df_registros['id_motor'] = df_registros['id_motor'].astype(str)
        dados_motor = df_registros[df_registros['id_motor'] == id_motor].to_dict('records')
        if not dados_motor: raise HTTPException(status_code=404, detail=f"Motor ID {id_motor} não encontrado.")
        checkboxes = {'tem_vazao': tem_vazao, 'tem_nivel': tem_nivel}
        caminho_pdf = pdf_generator.gerar_relatorio_final(df_brutos, dados_motor[0], checkboxes, id_motor)
        if os.path.exists(caminho_pdf):
            return FileResponse(path=caminho_pdf, media_type='application/pdf', filename=os.path.basename(caminho_pdf))
        else: raise HTTPException(status_code=500, detail="O PDF não foi gerado.")
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha crítica: {str(e)}")
    finally:
        if os.path.exists(caminho_temp): os.remove(caminho_temp)

@app.post("/api/ordens-servico", tags=["Relatórios e OS"])
def criar_ordem_de_servico(os_data: OrdemServico):
    try:
        df_registros = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP)
        df_registros['id_cliente'] = df_registros['id_cliente'].astype(int)
        df_registros['id_motor'] = df_registros['id_motor'].astype(str)
        registro_selecionado = df_registros[(df_registros['id_cliente'] == os_data.id_cliente) & (df_registros['id_motor'] == os_data.id_motor)].to_dict('records')
        if not registro_selecionado: raise HTTPException(status_code=404, detail="Registro não encontrado.")
        caminho_pdf = os_generator.gerar_os_pdf(dados_cliente=registro_selecionado[0], dados_motor=registro_selecionado[0], tipo_servico=os_data.tipo_servico, descricao_servico=os_data.descricao_servico)
        return {"mensagem": "OS gerada com sucesso!", "nome_arquivo": os.path.basename(caminho_pdf)}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao gerar OS: {str(e)}")

@app.get("/api/relatorios-salvos", tags=["Relatórios e OS"])
def get_relatorios_salvos():
    pasta = "reports_generated"; relatorios = []
    if not os.path.exists(pasta): return []
    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.endswith(".pdf"):
            try:
                partes = nome_arquivo.split('_')
                if partes[0] == 'RELATORIO':
                    info = {"nome_arquivo": nome_arquivo, "cliente": partes[2].replace("_", " "), "motor": partes[3].replace("_", " ")}
                elif partes[0] == 'OS':
                    info = {"nome_arquivo": nome_arquivo, "cliente": partes[1].replace("-", " "), "motor": "N/A"}
                else:
                    info = {"nome_arquivo": nome_arquivo, "cliente": "Desconhecido"}
                info["data"] = f"{partes[-1].split('.')[0]}"
                info["tamanho_mb"] = f"{os.path.getsize(os.path.join(pasta, nome_arquivo)) / (1024*1024):.2f} MB"
                relatorios.append(info)
            except Exception:
                relatorios.append({"nome_arquivo": nome_arquivo, "cliente": "Desconhecido"})
    return sorted(relatorios, key=lambda x: x.get('nome_arquivo'), reverse=True)

@app.get("/api/relatorios-salvos/{nome_arquivo}", tags=["Relatórios e OS"])
def get_relatorio_especifico(nome_arquivo: str):
    caminho = Path("reports_generated") / nome_arquivo
    if not caminho.is_file() or not caminho.resolve().parent.samefile(Path("reports_generated").resolve()):
        raise HTTPException(status_code=404, detail="Acesso negado.")
    return FileResponse(path=caminho, media_type='application/pdf', filename=nome_arquivo)

@app.delete("/api/relatorios-salvos/{nome_arquivo}", tags=["Relatórios e OS"])
def excluir_relatorio_especifico(nome_arquivo: str):
    caminho = Path("reports_generated") / nome_arquivo
    if not caminho.is_file() or not caminho.resolve().parent.samefile(Path("reports_generated").resolve()):
        raise HTTPException(status_code=404, detail="Acesso negado.")
    try:
        os.remove(caminho)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Não foi possível excluir: {e}")

@app.post("/api/relatorios-salvos/{nome_arquivo}/enviar-email", tags=["Relatórios e OS"])
async def enviar_relatorio_por_email(nome_arquivo: str):
    caminho_arquivo = Path("reports_generated") / nome_arquivo
    if not caminho_arquivo.is_file(): raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    try:
        id_motor_extraido = nome_arquivo.split('_')[1]
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP)
        df['id_motor'] = df['id_motor'].astype(str)
        dados_cliente = df[df['id_motor'] == id_motor_extraido].to_dict('records')
        if not dados_cliente or not dados_cliente[0].get('email_responsavel'):
            raise HTTPException(status_code=404, detail="E-mail não encontrado.")
        email_destinatario = dados_cliente[0]['email_responsavel']
        nome_cliente = dados_cliente[0]['nome_cliente']
        message = MessageSchema(
            subject=f"Seu Documento Técnico: {nome_cliente}",
            recipients=[email_destinatario],
            body="Olá,\n\nSegue em anexo o documento solicitado.\n\nAtenciosamente,\nSistema de Relatórios.",
            attachments=[str(caminho_arquivo)],
            subtype="plain"
        )
        fm = FastMail(conf_email)
        await fm.send_message(message)
        return {"message": f"Enviado com sucesso para {email_destinatario}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao enviar e-mail: {str(e)}")

@app.post("/api/relatorios-salvos/{nome_arquivo}/enviar-whatsapp", tags=["Relatórios e OS"])
async def enviar_relatorio_por_whatsapp(nome_arquivo: str):
    caminho_arquivo = Path("reports_generated") / nome_arquivo
    if not caminho_arquivo.is_file(): raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    try:
        id_motor_extraido = nome_arquivo.split('_')[1]
        df = pd.read_csv("clientes_motores.csv", dtype=DTYPE_MAP)
        df['id_motor'] = df['id_motor'].astype(str)
        dados_registro = df[df['id_motor'] == id_motor_extraido].to_dict('records')
        if not dados_registro or not dados_registro[0].get('telefone_contato'):
            raise HTTPException(status_code=404, detail="Telefone não encontrado.")
        numero_original = str(dados_registro[0]['telefone_contato']).strip().replace('.0', '')
        telefone_destinatario = f"whatsapp:+55{numero_original}" if not numero_original.startswith('55') else f"whatsapp:+{numero_original}"
        nome_cliente = dados_registro[0]['nome_cliente']
        link_download = f"http://192.168.1.9:8000/api/relatorios-salvos/{nome_arquivo}"
        corpo_mensagem = (f"Olá, {nome_cliente}! Segue o seu documento técnico.\n\n"
                        f"Acesse o link para visualizar ou baixar:\n{link_download}\n\n"
                        "Atenciosamente,\nEquipe de Relatórios")
        message = twilio_client.messages.create(from_=twilio_number, body=corpo_mensagem, to=telefone_destinatario)
        return {"message": f"WhatsApp enviado para o número finalizado em {telefone_destinatario[-4:]}"}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao enviar WhatsApp: {str(e)}")

# --- Módulo de Dashboard ---
@app.post("/api/dashboard/analise-instantanea", tags=["Dashboard"])
async def get_analise_instantanea(arquivo_csv: UploadFile = File(...)):
    caminho_temp = f"uploads/{uuid.uuid4()}_{arquivo_csv.filename}"
    try:
        with open(caminho_temp, "wb") as buffer: shutil.copyfileobj(arquivo_csv.file, buffer)
        df = pd.read_csv(caminho_temp, delimiter=';')
        coluna_tempo = analises.MAPEAMENTO_COLUNAS.get('timestamp')
        if coluna_tempo not in df.columns: raise HTTPException(status_code=400, detail=f"Coluna '{coluna_tempo}' necessária.")
        df[coluna_tempo] = pd.to_datetime(df[coluna_tempo], dayfirst=True, errors='coerce')
        df.dropna(subset=[coluna_tempo], inplace=True)
        df = df.set_index(coluna_tempo).sort_index()
        col_corrente_ref = analises.MAPEAMENTO_COLUNAS.get('corrente_a')
        if col_corrente_ref not in df.columns: raise HTTPException(status_code=400, detail=f"Coluna '{col_corrente_ref}' necessária.")
        df_operando = df[df[col_corrente_ref] > 1.0].copy()
        kpis = {}
        if not df_operando.empty:
            kpis["tensao_media"] = df_operando[analises.MAPEAMENTO_COLUNAS.get('tensao_a', 'AVRMS')].mean()
            kpis["corrente_media"] = df_operando[col_corrente_ref].mean()
            kpis["fp_medio"] = df_operando[analises.MAPEAMENTO_COLUNAS.get('fp_a', 'AFP')].mean()
        else: kpis = {"tensao_media": 0, "corrente_media": 0, "fp_medio": 0}
        kpis["periodo_analisado"] = f"{df.index.min().strftime('%d/%m/%Y')} a {df.index.max().strftime('%d/%m/%Y')}"
        kpis["analise_operacao"] = analises.analisar_operacao(df, 380.0)
        kpis.update(analises.calcular_kpis_vazao(df))
        df_resampled = df.resample('15min').mean().dropna(how='all') if len(df) > 2000 else df
        def formatar_para_grafico(dataframe, colunas_keys):
            cols_reais = [analises.MAPEAMENTO_COLUNAS.get(k) for k in colunas_keys if analises.MAPEAMENTO_COLUNAS.get(k) in dataframe.columns]
            if not cols_reais: return None
            df_temp = dataframe[cols_reais].copy().reset_index().rename(columns={coluna_tempo: 'timestamp'})
            df_temp['timestamp'] = df_temp['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            return df_temp.replace({np.nan: None}).to_dict('records')
        response_data = {
            "kpis": kpis,
            "grafico_tensao": formatar_para_grafico(df_resampled, ['tensao_a', 'tensao_b', 'tensao_c']),
            "grafico_corrente": formatar_para_grafico(df_resampled, ['corrente_a', 'corrente_b', 'corrente_c']),
            "grafico_fp": formatar_para_grafico(df_resampled, ['fp_a', 'fp_b', 'fp_c']),
            "grafico_nivel": formatar_para_grafico(df_resampled, ['nivel']),
            "grafico_velocidade": formatar_para_grafico(df_resampled, ['velocidade'])
        }
        return response_data
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao processar arquivo: {str(e)}")
    finally:
        if os.path.exists(caminho_temp): os.remove(caminho_temp)