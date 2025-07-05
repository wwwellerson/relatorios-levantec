# Arquivo: backend/routers/dashboard.py (VERSÃO CORRIGIDA)

from fastapi import APIRouter, HTTPException, File, UploadFile
import pandas as pd
import numpy as np
import uuid
import shutil
import os
import analises

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

@router.post("/analise-instantanea")
async def get_analise_instantanea(arquivo_csv: UploadFile = File(...)):
    caminho_temp = f"uploads/{uuid.uuid4()}_{arquivo_csv.filename}"
    try:
        os.makedirs("uploads", exist_ok=True)
        with open(caminho_temp, "wb") as buffer:
            shutil.copyfileobj(arquivo_csv.file, buffer)
        
        # --- AQUI ESTÁ A CORREÇÃO ---
        # Adicionamos o delimiter=';' para ler o CSV corretamente.
        df = pd.read_csv(caminho_temp, delimiter=';')
        
        # Lógica de processamento do Dashboard
        coluna_tempo = analises.MAPEAMENTO_COLUNAS.get('timestamp')
        if coluna_tempo not in df.columns:
            raise HTTPException(status_code=400, detail=f"Coluna de timestamp '{coluna_tempo}' necessária não encontrada no arquivo.")
        
        df[coluna_tempo] = pd.to_datetime(df[coluna_tempo], dayfirst=True, errors='coerce')
        df.dropna(subset=[coluna_tempo], inplace=True)
        df = df.set_index(coluna_tempo).sort_index()

        col_corrente_ref = analises.MAPEAMENTO_COLUNAS.get('corrente_a')
        if col_corrente_ref not in df.columns:
            raise HTTPException(status_code=400, detail=f"Coluna de corrente '{col_corrente_ref}' necessária não encontrada.")
        
        df_operando = df[df[col_corrente_ref] > 1.0].copy()
        
        kpis = {}
        if not df_operando.empty:
            kpis["tensao_media"] = df_operando[analises.MAPEAMENTO_COLUNAS.get('tensao_a', 'AVRMS')].mean()
            kpis["corrente_media"] = df_operando[col_corrente_ref].mean()
            kpis["fp_medio"] = df_operando[analises.MAPEAMENTO_COLUNAS.get('fp_a', 'AFP')].mean()
        else:
            kpis = {"tensao_media": 0, "corrente_media": 0, "fp_medio": 0}
        
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao processar arquivo: {str(e)}")
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)