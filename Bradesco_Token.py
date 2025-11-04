import database
import bradesco_api

def obter_token_acesso():
    """
    Orquestra a obtenção do token.
    Primeiro, tenta buscar um token válido no banco de dados.
    Se não encontrar, solicita um novo à API e o salva no banco.
    Retorna o access_token em caso de sucesso ou None em caso de falha.
    """
    # 1. Tenta buscar um token válido no banco de dados
    print("Verificando se há um token válido no banco de dados...")
    access_token = database.buscar_token_valido_bd()

    if access_token:
        return access_token

    # 2. Se não encontrou, solicita um novo para a API
    print("\nNenhum token válido encontrado. Solicitando um novo token da API...")
    token_info = bradesco_api.solicitar_novo_token()

    # 3. Se a API retornou um token, salva no banco e retorna o token de acesso
    if token_info and 'access_token' in token_info:
        database.salvar_token_bd(token_info)
        return token_info['access_token']
    
    # 4. Se falhou em todas as tentativas
    print("Não foi possível obter um novo token da API.")
    return None