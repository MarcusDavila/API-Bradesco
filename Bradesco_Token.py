import requests
import os
import ssl
import psycopg2
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configurações do Banco de Dados (do .env) ---
DB_NAME = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Classe para adaptar o request para certificados com senha
class SSLAdapterComSenha(HTTPAdapter):
    """Um adaptador HTTP que permite o uso de chaves privadas de certificado protegidas por senha."""
    def __init__(self, cert_file, key_file, password, *args, **kwargs):
        self.cert_file = cert_file
        self.key_file = key_file
        self.password = password
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(
            certfile=self.cert_file,
            keyfile=self.key_file,
            password=self.password
        )
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context
        )

def conectar_bd():
    """Estabelece a conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def buscar_token_valido_bd():
    """Verifica se existe um token válido no banco de dados."""
    conn = conectar_bd()
    if not conn:
        return None

    try:
        with conn.cursor() as cur:
            # Busca o token mais recente que ainda não expirou
            # Adicionamos uma margem de segurança de 60 segundos
            cur.execute("""
                SELECT access_token, dtemissao, expires_in
                FROM pub_token_bradesco
                WHERE dtemissao + INTERVAL '1 second' * (expires_in - 60) > NOW()
                ORDER BY dtemissao DESC
                LIMIT 1;
            """)
            resultado = cur.fetchone()
            if resultado:
                print("Token válido encontrado no banco de dados.")
                return resultado[0] # Retorna apenas o access_token
    except psycopg2.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
    finally:
        conn.close()
    
    print("Nenhum token válido encontrado no banco de dados.")
    return None

def salvar_token_bd(token_info):
    """Salva um novo token no banco de dados."""
    conn = conectar_bd()
    if not conn:
        return

    try:
        # A API retorna 'expires_in' como string, então convertemos para inteiro
        expires_in_int = int(token_info['expires_in'])
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pub_token_bradesco (access_token, token_type, dtemissao, expires_in, scope)
                VALUES (%s, %s, %s, %s, %s);
            """, (
                token_info['access_token'],
                token_info['token_type'],
                datetime.now(timezone.utc), # Usar timezone para consistência
                expires_in_int,
                token_info['scope']
            ))
        conn.commit()
        print("Novo token salvo no banco de dados com sucesso.")
    except (psycopg2.Error, KeyError, ValueError) as e:
        print(f"Erro ao salvar token no banco de dados: {e}")
        conn.rollback()
    finally:
        conn.close()

def solicitar_novo_token_bradesco():
    """Solicita um novo token de acesso à API do Bradesco."""
    client_id = os.getenv("BRADESCO_CLIENT_consulta_ID")
    cert_path = os.getenv("BRADESCO_CERT_FILE")
    key_path = os.getenv("BRADESCO_KEY_FILE")
    cert_password = os.getenv("Senha_CERT_FILE")

    if not all([client_id, cert_path, key_path, cert_password]):
        print("Erro: Variáveis de ambiente para a API do Bradesco não foram encontradas.")
        return None

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("Erro: Arquivo de certificado ou chave não encontrado.")
        return None

    url = "https://openapi.bradesco.com.br/auth/server-mtls/v2/token"
    # O client_secret não é mais necessário no payload, pois a autenticação é mútua (mTLS)
    payload = f'grant_type=client_credentials&client_id={client_id}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        session = requests.Session()
        adapter = SSLAdapterComSenha(cert_file=cert_path, key_file=key_path, password=cert_password)
        session.mount('https://openapi.bradesco.com.br', adapter)

        print("Realizando a chamada para a API do Bradesco para obter um novo token...")
        response = session.post(url, headers=headers, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        print("Token recebido com sucesso da API!")
        
        # Salva o novo token no banco de dados
        salvar_token_bd(token_data)
        
        return token_data['access_token']
    
    except ssl.SSLError as e:
        print(f"Ocorreu um erro de SSL. Causa comum: senha incorreta da chave privada. Erro: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição para a API: {e}")
        # Adiciona um print do corpo da resposta para ajudar a depurar
        if e.response is not None:
            print(f"Resposta da API (Erro): {e.response.text}")
        return None
    except json.JSONDecodeError:
        print("Erro ao decodificar a resposta JSON da API.")
        print(f"Resposta recebida: {response.text}")
        return None


# --- Bloco de execução principal ---
if __name__ == "__main__":
    access_token = buscar_token_valido_bd()

    if not access_token:
        print("Iniciando processo para obter um novo token da API.")
        access_token = solicitar_novo_token_bradesco()

    if access_token:
        print("\n--- Token de Acesso Pronto para Uso ---")
        # Mostra apenas uma parte do token para segurança
        print(f"{access_token[:30]}...") 
        print("---------------------------------------\n")
    else:
        print("\n--- Falha ao obter o token de acesso. ---")