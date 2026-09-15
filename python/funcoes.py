def mostrar_musicas(musicas):
    for musica in musicas:
        print(f"Título: {musica['titulo']}")
        print(f"Artista: {musica['artista']}")
        print(f"Álbum: {musica['album']}")
        print(f"Gênero: {musica['genero']}")
        print()


def menu():
    print("================================")
    print("       CATÁLOGO DE MÚSICA")
    print("================================")
    print()
    print("1 - Cadastrar música")
    print("2 - Listar músicas")
    print("3 - Buscar música")
    print("4 - Editar música")
    print("5 - Excluir música")
    print("6 - Criar playlist")
    print("7 - Listar playlists")
    print("8 - Adicionar música à playlist")
    print("0 - Sair")


def cadastrar_musica(cursor, conexao):
    titulo = input("Digite o título da música: ")
    artista = input("Digite o artista: ")
    album = input("Digite o álbum: ")
    genero = input("Digite o gênero: ")

    cursor.execute("""
    INSERT INTO musicas (titulo, artista, album, genero)
    VALUES (?, ?, ?, ?)
    """, (titulo, artista, album, genero))

    conexao.commit()

    print("Música cadastrada com sucesso!")


def buscar_musica(cursor):
    titulo = input("Digite o título da música: ")

    cursor.execute("""
    SELECT * FROM musicas
    WHERE titulo LIKE ?
    """, (f"%{titulo}%",))

    resultados = cursor.fetchall()

    if resultados:
        for musica in resultados:
            print(f"ID: {musica[0]}")
            print(f"Título: {musica[1]}")
            print(f"Artista: {musica[2]}")
            print(f"Álbum: {musica[3]}")
            print(f"Gênero: {musica[4]}")
            print()
    else:
        print("Música não encontrada.")


def editar_musica(cursor, conexao):
    id_musica = input("Digite o ID da música que deseja editar: ")

    cursor.execute(
        "SELECT * FROM musicas WHERE id = ?",
        (id_musica,)
    )

    musica = cursor.fetchone()

    if musica:
        titulo = input("Digite o novo título: ")
        artista = input("Digite o novo artista: ")
        album = input("Digite o novo álbum: ")
        genero = input("Digite o novo gênero: ")

        cursor.execute("""
        UPDATE musicas
        SET titulo = ?, artista = ?, album = ?, genero = ?
        WHERE id = ?
        """, (titulo, artista, album, genero, id_musica))

        conexao.commit()

        print("Música editada com sucesso!")
    else:
        print("Música não encontrada.")


def excluir_musica(cursor, conexao):
    id_musica = input("Digite o ID da música que deseja excluir: ")

    cursor.execute(
        "SELECT * FROM musicas WHERE id = ?",
        (id_musica,)
    )

    musica = cursor.fetchone()

    if musica:
        confirmacao = input("Tem certeza que deseja excluir? (s/n): ")

        if confirmacao.lower() == "s":
            cursor.execute(
                "DELETE FROM musicas WHERE id = ?",
                (id_musica,)
            )

            conexao.commit()

            print("Música excluída com sucesso!")
        else:
            print("Exclusão cancelada.")
    else:
        print("Música não encontrada.")


def criar_playlist(cursor, conexao):
    nome = input("Digite o nome da playlist: ")

    cursor.execute("""
    INSERT INTO playlists (nome)
    VALUES (?)
    """, (nome,))

    conexao.commit()

    print("Playlist criada com sucesso!")


def listar_playlists(cursor):
    cursor.execute("SELECT * FROM playlists")

    playlists = cursor.fetchall()

    if playlists:
        for playlist in playlists:
            print(f"ID: {playlist[0]}")
            print(f"Nome: {playlist[1]}")

            cursor.execute("""
            SELECT musicas.titulo
            FROM musicas
            INNER JOIN playlist_musicas
            ON musicas.id = playlist_musicas.id_musica
            WHERE playlist_musicas.id_playlist = ?
            """, (playlist[0],))

            musicas = cursor.fetchall()

            if musicas:
                print("Músicas:")

                for musica in musicas:
                    print(f"- {musica[0]}")
            else:
                print("Nenhuma música nessa playlist.")

            print()
    else:
        print("Nenhuma playlist cadastrada.")


def adicionar_musica_playlist(cursor, conexao):
    id_playlist = input("Digite o ID da playlist: ")
    id_musica = input("Digite o ID da música: ")

    cursor.execute("""
    SELECT * FROM playlists
    WHERE id = ?
    """, (id_playlist,))

    playlist = cursor.fetchone()

    cursor.execute("""
    SELECT * FROM musicas
    WHERE id = ?
    """, (id_musica,))

    musica = cursor.fetchone()

    if playlist and musica:
        cursor.execute("""
        SELECT * FROM playlist_musicas
        WHERE id_playlist = ? AND id_musica = ?
        """, (id_playlist, id_musica))

        existe = cursor.fetchone()

        if existe:
            print("Essa música já está nessa playlist.")
        else:
            cursor.execute("""
            INSERT INTO playlist_musicas (id_playlist, id_musica)
            VALUES (?, ?)
            """, (id_playlist, id_musica))

            conexao.commit()

            print("Música adicionada à playlist!")
    else:
        print("Playlist ou música não encontrada.")


def listar_musicas(cursor):
    cursor.execute("SELECT * FROM musicas")
    resultados = cursor.fetchall()

    if resultados:
        for musica in resultados:
            print(f"ID: {musica[0]}")
            print(f"Título: {musica[1]}")
            print(f"Artista: {musica[2]}")
            print(f"Álbum: {musica[3]}")
            print(f"Gênero: {musica[4]}")
            print()
    else:
        print("Nenhuma música cadastrada.")




