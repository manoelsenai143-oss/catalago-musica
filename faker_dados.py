import os
import psycopg2
from faker import Faker
import random
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env (ligação do Neon)
load_dotenv()

fake = Faker("pt_BR")

# Liga-se diretamente à base de dados configurada no .env (Neon)
conexao_postgres = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    client_encoding="UTF8"
)

cursor_postgres = conexao_postgres.cursor()

try:
    print("A iniciar o preenchimento seguro de todas as tabelas...")

    # -------------------------------------------------------------
    # 1. MÚSICOS E ARTISTAS (Sincronizados a partir do ID 1)
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT id_artista, nome_artista FROM "ARTISTA"')
    artistas = cursor_postgres.fetchall()
    nomes_artistas = {linha[1] for linha in artistas}

    # Garante pelo menos 20 músicos/artistas verificando diretamente a tabela ARTISTA
    while len(artistas) < 20:
        nome_musico = fake.name()
        while nome_musico in nomes_artistas:
            nome_musico = fake.name()

        cpf_falso = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
        senha_padrao = "123456"

        try:
            # Insere na tabela de login (musicos)
            cursor_postgres.execute("""
                INSERT INTO musicos (nome, cpf, senha)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (nome_musico, cpf_falso, senha_padrao))

            novo_id = cursor_postgres.fetchone()[0]

            # Insere na tabela "ARTISTA" com o MESMO ID (usando OVERRIDING SYSTEM VALUE)
            cursor_postgres.execute("""
                INSERT INTO "ARTISTA" (id_artista, nome_artista)
                OVERRIDING SYSTEM VALUE
                VALUES (%s, %s)
            """, (novo_id, nome_musico))

            artistas.append((novo_id, nome_musico))
            nomes_artistas.add(nome_musico)

        except Exception as e:
            print(f"\n[ERRO DETALHADO NO ARTISTA/MÚSICO]: {repr(e)}")
            raise e

    if not artistas:
        raise Exception("Erro crítico: A tabela 'ARTISTA' ficou vazia!")

    # -------------------------------------------------------------
    # 2. UTILIZADORES
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT id FROM "USUARIO"')
    usuarios = [linha[0] for linha in cursor_postgres.fetchall()]

    cursor_postgres.execute('SELECT nome_usuario FROM "USUARIO"')
    nomes_usuarios = {linha[0] for linha in cursor_postgres.fetchall()}

    cursor_postgres.execute('SELECT email FROM "USUARIO"')
    emails = {linha[0] for linha in cursor_postgres.fetchall()}

    while len(usuarios) < 50:
        nome = fake.user_name() + str(random.randint(100, 999))
        while nome in nomes_usuarios:
            nome = fake.user_name() + str(random.randint(100, 999))

        email = fake.unique.email()
        while email in emails:
            email = fake.unique.email()

        try:
            cursor_postgres.execute("""
                INSERT INTO "USUARIO" (nome_usuario, email, senha)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (nome, email, fake.password()))

            usuarios.append(cursor_postgres.fetchone()[0])
            nomes_usuarios.add(nome)
            emails.add(email)
        except Exception as e:
            print(f"\n[ERRO DETALHADO NO UTILIZADOR]: {repr(e)}")
            raise e

    # -------------------------------------------------------------
    # 3. GÉNEROS
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT id_genero, nome_genero FROM "GENERO"')
    generos = cursor_postgres.fetchall()
    nomes_generos = {linha[1] for linha in generos}

    while len(generos) < 20:
        nome_genero = "Gênero " + fake.word().capitalize() + str(random.randint(1, 999))
        while nome_genero in nomes_generos:
            nome_genero = "Gênero " + fake.word().capitalize() + str(random.randint(1, 999))

        try:
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
        except Exception as e:
            print(f"\n[ERRO DETALHADO NO GÉNERO]: {repr(e)}")
            raise e

    # -------------------------------------------------------------
    # 4. ÁLBUNS
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT id_album, nome_album, id_artista FROM "ALBUM"')
    albuns = cursor_postgres.fetchall()
    albuns_existentes = {(linha[1], linha[2]) for linha in albuns}

    while len(albuns) < 40:
        if not artistas:
            raise Exception("A lista de artistas está vazia, não é possível criar álbuns.")

        artista = random.choice(artistas)
        nome_album = fake.catch_phrase()
        while (nome_album, artista[0]) in albuns_existentes:
            nome_album = fake.catch_phrase()

        ano_album = random.randint(1990, 2026)

        try:
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
        except Exception as e:
            print(f"\n[ERRO DETALHADO NO ÁLBUM]: {repr(e)}")
            raise e

    # -------------------------------------------------------------
    # 5. MÚSICAS
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT COUNT(*) FROM "MUSICA"')
    qtd_musicas = cursor_postgres.fetchone()[0]

    cursor_postgres.execute('SELECT titulo FROM "MUSICA"')
    titulos_musicas = {linha[0] for linha in cursor_postgres.fetchall()}

    while qtd_musicas < 80:
        if not albuns or not generos:
            raise Exception("Faltam álbuns ou géneros para criar músicas.")

        titulo = fake.sentence(nb_words=3).replace(".", "")
        while titulo in titulos_musicas:
            titulo = fake.sentence(nb_words=3).replace(".", "")

        duracao = random.randint(120, 300)
        album = random.choice(albuns)
        genero = random.choice(generos)

        try:
            cursor_postgres.execute("""
                INSERT INTO "MUSICA"
                (titulo, "duração", id_album, id_genero)
                VALUES (%s, %s, %s, %s)
            """, (titulo, duracao, album[0], genero[0]))

            titulos_musicas.add(titulo)
            qtd_musicas += 1
        except Exception as e:
            print(f"\n[ERRO DETALHADO NA MÚSICA]: {repr(e)}")
            raise e

    # -------------------------------------------------------------
    # 6. PLAYLISTS
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT COUNT(*) FROM "PLAYLIST"')
    qtd_playlists = cursor_postgres.fetchone()[0]

    cursor_postgres.execute('SELECT nome_playlist FROM "PLAYLIST"')
    nomes_playlists = {linha[0] for linha in cursor_postgres.fetchall()}

    while qtd_playlists < 30:
        if not usuarios:
            raise Exception("Faltam utilizadores para criar playlists.")

        nome_playlist = fake.word().capitalize() + " Mix"
        while nome_playlist in nomes_playlists:
            nome_playlist = fake.word().capitalize() + " Mix " + str(random.randint(1, 999999))

        id_usuario = random.choice(usuarios)

        try:
            cursor_postgres.execute("""
                INSERT INTO "PLAYLIST" (nome_playlist, id_usuario)
                VALUES (%s, %s)
            """, (nome_playlist, id_usuario))

            nomes_playlists.add(nome_playlist)
            qtd_playlists += 1
        except Exception as e:
            print(f"\n[ERRO DETALHADO NA PLAYLIST]: {repr(e)}")
            raise e

    # -------------------------------------------------------------
    # 7. PLAYLIST_MUSICA
    # -------------------------------------------------------------
    cursor_postgres.execute('SELECT id_musica FROM "MUSICA"')
    ids_musicas = [linha[0] for linha in cursor_postgres.fetchall()]

    cursor_postgres.execute('SELECT id_playlist FROM "PLAYLIST"')
    ids_playlists = [linha[0] for linha in cursor_postgres.fetchall()]

    cursor_postgres.execute('SELECT id_playlist, id_musica FROM "PLAYLIST_MUSICA"')
    relacoes = set(cursor_postgres.fetchall())

    while len(relacoes) < 50:
        if not ids_playlists or not ids_musicas:
            raise Exception("Faltam playlists ou músicas para criar relações.")

        relacao = (
            random.choice(ids_playlists),
            random.choice(ids_musicas)
        )
        if relacao not in relacoes:
            try:
                cursor_postgres.execute("""
                    INSERT INTO "PLAYLIST_MUSICA" (id_playlist, id_musica)
                    VALUES (%s, %s)
                """, relacao)
                relacoes.add(relacao)
            except Exception as e:
                print(f"\n[ERRO DETALHADO EM PLAYLIST_MUSICA]: {repr(e)}")
                raise e

    # Confirma todas as alterações no banco de dados
    conexao_postgres.commit()

    print("\n[SUCESSO] Todas as tabelas foram preenchidas e sincronizadas a partir do 1!")
    print("-----------------------------------------")
    print("Músicos/Artistas criados:", len(artistas))
    print("Utilizadores:", len(usuarios))
    print("Géneros:", len(generos))
    print("Álbuns:", len(albuns))
    print("Músicas:", qtd_musicas)
    print("Playlists:", qtd_playlists)

except Exception as erro:
    conexao_postgres.rollback()
    print("\n[ERRO GERAL] A transação foi revertida (rollback).")
    print("Detalhe técnico do erro:", str(erro))

finally:
    cursor_postgres.close()
    conexao_postgres.close()