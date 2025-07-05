# Arquivo: backend/sheets_client.py (VERSÃO FINAL PARA PRODUÇÃO)

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe
import os
import json

# Define o escopo de permissões. Leitura e escrita.
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Nome do arquivo de credenciais para uso local
CREDS_FILE = 'google_credentials.json'

# Nome da sua planilha no Google Sheets
SHEET_NAME = 'database_relatorios'

def get_client():
    """
    Autentica com o Google e retorna o cliente gspread.
    Esta versão é inteligente: ela usa a variável de ambiente no Render
    e o arquivo .json quando rodando localmente.
    """
    # Procura pela variável de ambiente primeiro (para o Render)
    creds_json_str = os.getenv('GOOGLE_CREDENTIALS_JSON')

    if creds_json_str:
        # Se encontrou, carrega as credenciais a partir do texto
        creds_dict = json.loads(creds_json_str)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    else:
        # Se não encontrou, usa o arquivo local (para desenvolvimento)
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(f"Arquivo de credenciais '{CREDS_FILE}' não encontrado para desenvolvimento local.")
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)

    client = gspread.authorize(creds)
    return client

# As funções abaixo não precisam de alteração
def get_sheet_as_dataframe(worksheet_name: str) -> pd.DataFrame:
    client = get_client()
    sheet = client.open(SHEET_NAME).worksheet(worksheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def update_worksheet(worksheet_name: str, dataframe: pd.DataFrame):
    client = get_client()
    sheet = client.open(SHEET_NAME).worksheet(worksheet_name)
    sheet.clear()
    set_with_dataframe(worksheet=sheet, dataframe=dataframe, include_index=False, include_column_header=True, resize=True)