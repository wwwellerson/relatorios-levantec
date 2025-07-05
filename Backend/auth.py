# Arquivo: backend/services/data_service.py (VERSÃO DE SUPER-DEPURAÇÃO FINAL)

import pandas as pd
import traceback
import sheets_client
from typing import Dict, Any

# --- Constantes ---
SHEET_CLIENTES_MOTORES = "clientes_motores"
SHEET_ESTOQUE = "estoque_componentes"
DTYPE_MAP_CLIENTES = {
    'id_cliente': 'Int64', 'nome_cliente': 'str', 'id_motor': 'str', 'descricao_motor': 'str',
    'local_instalacao': 'str', 'corrente_nominal': 'float64', 'potencia_cv': 'float64',
    'tipo_conexao': 'str', 'tensao_nominal_v': 'float64', 'grupo_tarifario': 'str',
    'telefone_contato': 'str', 'email_responsavel': 'str', 'data_da_instalacao': 'str',
    'id_esp32': 'str', 'observacoes': 'str'
}

# --- Função de Leitura com Super-Depuração ---
def get_clientes_motores_df() -> pd.DataFrame:
    print("\n--- INICIANDO TESTE DE LEITURA DO GOOGLE SHEETS NO RENDER ---")
    try:
        df = sheets_client.get_sheet_as_dataframe(SHEET_CLIENTES_MOTORES)
        print("--- SUCESSO! Leitura da planilha concluída sem quebrar. ---")

        for col, dtype in DTYPE_MAP_CLIENTES.items():
            if col not in df.columns:
                df[col] = pd.Series(dtype=dtype)
        df = df.astype(DTYPE_MAP_CLIENTES, errors='ignore')
        return df

    except Exception as e:
        # ESTA PARTE AGORA VAI FORÇAR O SERVIDOR A MOSTRAR O ERRO REAL
        print("\n\n========================= ERRO DETECTADO NO RENDER =========================")
        traceback.print_exc()
        print("======================================================================\n\n")
        raise RuntimeError(f"Falha definitiva ao ler Google Sheets no Render. Verifique o log acima. Erro original: {e}")

# As outras funções permanecem as mesmas
def get_estoque_df() -> pd.DataFrame:
    return pd.DataFrame()
def update_clientes_motores_sheet(df: pd.DataFrame):
    pass
def update_estoque_sheet(df: pd.DataFrame):
    pass
