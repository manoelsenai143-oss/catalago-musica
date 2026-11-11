
import psycopg2
from faker import Faker
import random

fake = Faker("pt_BR")

conexao_postgres = psycopg2.connect(
    host="127.0.0.1",
    database="catalago_musica",
    user="postgres",
    password="1234",
    port="5432",
    client_encoding="UTF8"
)

cursor_postgres = conexao_postgres.cursor()

try:

    cursor_postgres.execute('SELECT id FROM "USUARIO"')
    usuarios = [linha[0] for linha in cursor_postgres.fetchall()]

    cursor_postgres.execute('SELECT id_artista, nome_artista FROM "ARTISTA"')
    artistas = cursor_postgres.fetchall()

    cursor_postgres.execute('SELECT id_genero, nome_genero FROM "GENERO"')
    generos = cursor_postgres.fetchall()

    cursor_postgres.execute('SELECT id_album, nome_album, id_artista FROM "ALBUM"')
    albuns = cursor_postgres.fetchall()

    cursor_postgres.execute('SELECT titulo FROM "MUSICA"')
    titulos_musicas = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT nome_usuario FROM "USUARIO"')
    nomes_usuarios = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT email FROM "USUARIO"')
    emails = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT nome_artista FROM "ARTISTA"')
    nomes_artistas = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT nome_genero FROM "GENERO"')
    nomes_generos = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT nome_album, id_artista FROM "ALBUM"')
    albuns_existentes = set(cursor_postgres.fetchall())

    cursor_postgres.execute('SELECT nome_playlist FROM "PLAYLIST"')
    nomes_playlists = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT COUNT(*) FROM "MUSICA"')
    qtd_musicas = cursor_postgres.fetchone()[0]

    cursor_postgres.execute('SELECT COUNT(*) FROM "PLAYLIST"')
    qtd_playlists = cursor_postgres.fetchone()[0]

    cursor_postgres.execute('SELECT id_playlist, id_musica FROM "PLAYLIST_MUSICA"')
    relacoes = set(cursor_postgres.fetchall())

    while len(usuarios) < 100:

        nome = fake.user_name() + str(random.randint(100, 999))

        while nome in nomes_usuarios:
            nome = fake.user_name() + str(random.randint(100, 999))

        email = fake.unique.email()

        while email in emails:
            email = fake.unique.email()

        cursor_postgres.execute("""
            INSERT INTO "USUARIO" (nome_usuario, email, senha)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nome, email, fake.password()))

        usuarios.append(cursor_postgres.fetchone()[0])

        nomes_usuarios.add(nome)
        emails.add(email)

    while len(artistas) < 100:

        nome_artista = fake.name()

        while nome_artista in nomes_artistas:
            nome_artista = fake.name()

        cursor_postgres.execute("""
            INSERT INTO "ARTISTA" (nome_artista)
            VALUES (%s)
            RETURNING id_artista
        """, (nome_artista,))

        artistas.append((
            cursor_postgres.fetchone()[0],
            nome_artista
        ))

        nomes_artistas.add(nome_artista)

    while len(generos) < 100:

        nome_genero = "Gênero fictício " + str(len(generos) + 1)

        while nome_genero in nomes_generos:
            nome_genero = "Gênero fictício " + str(random.randint(100, 999999))

        cursor_postgres.execute("""
            INSERT INTO "GENERO" (nome_genero)
            VALUES (%s)
            RETURNING id_genero
        """, (nome_genero,))

        generos.append((
            cursor_postgres.fetchone()[0],
            nome_genero
        ))

        nomes_generos.add(nome_genero)

    while len(albuns) < 100:

        artista = random.choice(artistas)

        nome_album = fake.catch_phrase()

        while (nome_album, artista[0]) in albuns_existentes:
            nome_album = fake.catch_phrase()

        ano_album = random.randint(1990, 2026)

        cursor_postgres.execute("""
            INSERT INTO "ALBUM" (nome_album, ano_album, id_artista)
            VALUES (%s, %s, %s)
            RETURNING id_album
        """, (nome_album, ano_album, artista[0]))

        albuns.append((
            cursor_postgres.fetchone()[0],
            nome_album,
            artista[0]
        ))

        albuns_existentes.add((nome_album, artista[0]))

    while qtd_musicas < 100:

        titulo = fake.sentence(nb_words=3).replace(".", "")

        while titulo in titulos_musicas:
            titulo = fake.sentence(nb_words=3).replace(".", "")

        duracao = random.randint(120, 300)

        album = random.choice(albuns)
        genero = random.choice(generos)

        cursor_postgres.execute("""
            INSERT INTO "MUSICA"
            (titulo, "duração", id_album, id_genero)
            VALUES (%s, %s, %s, %s)
        """, (titulo, duracao, album[0], genero[0]))

        titulos_musicas.add(titulo)
        qtd_musicas += 1

    while qtd_playlists < 100:

        nome_playlist = fake.word().capitalize() + " Mix"

        while nome_playlist in nomes_playlists:
            nome_playlist = fake.word().capitalize() + " Mix " + str(random.randint(1, 999999))

        id_usuario = random.choice(usuarios)

        cursor_postgres.execute("""
            INSERT INTO "PLAYLIST" (nome_playlist, id_usuario)
            VALUES (%s, %s)
        """, (nome_playlist, id_usuario))

        nomes_playlists.add(nome_playlist)
        qtd_playlists += 1

    cursor_postgres.execute('SELECT id_musica FROM "MUSICA"')
    ids_musicas = [linha[0] for linha in cursor_postgres.fetchall()]

    cursor_postgres.execute('SELECT id_playlist FROM "PLAYLIST"')
    ids_playlists = [linha[0] for linha in cursor_postgres.fetchall()]

    while len(relacoes) < 100:

        relacao = (
            random.choice(ids_playlists),
            random.choice(ids_musicas)
        )

        if relacao not in relacoes:

            cursor_postgres.execute("""
                INSERT INTO "PLAYLIST_MUSICA" (id_playlist, id_musica)
                VALUES (%s, %s)
            """, relacao)

            relacoes.add(relacao)

    conexao_postgres.commit()

    print("Dados adicionados com sucesso!")
    print()
    print("POSTGRESQL")

    print("Usuários:", len(usuarios))
    print("Artistas:", len(artistas))
    print("Gêneros:", len(generos))
    print("Álbuns:", len(albuns))
    print("Músicas:", qtd_musicas)
    print("Playlists:", qtd_playlists)
    print("Playlist/Música:", len(relacoes))

except Exception as erro:

    conexao_postgres.rollback()

    print("Ocorreu um erro:")
    print(erro)

finally:

    cursor_postgres.close()
    conexao_postgres.close()
