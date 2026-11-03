from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Configuração da conexão com o banco de dados (ajuste com os seus dados reais)
def conectar_banco():
    conexao = psycopg2.connect(
        host="localhost",
        database="nome_do_seu_banco",  # Substitua pelo seu banco
        user="seu_usuario",              # Substitua pelo seu usuário
        password="sua_senha"             # Substitua pela sua senha
    )
    # Força a codificação UTF-8 para evitar erros com acentos
    conexao.set_client_encoding('UTF8')
    return conexao

# Rota para cadastrar usuário
@app.route('/usuarios', methods=['POST'])
def cadastrar_usuario():
    dados = request.get_json()
    nome = dados.get('nome_usuario')
    email = dados.get('email')
    senha = dados.get('senha')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO usuarios (nome_usuario, email, senha)
    VALUES (%s, %s, %s)
    """, (nome, email, senha))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201


# Rota para fazer login
@app.route('/login', methods=['POST'])
def fazer_login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT id, nome_usuario
    FROM usuarios
    WHERE email = %s AND senha = %s
    """, (email, senha))

    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()

    if usuario:
        return jsonify({
            "mensagem": f"Bem-vindo, {usuario[1]}!",
            "id_usuario": usuario[0]
        }), 200

    return jsonify({"erro": "Email ou senha incorretos."}), 401


# Rota para listar músicas
@app.route('/musicas', methods=['GET'])
def listar_musicas():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM musicas")
    resultados = cursor.fetchall()
    conexao.close()

    musicas = []
    for musica in resultados:
        # Função auxiliar para limpar acentos problemáticos se houver erro de codificação
        def limpar(texto):
            if isinstance(texto, str):
                try:
                    return texto.encode('latin-1').decode('utf-8')
                except:
                    return texto
            return str(texto)

        musicas.append({
            "id": musica["id"],
            "titulo": limpar(musica["titulo"]),
            "artista": limpar(musica["artista"]),
            "album": limpar(musica["album"]),
            "genero": limpar(musica["genero"])
        })

    return jsonify(musicas), 200
@app.route('/musicas', methods=['POST'])
def cadastrar_musica():
    dados = request.get_json()
    titulo = dados.get('titulo')
    artista = dados.get('artista')
    album = dados.get('album')
    genero = dados.get('genero')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO musicas (titulo, artista, album, genero)
    VALUES (%s, %s, %s, %s)
    """, (titulo, artista, album, genero))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Música cadastrada com sucesso!"}), 201


# Rota para buscar música por título
@app.route('/musicas/buscar', methods=['GET'])
def buscar_musica():
    titulo = request.args.get('titulo', '')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT id, titulo, artista, album, genero FROM musicas
    WHERE titulo ILIKE %s
    """, (f"%{titulo}%",))

    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()

    musicas = []
    for musica in resultados:
        musicas.append({
            "id": musica[0],
            "titulo": musica[1],
            "artista": musica[2],
            "album": musica[3],
            "genero": musica[4]
        })

    return jsonify(musicas), 200


# Rota para criar playlist
@app.route('/playlists', methods=['POST'])
def criar_playlist():
    dados = request.get_json()
    nome = dados.get('nome')
    id_usuario = dados.get('id_usuario')

    if not id_usuario:
        return jsonify({"erro": "ID do usuário é obrigatório."}), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO playlists (nome, id_usuario)
    VALUES (%s, %s)
    """, (nome, id_usuario))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Playlist criada com sucesso!"}), 201


if __name__ == '__main__':
    app.run(debug=True)