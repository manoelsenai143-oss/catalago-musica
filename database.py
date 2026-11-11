import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Carrega o .env se estiveres no PC local


def criar_conexao():
    try:
        # O psycopg2 aceita a DATABASE_URL diretamente como string de conexão!
        database_url = os.environ.get('DATABASE_URL')

        conexao = psycopg2.connect(database_url)
        return conexao

    except psycopg2.Error as erro:
        print("Erro ao conectar com o banco de dados:")
        print(repr(erro))
        raise