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

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin_page():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        if usuario == "admin" and senha == "admin123":
            return redirect(url_for('admin_home'))
        else:
            erro = "Utilizador ou senha de administrador incorretos."
    return render_template('login_admin.html', erro=erro)



@app.route('/admin/home', methods=['GET'])
def admin_home():
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT COUNT(*) AS total FROM "USUARIO"')
    total_usuarios = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM musicos')
    total_musicos = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM "MUSICA"')
    total_musicas = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM "ALBUM"')
    total_albuns = cursor.fetchone()['total']

    cursor.close()
    conexao.close()

    return render_template(
        'admin_home.html',
        total_usuarios=total_usuarios,
        total_musicos=total_musicos,
        total_musicas=total_musicas,
        total_albuns=total_albuns
    )





# Listar e Adicionar Gêneros
@app.route('/admin/generos', methods=['GET', 'POST'])
def admin_gerenciar_generos():
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        nome_genero = request.form.get('nome_genero')
        if nome_genero:
            cursor.execute('INSERT INTO "GENERO" (nome_genero) VALUES (%s)', (nome_genero,))
            conexao.commit()

        cursor.close()
        conexao.close()
        return redirect(url_for('admin_gerenciar_generos'))

    cursor.execute('SELECT * FROM "GENERO" ORDER BY id_genero ASC')
    generos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('admin_generos.html', generos=generos)


