import requests
import ssl
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import config  # Importa as configurações

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

def solicitar_novo_token():
    """Solicita um novo token de acesso à API do Bradesco e retorna os dados do token."""
    if not all([config.BRADESCO_CLIENT_ID, config.BRADESCO_CERT_FILE, config.BRADESCO_KEY_FILE, config.BRADESCO_CERT_PASSWORD]):
        print("Erro: Variáveis de ambiente para a API do Bradesco não foram encontradas.")
        return None

    if not os.path.exists(config.BRADESCO_CERT_FILE) or not os.path.exists(config.BRADESCO_KEY_FILE):
        print("Erro: Arquivo de certificado ou chave não encontrado.")
        return None

    url = "https://openapi.bradesco.com.br/auth/server-mtls/v2/token"
    payload = f'grant_type=client_credentials&client_id={config.BRADESCO_CLIENT_ID}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        session = requests.Session()
        adapter = SSLAdapterComSenha(
            cert_file=config.BRADESCO_CERT_FILE, 
            key_file=config.BRADESCO_KEY_FILE, 
            password=config.BRADESCO_CERT_PASSWORD
        )
        session.mount('https://openapi.bradesco.com.br', adapter)

        print("Realizando a chamada para a API do Bradesco para obter um novo token...")
        response = session.post(url, headers=headers, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        print("Token recebido com sucesso da API!")
        return token_data
    
    except ssl.SSLError as e:
        print(f"Ocorreu um erro de SSL. Causa comum: senha incorreta da chave privada. Erro: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição para a API: {e}")
        if e.response is not None:
            print(f"Resposta da API (Erro): {e.response.text}")
        return None
    except json.JSONDecodeError:
        # Verifica se 'response' foi definido antes de tentar acessá-lo
        response_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'N/A'
        print(f"Erro ao decodificar a resposta JSON da API. Resposta recebida: {response_text}")
        return None