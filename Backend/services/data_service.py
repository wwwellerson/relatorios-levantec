# Arquivo: backend/services/data_service.py (VERSÃO FINAL E ROBUSTA)

import pandas as pd
import traceback
import sheets_client
from typing import Dict, Any

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

        # Se o DataFrame estiver vazio após a leitura, retorne-o imediatamente.
        if df.empty:
            return df

        # --- CORREÇÃO: Conversão de tipos de dados mais segura ---
        numeric_cols = [
            'id_cliente', 'corrente_nominal', 'potencia_cv', 'tensao_nominal_v'
        ]
        for col in numeric_cols:
            if col in df.columns:
                # pd.to_numeric com errors='coerce' transforma valores que não são números em Nulo (NaN),
                # em vez de causar um erro.
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Garante que todas as colunas esperadas existam
        for col, dtype in DTYPE_MAP_CLIENTES.items():
            if col not in df.columns:
                df[col] = pd.Series(dtype=dtype)

        # Aplica os tipos de dados finais
        df = df.astype(DTYPE_MAP_CLIENTES, errors='ignore')
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
        if 'modelo_componente' in df.columns:
            df['modelo_componente'] = df['modelo_componente'].astype(str)

        return df
    except Exception as e:
        print(f"ERRO CRÍTICO AO LER PLANILHA DE ESTOQUE: {e}")
        return pd.DataFrame(columns=colunas_estoque)


def update_clientes_motores_sheet(df: pd.DataFrame):
    try:
        df_completo = df.reindex(columns=DTYPE_MAP_CLIENTES.keys())
        sheets_client.update_worksheet(SHEET_CLIENTES_MOTORES, df_completo)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de clientes: {e}")


def update_estoque_sheet(df: pd.DataFrame):
    try:
        sheets_client.update_worksheet(SHEET_ESTOQUE, df)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de estoque: {e}")