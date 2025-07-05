# Arquivo: backend/sheets_client.py (VERSÃO FINAL COM NOVA AUTENTICAÇÃO)

import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
import os
import json

# O SCOPE não é mais necessário com esta biblioteca
CREDS_FILE = 'google_credentials.json'
SHEET_NAME = 'database_relatorios'

def get_client():
    """
    Autentica com o Google usando a nova biblioteca google-auth.
    Usa a variável de ambiente no Render ou o arquivo .json localmente.
    """
    creds_json_str = os.getenv('GOOGLE_CREDENTIALS_JSON')

    if creds_json_str:
        # No Render: usa as credenciais da variável de ambiente
        creds_dict = json.loads(creds_json_str)
        return gspread.service_account_from_dict(creds_dict)
    else:
        # Localmente: usa o arquivo google_credentials.json
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(f"Arquivo de credenciais '{CREDS_FILE}' não encontrado para desenvolvimento local.")
        return gspread.service_account(filename=CREDS_FILE)

# As funções abaixo continuam funcionando da mesma forma
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