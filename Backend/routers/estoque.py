# Arquivo: backend/routers/estoque.py

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime
import os
from services import data_service
import pdf_estoque_generator

router = APIRouter(
    prefix="/api/estoque",
    tags=["Estoque"]
)

# --- MODELOS DE DADOS Pydantic ---
class Componente(BaseModel):
    modelo_componente: str
    nome_componente: str
    especificacao: Optional[str] = None
    quantidade: int
    localizacao: Optional[str] = None

# --- ENDPOINTS ---

@router.get("/")
def get_estoque():
    try:
        df = data_service.get_estoque_df()
        df_filled = df.fillna("")
        return JSONResponse(content=df_filled.to_dict('records'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def adicionar_ou_atualizar_estoque(componente: Componente):
    try:
        df = data_service.get_estoque_df()
        componente_existente = df[df['modelo_componente'] == componente.modelo_componente]

        if not componente_existente.empty:
            indice = componente_existente.index[0]
            # Se for uma adição (body completo), substitui. Se for só quantidade, soma.
            # Assumindo que o front envia o objeto completo para adição.
            df.loc[indice, 'quantidade'] += componente.quantidade
            df.loc[indice, 'data_ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mensagem = f"Estoque do componente '{componente.modelo_componente}' atualizado."
        else:
            novo_componente_dict = componente.dict()
            novo_componente_dict['data_ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            novo_df = pd.DataFrame([novo_componente_dict])
            df = pd.concat([df, novo_df], ignore_index=True)
            mensagem = f"Novo componente '{componente.modelo_componente}' adicionado ao estoque."
        
        data_service.update_estoque_sheet(df)
        return {"mensagem": mensagem}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

@router.put("/{modelo_original}")
def atualizar_componente(modelo_original: str, componente_editado: Componente):
    try:
        df = data_service.get_estoque_df()
        indice_lista = df.index[df['modelo_componente'] == modelo_original].tolist()
        
        if not indice_lista:
            raise HTTPException(status_code=404, detail="Componente original não encontrado.")
        
        indice = indice_lista[0]
        dados_novos = componente_editado.dict()
        for chave, valor in dados_novos.items():
            df.loc[indice, chave] = valor
        df.loc[indice, 'data_ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        data_service.update_estoque_sheet(df)
        return {"mensagem": f"Componente '{modelo_original}' atualizado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{modelo_componente}")
def remover_componente(modelo_componente: str):
    try:
        df = data_service.get_estoque_df()
        if modelo_componente not in df['modelo_componente'].values:
            raise HTTPException(status_code=404, detail="Componente não encontrado")
        
        df_atualizado = df[df['modelo_componente'] != modelo_componente]
        data_service.update_estoque_sheet(df_atualizado)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exportar-pdf")
def exportar_estoque_pdf():
    try:
        df = data_service.get_estoque_df()
        dados_lista = df.to_dict('records')
        caminho_pdf = pdf_estoque_generator.gerar_pdf_estoque(dados_lista)
        
        if os.path.exists(caminho_pdf):
            return FileResponse(path=caminho_pdf, media_type='application/pdf', filename=os.path.basename(caminho_pdf))
        else:
            raise HTTPException(status_code=500, detail="O arquivo PDF de estoque não foi gerado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha crítica: {str(e)}")