# Arquivo: backend/sheets_client.py (VERSÃO FINAL COM MÉTODO DE LEITURA ROBUSTO)

import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
import os
import json

CREDS_FILE = 'google_credentials.json'
SHEET_NAME = 'database_relatorios'

def get_client():
    creds_json_str = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if creds_json_str:
        creds_dict = json.loads(creds_json_str)
        return gspread.service_account_from_dict(creds_dict)
    else:
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(f"Arquivo de credenciais '{CREDS_FILE}' não encontrado.")
        return gspread.service_account(filename=CREDS_FILE)

def get_sheet_as_dataframe(worksheet_name: str) -> pd.DataFrame:
    """
    Busca uma aba da planilha usando o método get_all_values(), que é mais robusto,
    e constrói o DataFrame manualmente.
    """
    print(f"DEBUG: Lendo a aba '{worksheet_name}' com o método alternativo...")
    client = get_client()
    sheet = client.open(SHEET_NAME).worksheet(worksheet_name)

    # MÉTODO ALTERNATIVO: Pega todos os valores como uma lista de listas
    all_values = sheet.get_all_values()

    if not all_values or len(all_values) < 2:
        # Se a planilha estiver vazia ou tiver apenas o cabeçalho, retorna um DataFrame vazio.
        print(f"DEBUG: A planilha '{worksheet_name}' está vazia ou não tem dados de registro.")
        return pd.DataFrame()

    # A primeira lista (índice 0) é o cabeçalho, o resto são as linhas de dados.
    header = all_values[0]
    data_rows = all_values[1:]

    # Cria o DataFrame do Pandas manualmente a partir dos dados brutos.
    df = pd.DataFrame(data_rows, columns=header)
    print(f"DEBUG: DataFrame criado manualmente com {len(df)} linhas e {len(df.columns)} colunas.")
    return df

def update_worksheet(worksheet_name: str, dataframe: pd.DataFrame):
    client = get_client()
    sheet = client.open(SHEET_NAME).worksheet(worksheet_name)
    sheet.clear()
    set_with_dataframe(worksheet=sheet, dataframe=dataframe, include_index=False, include_column_header=True, resize=True)