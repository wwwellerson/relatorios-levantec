# Arquivo: backend/main.py (Versão Correta e Final)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa os módulos de rotas que criamos
from routers import clientes_motores, estoque, relatorios_os, dashboard

# --- INICIALIZAÇÃO DO FASTAPI ---
app = FastAPI(
    title="API do Sistema de Relatórios",
    version="3.0 Refatorada",
    description="API modularizada para gestão de clientes, estoque e geração de relatórios."
)

# --- Configuração do CORS ---
origins = [
    "http://localhost:3000",
    "http://192.168.1.9:3000", # Mantido para seu desenvolvimento local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# --- INCLUSÃO DAS ROTAS ---
app.include_router(clientes_motores.router)
app.include_router(estoque.router)
app.include_router(relatorios_os.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Root"])
def ler_raiz():
    """Endpoint principal que verifica se a API está online."""
    return {"mensagem": "Servidor do sistema de relatórios está online e refatorado!"}