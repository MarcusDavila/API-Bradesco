import sqlite3
from datetime import datetime

DATABASE_NAME = 'saldo_history.db'

def init_db():
    """Cria o banco de dados e a tabela se não existirem."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        # Cria a tabela para armazenar os registros de saldo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saldos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agencia TEXT NOT NULL,
                conta TEXT NOT NULL,
                saldo REAL NOT NULL,
                data_consulta TIMESTAMP NOT NULL
            )
        ''')
        conn.commit()
    print("Banco de dados inicializado com sucesso.")

def insert_saldo(agencia, conta, saldo):
    """Insere um novo registro de saldo no banco de dados."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        data_atual = datetime.now()
        
        # Usamos '?' para prevenir SQL Injection, uma prática de segurança essencial.
        cursor.execute(
            "INSERT INTO saldos (agencia, conta, saldo, data_consulta) VALUES (?, ?, ?, ?)",
            (agencia, conta, saldo, data_atual)
        )
        conn.commit()
    print(f"Saldo de R${saldo:.2f} para a conta {agencia}/{conta} inserido no banco.")