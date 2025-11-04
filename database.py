import psycopg2
from datetime import datetime, timezone
import config # Importa as configurações

def conectar_bd():
    """Estabelece a conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
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
        if conn:
            conn.close()
    
    print("Nenhum token válido encontrado no banco de dados.")
    return None

def salvar_token_bd(token_info):
    """Salva um novo token no banco de dados."""
    conn = conectar_bd()
    if not conn:
        return

    try:
        expires_in_int = int(token_info['expires_in'])
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pub_token_bradesco (access_token, token_type, dtemissao, expires_in, scope)
                VALUES (%s, %s, %s, %s, %s);
            """, (
                token_info['access_token'],
                token_info['token_type'],
                datetime.now(timezone.utc),
                expires_in_int,
                token_info['scope']
            ))
        conn.commit()
        print("Novo token salvo no banco de dados com sucesso.")
    except (psycopg2.Error, KeyError, ValueError) as e:
        print(f"Erro ao salvar token no banco de dados: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()