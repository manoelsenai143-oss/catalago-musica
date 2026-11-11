from flask import Flask, jsonify, request, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import criar_conexao


app = Flask(__name__)


@app.route('/')
def pagina_escolha_login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/login/admin')
def login_admin_page():
    return render_template('login_admin.html')

@app.route('/login/musico', methods=['GET', 'POST'])
def login_musico():
    erro = None
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']

        conexao = criar_conexao()
        cursor = conexao.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, nome
            FROM musicos
            WHERE cpf = %s AND senha = %s
        """, (cpf, senha))
        musico = cursor.fetchone()
        cursor.close()
        conexao.close()

        if musico:
            # Redireciona para a home do músico passando o ID diretamente na URL (sem session)
            return redirect(url_for('musico_home', musico_id=musico['id']))
        else:
            erro = "CPF ou senha incorretos."

    return render_template('login_musico.html', erro=erro)

@app.route('/cadastrar_musico', methods=['GET', 'POST'])
def cadastrar_musico():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']

        conexao = criar_conexao()
        cursor = conexao.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT id FROM musicos WHERE cpf = %s', (cpf,))
        musico_existente = cursor.fetchone()

        if musico_existente:
            erro = "Este CPF já está cadastrado."
            cursor.close()
            conexao.close()
        else:
            cursor.execute("""
                INSERT INTO musicos (nome, cpf, senha)
                VALUES (%s, %s, %s)
            """, (nome, cpf, senha))

            conexao.commit()
            cursor.close()
            conexao.close()

            return redirect(url_for('login_musico'))

    return render_template("cadastrar_musico.html", erro=erro)

@app.route('/musico/home/<int:musico_id>', methods=['GET', 'POST'])
def musico_home(musico_id):
    return render_template('musico_home.html', musico_id=musico_id)


@app.route('/musico/musicas/<int:musico_id>', methods=['GET'])
def musico_listar_musicas(musico_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

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
        WHERE m.id_artista = %s
        ORDER BY m.id_musica ASC
    """, (musico_id,))

    musicas = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template('musico_listar.html', musicas=musicas, musico_id=musico_id)


