import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# URLs do ambiente de Sandbox
TOKEN_URL = "https://openapisandbox.prebanco.com.br/auth/server-mtls/v2/token"
REGISTRO_URL = "https://openapisandbox.prebanco.com.br/v1/fornecimento-saldos-contas/saldos"

# Obtém as credenciais do ambiente
CLIENT_ID = os.getenv('BRADESCO_CLIENT_ID')
CLIENT_SECRET = os.getenv('BRADESCO_CLIENT_SECRET')


# Certifique-se de que os nomes dos arquivos correspondem aos seus.
CERT_FILE_PATH = os.path.join('certs', 'seu_certificado.crt')
KEY_FILE_PATH = os.path.join('certs', 'sua_chave_privada.key')

# Agrupa os caminhos em uma tupla para usar com o requests
CERTIFICATES = (CERT_FILE_PATH, KEY_FILE_PATH)

def get_bradesco_token():
    """Obtém o token de acesso da API do Bradesco usando mTLS."""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    try:
        print("Tentando obter token com mTLS...")
        
        response = requests.post(
            TOKEN_URL, 
            headers=headers, 
            data=payload, 
            cert=CERTIFICATES, 
            verify=False  # Para Sandbox. Em produção, use o CA do banco: verify='/path/to/ca.pem'
        )
        response.raise_for_status()
        print("Token obtido com sucesso.")
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token: {e}")
        # Detalhe extra em caso de erro de certificado
        if "SSL" in str(e):
            print("Dica: Verifique se os caminhos dos certificados estão corretos e se os arquivos são válidos.")
        return None

def get_bradesco_saldo(token, agencia, conta):
    """Consulta o saldo de uma conta usando o token e mTLS."""
    if not token:
        return None

    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'agencia': agencia,
        'conta': conta
    }

    try:
        print("Consultando saldo com mTLS...")
        # ADICIONAMOS O PARÂMETRO `cert` AQUI TAMBÉM
        response = requests.get(
            REGISTRO_URL, 
            headers=headers, 
            params=params, 
            cert=CERTIFICATES, 
            verify=False # Para Sandbox.
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Lógica para extrair o valor do saldo (mesma de antes)
        saldo_info = next(
            (item for item in data['saldoCC']['lstLancamentosSaldos'] if item['nomeProduto'] == 'SALDO TOTAL'),
            None
        )

        if saldo_info and 'valorLancamento' in saldo_info:
            valor_str = saldo_info['valorLancamento']
            saldo_float = float(valor_str.replace('.', '').replace(',', '.'))
            print(f"Saldo encontrado: {saldo_float}")
            return saldo_float
        else:
            print("Não foi possível encontrar o 'SALDO TOTAL' na resposta da API.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar saldo: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Erro ao processar a resposta JSON do saldo: {e}")
        return None