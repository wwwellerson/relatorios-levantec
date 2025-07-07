# Arquivo: backend/services/data_service.py (VERSÃO FINAL BLINDADA)

import pandas as pd
import traceback
import sheets_client
from typing import Dict, Any, Union, List

SHEET_CLIENTES_MOTORES = "clientes_motores"
SHEET_ESTOQUE = "estoque_componentes"
DTYPE_MAP_CLIENTES = {
    'id_cliente': 'Int64', 'nome_cliente': 'str', 'id_motor': 'str',
    'descricao_motor': 'str', 'local_instalacao': 'str', 'corrente_nominal': 'float64',
    'potencia_cv': 'float64', 'tipo_conexao': 'str', 'tensao_nominal_v': 'float64',
    'grupo_tarifario': 'str', 'telefone_contato': 'str', 'email_responsavel': 'str',
    'data_da_instalacao': 'str', 'id_esp32': 'str', 'observacoes': 'str'
}

def get_clientes_motores_df() -> pd.DataFrame:
    try:
        df = sheets_client.get_sheet_as_dataframe(SHEET_CLIENTES_MOTORES)
        if df.empty:
            return pd.DataFrame(columns=DTYPE_MAP_CLIENTES.keys())

        numeric_cols_float = ['corrente_nominal', 'potencia_cv', 'tensao_nominal_v']
        for col in numeric_cols_float:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'id_cliente' in df.columns:
            df['id_cliente'] = pd.to_numeric(df['id_cliente'], errors='coerce').astype('Int64')

        for col in df.columns:
            if col not in ['id_cliente'] + numeric_cols_float:
                df[col] = df[col].astype(str)

        return df
    except Exception as e:
        print(f"ERRO CRÍTICO AO PROCESSAR DADOS DE CLIENTES: {e}")
        traceback.print_exc()
        return pd.DataFrame(columns=DTYPE_MAP_CLIENTES.keys())

def get_estoque_df() -> pd.DataFrame:
    colunas_estoque = ['modelo_componente', 'nome_componente', 'especificacao', 'quantidade', 'localizacao', 'data_ultima_atualizacao']
    try:
        df = sheets_client.get_sheet_as_dataframe(SHEET_ESTOQUE)
        if df.empty:
            return pd.DataFrame(columns=colunas_estoque)
        if 'quantidade' in df.columns:
            df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        print(f"ERRO CRÍTICO AO LER PLANILHA DE ESTOQUE: {e}")
        return pd.DataFrame(columns=colunas_estoque)

def update_clientes_motores_sheet(df: Union[pd.DataFrame, List[Dict[str, Any]]]):
    try:
        # --- CORREÇÃO FINAL: Garante que o input é um DataFrame ---
        if not isinstance(df, pd.DataFrame):
            # Se, por algum motivo, recebermos uma lista, a convertemos de volta para DataFrame.
            df = pd.DataFrame(df)

        df_para_salvar = df.copy()
        df_para_salvar.fillna('', inplace=True)
        df_formatado = df_para_salvar.astype(str).replace('<NA>', '')
        sheets_client.update_worksheet(SHEET_CLIENTES_MOTORES, df_formatado)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de clientes: {e}")

def update_estoque_sheet(df: Union[pd.DataFrame, List[Dict[str, Any]]]):
    try:
        # --- CORREÇÃO FINAL: Garante que o input é um DataFrame ---
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
            
        df_para_salvar = df.copy()
        df_para_salvar.fillna('', inplace=True)
        df_formatado = df_para_salvar.astype(str).replace('<NA>', '')
        sheets_client.update_worksheet(SHEET_ESTOQUE, df_formatado)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de estoque: {e}")
