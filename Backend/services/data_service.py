# Arquivo: backend/services/data_service.py (VERSÃO À PROVA DE FALHAS)

import pandas as pd
import traceback
import sheets_client
from typing import Dict, Any

SHEET_CLIENTES_MOTORES = "clientes_motores"
SHEET_ESTOQUE = "estoque_componentes"

def get_clientes_motores_df() -> pd.DataFrame:
    try:
        df = sheets_client.get_sheet_as_dataframe(SHEET_CLIENTES_MOTORES)
        
        if df.empty:
            return df

        # --- CONVERSÃO DE TIPOS BLINDADA ---
        # Converte cada coluna numérica individualmente de forma segura.
        # 'errors=coerce' transforma qualquer valor que não seja um número em Nulo (NaN), em vez de quebrar.

        numeric_cols_float = ['corrente_nominal', 'potencia_cv', 'tensao_nominal_v']
        for col in numeric_cols_float:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # A conversão para Inteiro é feita por último e lida bem com os Nulos (NaN).
        if 'id_cliente' in df.columns:
            df['id_cliente'] = pd.to_numeric(df['id_cliente'], errors='coerce').astype('Int64')

        # Converte as colunas restantes para texto para garantir consistência
        for col in df.columns:
            if col not in ['id_cliente'] + numeric_cols_float:
                # O .astype(str) garante que tudo seja texto, limpando formatos
                df[col] = df[col].astype(str)

        return df
    except Exception as e:
        print(f"ERRO CRÍTICO AO PROCESSAR DADOS DE CLIENTES: {e}")
        traceback.print_exc()
        return pd.DataFrame() # Retorna DataFrame vazio em caso de erro


def get_estoque_df() -> pd.DataFrame:
    try:
        df = sheets_client.get_sheet_as_dataframe(SHEET_ESTOQUE)
        if df.empty:
            return df

        if 'quantidade' in df.columns:
            df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        print(f"ERRO CRÍTICO AO LER PLANILHA DE ESTOQUE: {e}")
        return pd.DataFrame()


def update_clientes_motores_sheet(df: pd.DataFrame):
    try:
        # Antes de salvar, converte colunas para texto para evitar problemas de formato no Sheets
        df_para_salvar = df.copy()
        for col in df_para_salvar.columns:
            df_para_salvar[col] = df_para_salvar[col].astype(str).replace('<NA>', '')
        sheets_client.update_worksheet(SHEET_CLIENTES_MOTORES, df_para_salvar)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de clientes: {e}")


def update_estoque_sheet(df: pd.DataFrame):
    try:
        df_para_salvar = df.copy()
        for col in df_para_salvar.columns:
            df_para_salvar[col] = df_para_salvar[col].astype(str).replace('<NA>', '')
        sheets_client.update_worksheet(SHEET_ESTOQUE, df_para_salvar)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de estoque: {e}")