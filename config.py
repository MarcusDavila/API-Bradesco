import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configurações do Banco de Dados ---
DB_NAME = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# --- Configurações da API Bradesco ---
BRADESCO_CLIENT_ID = os.getenv("BRADESCO_CLIENT_consulta_ID")
BRADESCO_CERT_FILE = os.getenv("BRADESCO_CERT_FILE")
BRADESCO_KEY_FILE = os.getenv("BRADESCO_KEY_FILE")
BRADESCO_CERT_PASSWORD = os.getenv("Senha_CERT_FILE")