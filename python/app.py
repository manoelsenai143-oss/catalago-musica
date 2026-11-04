from flask import Flask, jsonify, request, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import criar_conexao


app = Flask(__name__)



# 1 - Cadastrar usuário
@app.route('/usuarios', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome_usuario']
        email = request.form['email']
        senha = request.form['senha']

        conexao = criar_conexao()
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO "USUARIO" (nome_usuario, email, senha)
            VALUES (%s, %s, %s)
        """, (nome, email, senha))
        conexao.commit()
        cursor.close()
        conexao.close()

        # Após cadastrar com sucesso, redireciona para a página de login
        return redirect(url_for('fazer_login'))

    return render_template("cadastrar_usuario.html")


# Rota de Login (GET mostra o formulário, POST valida no banco)
@app.route('/login', methods=['GET', 'POST'])
def fazer_login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = criar_conexao()
        cursor = conexao.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, nome_usuario
            FROM "USUARIO"
            WHERE email = %s AND senha = %s
        """, (email, senha))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario:
            # Login bem-sucedido, redireciona para a listagem de músicas
            return redirect(url_for('listar_musicas'))
        else:
            erro = "Email ou senha incorretos."

    return render_template("login.html", erro=erro)

# 3 - Cadastrar música
@app.route('/musicas/novo', methods=['GET', 'POST'])
def cadastrar_musica():
    if request.method == 'POST':
        titulo = request.form['titulo']
        duracao = request.form['duracao']

        # A forma curta e direta de tratar o campo do álbum
        id_album_raw = request.form.get('id_album')
        id_album = int(id_album_raw) if id_album_raw else None

        id_genero = request.form['id_genero']

        conexao = criar_conexao()
        cursor = conexao.cursor()

        # Se o utilizador preencheu um álbum, verifica se ele realmente existe
        if id_album is not None:
            cursor.execute('SELECT id_album FROM "ALBUM" WHERE id_album = %s', (id_album,))
            if not cursor.fetchone():
                cursor.close()
                conexao.close()

                # Busca os géneros novamente para recarregar a página sem quebrar
                conexao_gen = criar_conexao()
                cursor_gen = conexao_gen.cursor()
                cursor_gen.execute('SELECT id_genero, nome_genero FROM "GENERO"')
                generos = cursor_gen.fetchall()
                cursor_gen.close()
                conexao_gen.close()

                mensagem_erro = "Ops! O álbum com o ID informado não foi encontrado. Por favor, verifique o número ou deixe em branco."
                return render_template("cadastrar_musica.html", generos=generos, erro=mensagem_erro)

        # Se estiver tudo certo, guarda a música
        cursor.execute("""
            INSERT INTO "MUSICA" (titulo, "duração", id_album, id_genero)
            VALUES (%s, %s, %s, %s)
        """, (titulo, duracao, id_album, id_genero))

        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('listar_musicas'))

    # Parte do GET para carregar os géneros no <select>
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT id_genero, nome_genero FROM "GENERO"')
    generos = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template("cadastrar_musica.html", generos=generos)

# 4 - Listar músicas (com JOINs e RealDictCursor para retornar nomes legíveis)


@app.route('/musicas', methods=['GET'])
def listar_musicas():
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    # O LEFT JOIN no ALBUM permite que músicas sem álbum apareçam na lista
    cursor.execute("""
        SELECT 
            m.id_musica AS id,
            m.titulo,
            m."duração" AS duracao,
            al.nome_album AS album,
            g.nome_genero AS genero
        FROM "MUSICA" m
        LEFT JOIN "ALBUM" al ON m.id_album = al.id_album
        JOIN "GENERO" g ON m.id_genero = g.id_genero
        ORDER BY m.id_musica ASC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template("listar_musicas.html", musicas=resultados)

# 5 - Buscar música
@app.route('/musicas/buscar', methods=['GET'])
def buscar_musica():
    titulo = request.args.get('titulo', '')

    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT 
            m.id_musica AS id,
            m.titulo,
            m."duração" AS duracao,
            a.nome_artista AS artista,
            al.nome_album AS album,
            g.nome_genero AS genero
        FROM "MUSICA" m
        LEFT JOIN "ALBUM" al ON m.id_album = al.id_album
        LEFT JOIN "ARTISTA" a ON al.id_artista = a.id_artista
        JOIN "GENERO" g ON m.id_genero = g.id_genero
        WHERE m.titulo ILIKE %s
    """, (f"%{titulo}%",))

    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()

    # Reutiliza o template de listagem para mostrar as músicas encontradas
    return render_template("buscar_musica.html", musicas=resultados)

# 6 - Editar música
@app.route('/musicas/editar/<int:id_musica>', methods=['GET', 'POST'])
def editar_musica(id_musica):
    conexao = criar_conexao()

    if request.method == 'POST':
        titulo = request.form['titulo']
        duracao = request.form['duracao']

        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE "MUSICA"
            SET titulo = %s, "duração" = %s
            WHERE id_musica = %s
        """, (titulo, duracao, id_musica))

        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('listar_musicas'))

    # Se for GET, busca a música para preencher o formulário
    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM "MUSICA" WHERE id_musica = %s', (id_musica,))
    musica = cursor.fetchone()
    cursor.close()
    conexao.close()

    return render_template("editar_musica.html", musica=musica)

# 7 - Excluir música
@app.route('/musicas/deletar/<int:id_musica>', methods=['POST'])
def excluir_musica(id_musica):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM "PLAYLIST_MUSICA" WHERE id_musica = %s
    """, (id_musica,))
    total_playlists = cursor.fetchone()[0]

    if total_playlists > 0:
        print(f"Aviso: A música {id_musica} estava em {total_playlists} playlist(s) e foi removida delas.")

    cursor.execute("""
        DELETE FROM "PLAYLIST_MUSICA" WHERE id_musica = %s
    """, (id_musica,))

    # 3.  a música
    cursor.execute("""
        DELETE FROM "MUSICA" WHERE id_musica = %s
    """, (id_musica,))

    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('listar_musicas'))


# 8 - Criar playlist
@app.route('/playlists', methods=['POST'])
def criar_playlist():
    dados = request.get_json()
    nome_playlist = dados.get('nome_playlist')
    id_usuario = dados.get('id_usuario')

    if not id_usuario:
        return jsonify({"erro": "ID do usuário é obrigatório."}), 400

    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO "PLAYLIST" (nome_playlist, id_usuario)
        VALUES (%s, %s)
        RETURNING id_playlist;
    """, (nome_playlist, id_usuario))

    novo_id = cursor.fetchone()[0]
    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Playlist criada com sucesso!", "id_playlist": novo_id}), 201


# 9 - Listar playlists
@app.route('/playlists', methods=['GET'])
def listar_playlists():
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT p.id_playlist, p.nome_playlist, u.nome_usuario 
        FROM "PLAYLIST" p
        JOIN "USUARIO" u ON p.id_usuario = u.id
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()

    return jsonify(resultados), 200


# 10 - Adicionar música à playlist
@app.route('/playlists/adicionar-musica', methods=['POST'])
def adicionar_musica_playlist():
    dados = request.get_json()
    id_playlist = dados.get('id_playlist')
    id_musica = dados.get('id_musica')

    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO "PLAYLIST_MUSICA" (id_playlist, id_musica)
        VALUES (%s, %s)
    """, (id_playlist, id_musica))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Música adicionada à playlist com sucesso!"}), 201


if __name__ == '__main__':
    app.run(debug=True)