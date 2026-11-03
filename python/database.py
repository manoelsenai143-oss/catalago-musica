import psycopg2

def criar_conexao():
    conexao = psycopg2.connect(
        host="127.0.0.1",
        database="catalago_musica",
        user="postgres",
        password="1234",
        port="5432"
    )
    return conexao