from Bradesco_Token import obter_token_acesso

def executar_consulta_principal():
    """Função principal que obtém o token e o utiliza para as operações."""
    
    print("--- Tentando obter token de acesso ---")
    access_token = obter_token_acesso()

    if access_token:
        print("\n--- Token de Acesso Pronto para Uso ---")
        # Mostra apenas uma parte do token para segurança
        print(f"{access_token[:30]}...") 
        print("---------------------------------------\n")
        
        #
        # ADICIONAR A LÓGICA PARA USAR O TOKEN
        #
        
    else:
        print("\n--- Falha ao obter o token de acesso. Verifique os logs de erro. ---")

# --- Bloco de execução principal ---
if __name__ == "__main__":
    executar_consulta_principal()