# Excluir Gênero
@app.route('/admin/generos/excluir/<int:id_genero>', methods=['POST'])
def admin_excluir_genero(id_genero):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute('DELETE FROM "GENERO" WHERE id_genero = %s', (id_genero,))
        conexao.commit()
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao excluir gênero: {e}")
    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for('admin_gerenciar_generos'))



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
            # 1. Insere na tabela musicos e obtém o ID gerado
            cursor.execute("""
                INSERT INTO musicos (nome, cpf, senha)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (nome, cpf, senha))

            # Como estás a usar RealDictCursor, o resultado é um dicionário
            novo_id = cursor.fetchone()['id']

            # 2. Insere na tabela ARTISTA com o mesmo ID (usando OVERRIDING SYSTEM VALUE)
            cursor.execute("""
                INSERT INTO "ARTISTA" (id_artista, nome_artista)
                OVERRIDING SYSTEM VALUE
                VALUES (%s, %s)
            """, (novo_id, nome))

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
        titulo = request.form.get('titulo')
        duracao = request.form.get('duracao')
        id_album = request.form.get('id_album') if request.form.get('id_album') else None
        id_genero = request.form.get('id_genero')

        # Guarda a música associando diretamente o musico_id como id_artista
        cursor.execute('''
            INSERT INTO "MUSICA" (titulo, "duração", id_album, id_genero, id_artista) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (titulo, duracao, id_album, id_genero, musico_id))

        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect(url_for('musico_listar_musicas', musico_id=musico_id))

    # GET: Busca álbuns e géneros filtrados diretamente pelo musico_id
    cursor.execute('SELECT * FROM "ALBUM" WHERE id_artista = %s', (musico_id,))
    albuns = cursor.fetchall()

    cursor.execute('SELECT * FROM "GENERO"')
    generos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        'cadastrar_musica.html',
        musico_id=musico_id,
        albuns=albuns,
        generos=generos
    )


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

        return redirect(url_for('musico_listar_albuns', musico_id=musico_id))

    return render_template("musico_cadastrar_album.html", musico_id=musico_id)




@app.route('/musico/albuns/<int:musico_id>', methods=['GET'])
def musico_listar_albuns(musico_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    # Usa o musico_id diretamente como id_artista!
    cursor.execute("""
        SELECT id_album, nome_album, ano_album 
        FROM "ALBUM" 
        WHERE id_artista = %s 
        ORDER BY id_album ASC
    """, (musico_id,))

    albuns = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template('musico_listar_albuns.html', albuns=albuns, musico_id=musico_id)

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
        # 1. Encontra todas as músicas que pertencem a este álbum
        cursor.execute('SELECT id_musica FROM "MUSICA" WHERE id_album = %s', (id_album,))
        musicas_album = cursor.fetchall()

        # 2. Para cada música do álbum, apaga primeiro as ligações na tabela "PLAYLIST_MUSICA"
        for musica in musicas_album:
            id_musica = musica['id_musica'] if isinstance(musica, dict) else musica[0]
            cursor.execute('DELETE FROM "PLAYLIST_MUSICA" WHERE id_musica = %s', (id_musica,))

        # 3. Agora já podes apagar as músicas associadas a este álbum
        cursor.execute('DELETE FROM "MUSICA" WHERE id_album = %s', (id_album,))

        # 4. Por fim, apaga o álbum com segurança
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

    try:
        # 1. Apaga primeiro as associações desta música nas playlists
        cursor.execute('DELETE FROM "PLAYLIST_MUSICA" WHERE id_musica = %s', (id_musica,))

        # 2. Agora apaga a música com segurança
        cursor.execute('DELETE FROM "MUSICA" WHERE id_musica = %s', (id_musica,))

        conexao.commit()
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao excluir música: {e}")
    finally:
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

    cursor.execute('SELECT id_genero, nome_genero FROM "GENERO" ORDER BY id_genero ASC')
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
        email = request.form.get('email')
        senha = request.form.get('senha')

        conexao = criar_conexao()
        cursor = conexao.cursor(cursor_factory=RealDictCursor)

        # Procura o utilizador pelo email e senha
        cursor.execute("""
            SELECT * FROM "USUARIO" WHERE email = %s AND senha = %s
        """, (email, senha))

        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario:
            # SUCESSO: O utilizador existe!
            # Vais buscar o ID dele (ex: usuario['id']) e passas no url_for:
            return redirect(url_for('usuario_home', usuario_id=usuario['id']))
        else:
            erro = "Email ou senha incorretos."

    return render_template("login_usuario.html", erro=erro)


# 1 - Cadastrar usuário
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome_usuario']
        email = request.form['email']
        senha = request.form['senha']

        conexao = criar_conexao()
        cursor = conexao.cursor(cursor_factory=RealDictCursor)

        # Verifica APENAS se o email já existe na base de dados
        cursor.execute("""
            SELECT * FROM "USUARIO" 
            WHERE email = %s
        """, (email,))

        usuario_existente = cursor.fetchone()

        if usuario_existente:
            erro = "Este email já está a ser utilizado por outra conta."
            cursor.close()
            conexao.close()
        else:
            # Se o email for único, permite o cadastro (mesmo que o nome seja igual)
            cursor.execute("""
                INSERT INTO "USUARIO" (nome_usuario, email, senha)
                VALUES (%s, %s, %s)
            """, (nome, email, senha))

            conexao.commit()
            cursor.close()
            conexao.close()

            return redirect(url_for('login_usuario'))

    return render_template("cadastrar_usuario.html", erro=erro)


@app.route('/usuario/<int:usuario_id>/home')
def usuario_home(usuario_id):
    # Envia o usuario_id para o HTML do painel
    return render_template("usuario_home.html", usuario_id=usuario_id)

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
                cursor.execute('SELECT id_genero, nome_genero FROM "GENERO" ORDER BY id_genero ASC')
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

    # Query corrigida com COALESCE completo para encontrar o artista pelo álbum, pela música ou pela tabela de músicos
    cursor.execute("""
        SELECT 
            m.id_musica AS id,
            m.titulo,
            m."duração" AS duracao,
            COALESCE(art.nome_artista, art_direto.nome_artista, mus.nome, 'Desconhecido') AS artista,
            COALESCE(al.nome_album, 'Sem Álbum') AS album,
            g.nome_genero AS genero
        FROM "MUSICA" m
        LEFT JOIN "ALBUM" al ON m.id_album = al.id_album
        LEFT JOIN "ARTISTA" art ON al.id_artista = art.id_artista
        LEFT JOIN "ARTISTA" art_direto ON m.id_artista = art_direto.id_artista
        LEFT JOIN musicos mus ON m.id_artista = mus.id
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

@app.route('/usuario/<int:usuario_id>/cadastrar_playlist', methods=['GET'])
def cadastrar_playlist_form(usuario_id):
    return render_template("cadastrar_playlist.html", usuario_id=usuario_id)

# 8 - Criar playlist
@app.route('/usuario/<int:usuario_id>/salvar_playlist', methods=['POST'])
def criar_playlist(usuario_id):
    nome_playlist = request.form.get('nome_playlist')

    if nome_playlist:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        # IMPORTANTE: Usa id_usuario aqui!
        cursor.execute("""
            INSERT INTO "PLAYLIST" (nome_playlist, id_usuario)
            VALUES (%s, %s)
        """, (nome_playlist, usuario_id))

        conexao.commit()
        cursor.close()
        conexao.close()

    return redirect(url_for('listar_playlists', usuario_id=usuario_id))

# 9 - Listar playlists
@app.route('/usuario/<int:usuario_id>/playlists')
def listar_playlists(usuario_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM "PLAYLIST" WHERE id_usuario = %s', (usuario_id,))
    playlists = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("listar_playlists.html", playlists=playlists, usuario_id=usuario_id)

# 10 - Adicionar música à playlist
# 10 - Adicionar música à playlist
@app.route('/usuario/<int:usuario_id>/playlist/<int:playlist_id>/adicionar-musica', methods=['GET', 'POST'])
def adicionar_musica_playlist(usuario_id, playlist_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        id_musica = request.form.get('id_musica')
        if id_musica:
            cursor.execute("""
                INSERT INTO "PLAYLIST_MUSICA" (id_playlist, id_musica)
                VALUES (%s, %s)
            """, (playlist_id, id_musica))
            conexao.commit()

        cursor.close()
        conexao.close()
        return redirect(url_for('detalhes_playlist', usuario_id=usuario_id, playlist_id=playlist_id))

    # Consulta SQL robusta que procura o artista pelo álbum, pela ligação direta ou pela tabela de músicos
    cursor.execute("""
        SELECT 
            m.id_musica,
            m.titulo,
            COALESCE(ar.nome_artista, art_direto.nome_artista, mus.nome, 'Desconhecido') AS artista,
            COALESCE(al.nome_album, 'Sem Álbum') AS album
        FROM "MUSICA" m
        LEFT JOIN "ALBUM" al ON m.id_album = al.id_album
        LEFT JOIN "ARTISTA" ar ON al.id_artista = ar.id_artista
        LEFT JOIN "ARTISTA" art_direto ON m.id_artista = art_direto.id_artista
        LEFT JOIN musicos mus ON m.id_artista = mus.id
        ORDER BY m.titulo ASC
    """)
    musicas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        'adicionar_musica_playlist.html',
        usuario_id=usuario_id,
        playlist_id=playlist_id,
        musicas=musicas
    )


@app.route('/usuario/<int:usuario_id>/playlist/<int:playlist_id>/excluir', methods=['POST'])
def excluir_playlist(usuario_id, playlist_id):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    # 1. Apaga primeiro as ligações na tabela intermédia para evitar o erro de chave estrangeira
    cursor.execute('DELETE FROM "PLAYLIST_MUSICA" WHERE id_playlist = %s', (playlist_id,))

    # 2. Apaga a playlist
    cursor.execute('DELETE FROM "PLAYLIST" WHERE id_playlist = %s AND id_usuario = %s', (playlist_id, usuario_id))

    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('listar_playlists', usuario_id=usuario_id))



@app.route('/usuario/<int:usuario_id>/playlist/<int:playlist_id>')
def detalhes_playlist(usuario_id, playlist_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    # 1. Busca os dados da playlist
    cursor.execute('SELECT * FROM "PLAYLIST" WHERE id_playlist = %s AND id_usuario = %s', (playlist_id, usuario_id))
    playlist = cursor.fetchone()

    if not playlist:
        cursor.close()
        conexao.close()
        return "Playlist não encontrada", 404

    # 2. Busca as músicas da playlist incluindo o Artista diretamente (funciona com ou sem álbum!)
    cursor.execute("""
        SELECT 
            m.id_musica,
            m.titulo,
            m."duração" AS duracao,
            g.nome_genero AS genero,
            COALESCE(al.nome_album, 'Sem Álbum') AS album,
            COALESCE(art.nome_artista, mus.nome, 'Desconhecido') AS artista
        FROM "PLAYLIST_MUSICA" pm
        JOIN "MUSICA" m ON pm.id_musica = m.id_musica
        JOIN "GENERO" g ON m.id_genero = g.id_genero
        LEFT JOIN "ALBUM" al ON m.id_album = al.id_album
        LEFT JOIN "ARTISTA" art ON m.id_artista = art.id_artista
        LEFT JOIN musicos mus ON m.id_artista = mus.id
        WHERE pm.id_playlist = %s
    """, (playlist_id,))
    musicas_playlist = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("detalhes_playlist.html", playlist=playlist, musicas_playlist=musicas_playlist, usuario_id=usuario_id)



@app.route('/usuario/<int:usuario_id>/playlist/<int:playlist_id>/remover-musica/<int:musica_id>', methods=['POST'])
def remover_musica_playlist(usuario_id, playlist_id, musica_id):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    # Apaga apenas a associação entre esta playlist e esta música
    cursor.execute("""
        DELETE FROM "PLAYLIST_MUSICA" 
        WHERE id_playlist = %s AND id_musica = %s
    """, (playlist_id, musica_id))

    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('detalhes_playlist', usuario_id=usuario_id, playlist_id=playlist_id))


@app.route('/usuario/<int:usuario_id>/playlist/<int:playlist_id>/editar', methods=['GET', 'POST'])
def editar_playlist(usuario_id, playlist_id):
    conexao = criar_conexao()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        novo_nome = request.form.get('nome_playlist')
        cursor.execute("""
            UPDATE "PLAYLIST" 
            SET nome_playlist = %s 
            WHERE id_playlist = %s AND id_usuario = %s
        """, (novo_nome, playlist_id, usuario_id))
        conexao.commit()
        cursor.close()
        conexao.close()
        return redirect(url_for('listar_playlists', usuario_id=usuario_id))

    # Busca os dados atuais da playlist para preencher o formulário
    cursor.execute('SELECT * FROM "PLAYLIST" WHERE id_playlist = %s AND id_usuario = %s', (playlist_id, usuario_id))
    playlist = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not playlist:
        return "Playlist não encontrada", 404

    return render_template('editar_playlist.html', playlist=playlist, usuario_id=usuario_id)


if __name__ == '__main__':
    app.run(debug=True)