
import psycopg2

def criar_conexao():
    try:
        conexao = psycopg2.connect(
            host="localhost",
            database="catalago_musica",
            user="postgres",
            password="1234",
            port="5432",
            client_encoding="UTF8"
        )

        return conexao

    except psycopg2.Error as erro:
        print("Erro ao conectar com o banco de dados:")
        print(repr(erro))
        raise
