# Arquivo: backend/services/data_service.py (VERSÃO FINAL ROBUSTA)

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
        
        if df.empty:
            # Retorna um DataFrame vazio com as colunas corretas se a planilha estiver vazia
            return pd.DataFrame(columns=DTYPE_MAP_CLIENTES.keys())

        # --- NOVA LÓGICA DE CONVERSÃO - MAIS SEGURA ---
        df_final = pd.DataFrame()

        for col_name, col_type in DTYPE_MAP_CLIENTES.items():
            if col_name in df.columns:
                series = df[col_name]
                if 'Int64' in str(col_type) or 'float' in str(col_type):
                    # Para colunas numéricas, usa to_numeric com 'coerce'. Isso transforma
                    # valores que não são números em Nulo (NaN), em vez de quebrar.
                    df_final[col_name] = pd.to_numeric(series, errors='coerce')
                else:
                    # Para outras colunas (texto), preenche nulos com texto vazio e converte.
                    df_final[col_name] = series.fillna('').astype(str)
            else:
                # Se a coluna esperada não existir na planilha, cria uma coluna vazia.
                df_final[col_name] = pd.Series(dtype=col_type)
        
        # Aplica o tipo final, agora que os dados estão limpos e seguros
        return df_final.astype(DTYPE_MAP_CLIENTES, errors='ignore')

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


def update_clientes_motores_sheet(df: pd.DataFrame):
    try:
        # Cria uma cópia para evitar modificar o DataFrame original
        df_para_salvar = df.copy()
        # Preenche qualquer valor nulo com uma string vazia antes de salvar
        df_para_salvar.fillna('', inplace=True)
        # Converte tudo para string, que é o formato mais seguro para salvar no Sheets
        df_formatado = df_para_salvar.astype(str)

        sheets_client.update_worksheet(SHEET_CLIENTES_MOTORES, df_formatado)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de clientes: {e}")


def update_estoque_sheet(df: pd.DataFrame):
    try:
        df_para_salvar = df.copy()
        df_para_salvar.fillna('', inplace=True)
        df_formatado = df_para_salvar.astype(str)
        sheets_client.update_worksheet(SHEET_ESTOQUE, df_formatado)
    except Exception as e:
        raise RuntimeError(f"Falha ao atualizar a planilha de estoque: {e}")