@app.route('/musico/cadastrar_musica/<int:musico_id>', methods=['GET', 'POST'])
def musico_cadastrar_musica(musico_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        titulo = request.form['titulo']
        duracao = request.form['duracao']
        id_album = request.form['id_album'] if request.form['id_album'] else None
        id_genero = request.form['id_genero']

        # Validar se ESTE ARTISTA específico já tem uma música com este título
        cursor.execute('''
            SELECT * FROM "MUSICA" 
            WHERE titulo = %s AND id_artista = %s
        ''', (titulo, musico_id))

        if cursor.fetchone():
            cursor.close()
            conexao.close()
            return "Erro: Já tens uma música cadastrada com este título!", 400

        # Inserir a nova música guardando o id_artista
        cursor.execute('''
            INSERT INTO "MUSICA" (titulo, "duração", id_artista, id_album, id_genero) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (titulo, duracao, musico_id, id_album, id_genero))

        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('musico_listar_musicas', musico_id=musico_id))

    # GET: Buscar álbuns do artista e géneros para preencher o formulário
    cursor.execute('SELECT * FROM "ALBUM" WHERE id_artista = %s', (musico_id,))
    albuns = cursor.fetchall()

    cursor.execute('SELECT * FROM "GENERO"')
    generos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('cadastrar_musica.html', musico_id=musico_id, albuns=albuns, generos=generos)

@app.route('/musico/albuns/<int:musico_id>', methods=['GET'])
def musico_listar_albuns(musico_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    # Filtra apenas os álbuns do artista logado
    cursor.execute('SELECT id_album, nome_album FROM "ALBUM" WHERE id_artista = %s ORDER BY id_album ASC', (musico_id,))
    albuns = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('musico_listar_albuns.html', albuns=albuns, musico_id=musico_id)


# Rota para o Músico criar um novo álbum
@app.route('/musico/albuns/novo/<int:musico_id>', methods=['GET', 'POST'])
def musico_cadastrar_album(musico_id):
    if request.method == 'POST':
        nome_album = request.form['nome_album']
        ano_album = request.form['ano_album']

        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO "ALBUM" (nome_album, ano_album, id_artista)
            VALUES (%s, %s, %s)
        """, (nome_album, ano_album, musico_id))

        conexao.commit()
        cursor.close()
        conexao.close()

        # Redireciona para a home após cadastrar com sucesso
        return redirect(url_for('musico_home', musico_id=musico_id))

    return render_template("musico_cadastrar_album.html", musico_id=musico_id)

@app.route('/musico/albuns/editar/<int:musico_id>/<int:id_album>', methods=['GET', 'POST'])
def atualizar_album(musico_id, id_album):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        nome_album = request.form['nome_album']
        ano_album = request.form['ano_album']

        # Atualiza o álbum garantindo que pertence a este artista
        cursor.execute(
            '''UPDATE "ALBUM" 
               SET nome_album = %s, ano_album = %s 
               WHERE id_album = %s AND id_artista = %s''',
            (nome_album, ano_album, id_album, musico_id)
        )
        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('musico_listar_albuns', musico_id=musico_id))

    # GET: Buscar dados atuais do álbum para preencher o formulário
    cursor.execute('SELECT * FROM "ALBUM" WHERE id_album = %s AND id_artista = %s', (id_album, musico_id))
    album = cursor.fetchone()

    cursor.close()
    conexao.close()

    return render_template('editar_album.html', album=album, musico_id=musico_id)

@app.route('/musico/albuns/excluir/<int:musico_id>/<int:id_album>', methods=['POST'])
def musico_excluir_album(musico_id, id_album):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    try:
        # 1. Apaga primeiro as músicas associadas a este álbum para evitar o erro de chave estrangeira
        cursor.execute('DELETE FROM "MUSICA" WHERE id_album = %s', (id_album,))

        # 2. Agora apaga o álbum com segurança
        cursor.execute('DELETE FROM "ALBUM" WHERE id_album = %s AND id_artista = %s', (id_album, musico_id))

        conexao.commit()
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao excluir álbum: {e}")
    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for('musico_listar_albuns', musico_id=musico_id))


@app.route('/musico/musicas/excluir/<int:musico_id>/<int:id_musica>', methods=['POST'])
def musico_excluir_musica(musico_id, id_musica):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM "MUSICA" WHERE id_musica = %s', (id_musica,))

    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('musico_listar_musicas', musico_id=musico_id))


@app.route('/musico/musicas/editar/<int:musico_id>/<int:id_musica>', methods=['GET', 'POST'])
def atualizar_musico(musico_id, id_musica):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        novo_titulo = request.form['titulo']
        nova_duracao = request.form['duracao']
        novo_genero = request.form['id_genero']
        novo_album = request.form['id_album'] if request.form['id_album'] else None

        cursor.execute(
            '''UPDATE "MUSICA" 
               SET titulo = %s, "duração" = %s, id_genero = %s, id_album = %s 
               WHERE id_musica = %s AND id_artista = %s''',
            (novo_titulo, nova_duracao, novo_genero, novo_album, id_musica, musico_id)
        )
        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('musico_listar_musicas', musico_id=musico_id))

    # GET: Buscar dados atuais da música
    cursor.execute('SELECT * FROM "MUSICA" WHERE id_musica = %s AND id_artista = %s', (id_musica, musico_id))
    musica = cursor.fetchone()

    cursor.execute('SELECT id_genero, nome_genero FROM "GENERO"')
    generos = cursor.fetchall()

    cursor.execute('SELECT id_album, nome_album FROM "ALBUM" WHERE id_artista = %s', (musico_id,))
    albuns = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('editar_musica.html', musica=musica, generos=generos, albuns=albuns, musico_id=musico_id)



@app.route('/login/usuario', methods=['GET', 'POST'])
def login_usuario():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = criar_conexao()
        cursor = conexao.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, nome_usuario, email
            FROM "USUARIO"
            WHERE email = %s AND senha = %s
        """, (email, senha))

        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario:
            return redirect(url_for('usuario_home'))
        else:
            erro = "Email ou senha incorretos."

    return render_template('login_usuario.html', erro=erro)


# 1 - Cadastrar usuário
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
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

        return redirect(url_for('login_usuario'))

    return render_template("cadastrar_usuario.html")


# Rota de Login (GET mostra o formulário, POST valida no banco)

@app.route('/usuario/home')
def usuario_home():
    # Aqui pode depois verificar se o utilizador está logado, se necessário
    return render_template('usuario_home.html')

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

    return render_template("buscar_musica.html", musicas=resultados)

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


# 8 - Criar playlist
@app.route('/playlists/novo', methods=['GET', 'POST'])
def criar_playlist():
    if request.method == 'POST':
        nome_playlist = request.form['nome_playlist']
        id_usuario = request.form['id_usuario']

        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO "PLAYLIST" (nome_playlist, id_usuario)
            VALUES (%s, %s)
        """, (nome_playlist, id_usuario))

        conexao.commit()
        cursor.close()
        conexao.close()

        # Alterado para redirecionar para a lista de playlists
        return redirect(url_for('listar_playlists'))

    return render_template("criar_playlist.html")

# 9 - Listar playlists
@app.route('/playlists', methods=['GET'])
def listar_playlists():
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    # Usamos o LEFT JOIN para trazer as músicas e o STRING_AGG para agrupá-las
    cursor.execute("""
        SELECT 
            p.id_playlist, 
            p.nome_playlist, 
            u.nome_usuario,
            STRING_AGG(m.titulo, ', ') AS musicas
        FROM "PLAYLIST" p
        JOIN "USUARIO" u ON p.id_usuario = u.id
        JOIN "PLAYLIST_MUSICA" pm ON p.id_playlist = pm.id_playlist
        JOIN "MUSICA" m ON pm.id_musica = m.id_musica
        GROUP BY p.id_playlist, p.nome_playlist, u.nome_usuario
        ORDER BY p.id_playlist ASC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template("listar_playlists.html", playlists=resultados)


# 10 - Adicionar música à playlist
@app.route('/playlists/adicionar-musica', methods=['GET', 'POST'])
def adicionar_musica_playlist():
    conexao = criar_conexao()

    if request.method == 'POST':
        id_playlist = request.form.get('id_playlist')
        id_musica = request.form.get('id_musica')

        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO "PLAYLIST_MUSICA" (id_playlist, id_musica)
            VALUES (%s, %s)
        """, (id_playlist, id_musica))

        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('listar_playlists'))

    # GET: Busca as playlists e as músicas para preencher os menus <select>
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT id_playlist, nome_playlist FROM "PLAYLIST"')
    playlists = cursor.fetchall()

    cursor.execute('SELECT id_musica, titulo FROM "MUSICA"')
    musicas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("adicionar_musica_playlist.html", playlists=playlists, musicas=musicas)


if __name__ == '__main__':
    app.run(debug=True)