# Arquivo: backend/routers/clientes_motores.py

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import uuid
from services import data_service

router = APIRouter(
    prefix="/api",
    tags=["Clientes e Motores"]
)

# --- MODELOS DE DADOS Pydantic (específicos para este router) ---
class Motor(BaseModel):
    id_cliente: int
    nome_cliente: str
    descricao_motor: str
    local_instalacao: Optional[str] = None
    corrente_nominal: Optional[float] = None
    potencia_cv: Optional[float] = None
    tipo_conexao: Optional[str] = None
    tensao_nominal_v: Optional[float] = None
    grupo_tarifario: Optional[str] = None
    telefone_contato: Optional[str] = None
    email_responsavel: Optional[str] = None
    data_da_instalacao: Optional[str] = None
    id_esp32: Optional[str] = None
    observacoes: Optional[str] = None

# --- ENDPOINTS ---

@router.get("/clientes")
def get_clientes():
    try:
        df = data_service.get_clientes_motores_df()
        if df.empty or 'id_cliente' not in df.columns:
            return []
        clientes_unicos = df[['id_cliente', 'nome_cliente']].dropna().drop_duplicates(subset=['id_cliente'])
        return JSONResponse(content=clientes_unicos.to_dict('records'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/registros")
def get_todos_os_registros():
    try:
        df = data_service.get_clientes_motores_df()
        # Preenche valores NaN com string vazia para compatibilidade com JSON
        df_filled = df.fillna("")
        return JSONResponse(content=df_filled.to_dict('records'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clientes/{id_cliente}/motores")
def get_motores_por_cliente(id_cliente: int):
    try:
        df = data_service.get_clientes_motores_df()
        motores_cliente = df[df['id_cliente'] == id_cliente][['id_motor', 'descricao_motor']]
        return JSONResponse(content=motores_cliente.to_dict('records'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/motores")
def adicionar_motor(motor: Motor):
    try:
        df = data_service.get_clientes_motores_df()
        novo_motor_dict = motor.dict()
        novo_motor_dict['id_motor'] = str(uuid.uuid4())[:8]
        
        novo_df = pd.DataFrame([novo_motor_dict])
        df_atualizado = pd.concat([df, novo_df], ignore_index=True)
        
        data_service.update_clientes_motores_sheet(df_atualizado)
        return {"mensagem": "Registro adicionado com sucesso!", "dados": novo_motor_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

@router.put("/motores/{id_motor}")
def atualizar_motor(id_motor: str, motor_atualizado: Motor):
    try:
        df = data_service.get_clientes_motores_df()
        if id_motor not in df['id_motor'].values:
            raise HTTPException(status_code=404, detail="Motor não encontrado")
        
        indice = df.index[df['id_motor'] == id_motor].tolist()[0]
        for chave, valor in motor_atualizado.dict().items():
            # Converte valores vazios/None para pd.NA em colunas numéricas
            if (valor is None or valor == '') and pd.api.types.is_numeric_dtype(df[chave]):
                df.loc[indice, chave] = pd.NA
            else:
                df.loc[indice, chave] = valor
        
        data_service.update_clientes_motores_sheet(df)
        return {"mensagem": "Registro atualizado com sucesso!", "dados": motor_atualizado.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/motores/{id_motor}")
def remover_motor(id_motor: str):
    try:
        df = data_service.get_clientes_motores_df()
        if id_motor not in df['id_motor'].values:
            raise HTTPException(status_code=404, detail="Motor não encontrado")
        
        df_atualizado = df[df['id_motor'] != id_motor]
        data_service.update_clientes_motores_sheet(df_atualizado)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))