import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe

# Define o escopo de permissões. Read and write.
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Nome do seu arquivo de credenciais
CREDS_FILE = 'google_credentials.json'

# Nome da sua planilha no Google Sheets
SHEET_NAME = 'database_relatorios'

def get_client():
    """Autentica com o Google e retorna o cliente gspread."""
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client

def get_sheet_as_dataframe(worksheet_name: str) -> pd.DataFrame:
    """
    Busca uma aba específica da planilha e a retorna como um DataFrame do Pandas.
    `worksheet_name` é o nome da aba (ex: 'clientes_motores').
    """
    client = get_client()
    sheet = client.open(SHEET_NAME).worksheet(worksheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def update_worksheet(worksheet_name: str, dataframe: pd.DataFrame):
    """
    Atualiza uma aba inteira com os dados de um DataFrame do Pandas.
    `worksheet_name` é o nome da aba (ex: 'clientes_motores').
    `dataframe` é o DataFrame com os novos dados.
    """
    client = get_client()
    sheet = client.open(SHEET_NAME).worksheet(worksheet_name)
    # Limpa a aba antes de inserir os novos dados para evitar duplicatas
    sheet.clear() 
    set_with_dataframe(worksheet=sheet, dataframe=dataframe, include_index=False, include_column_header=True, resize=True)