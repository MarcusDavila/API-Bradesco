import requests
import os
import ssl
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# Criar um Adaptador HTTP customizado que entende de senhas de certificado
class SSLAdapterComSenha(HTTPAdapter):

    def __init__(self, cert_file, key_file, password, *args, **kwargs):
        self.cert_file = cert_file
        self.key_file = key_file
        self.password = password
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        # Cria um contexto SSL
        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        
        # Carrega o par certificado/chave, fornecendo a senha para a chave
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

# Função principal atualizada para usar o novo adaptador
def solicitar_token_bradesco():

    load_dotenv()

    client_id = os.getenv("BRADESCO_CLIENT_consulta_ID")
    client_secret = os.getenv("BRADESCO_CLIENT_consulta_SECRET")
    cert_path = os.getenv("BRADESCO_CERT_FILE")
    key_path = os.getenv("BRADESCO_KEY_FILE")
    cert_password = os.getenv("Senha_CERT_FILE")

    if not all([client_id, client_secret, cert_path, key_path, cert_password]):
        print("Erro: Uma ou mais variáveis de ambiente necessárias não foram encontradas.")
        print("Verifique se todas as cinco variáveis (ID, SECRET, CERT_FILE, KEY_FILE, Senha_CERT_FILE) estão no seu .env.")
        return None

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print(f"Erro: Arquivo de certificado ou chave não encontrado. Verifique os caminhos.")
        return None

    url = "https://openapi.bradesco.com.br/auth/server-mtls/v2/token"
    payload = f'grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        session = requests.Session()
        
        adapter = SSLAdapterComSenha(
            cert_file=cert_path,
            key_file=key_path,
            password=cert_password
        )
        
        session.mount('https://openapi.bradesco.com.br', adapter)

        print("Realizando a chamada para a API do Bradesco (com chave protegida por senha)...")
        response = session.post(url, headers=headers, data=payload)
        
        response.raise_for_status()
        print("Token recebido com sucesso!")
        return response.text
    
    except ssl.SSLError as e:
        print(f"Ocorreu um erro de SSL. A causa mais comum é uma SENHA INCORRETA para a chave privada. Verifique o .env. Erro: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")
        return None

# --- Bloco de execução principal ---
if __name__ == "__main__":
    token_info = solicitar_token_bradesco()

    if token_info:
        print("\n--- Resposta da API ---")
        print(token_info)
        print("-----------------------\n")