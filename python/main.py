import sqlite3

from dados import musicas
from funcoes import mostrar_musicas, menu, cadastrar_musica, buscar_musica, editar_musica, excluir_musica, criar_playlist, listar_playlists, adicionar_musica_playlist, listar_musicas

conexao = sqlite3.connect("banco.db")

cursor = conexao.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS musicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    artista TEXT NOT NULL,
    album TEXT NOT NULL,
    genero TEXT NOT NULL
)
""")

conexao.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
""")

conexao.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS playlist_musicas (
    id_playlist INTEGER,
    id_musica INTEGER,
    PRIMARY KEY (id_playlist, id_musica)
)
""")

conexao.commit()


cursor.execute("SELECT COUNT(*) FROM musicas")
quantidade = cursor.fetchone()[0]


if quantidade == 0:
    for musica in musicas:
        cursor.execute("""
        INSERT INTO musicas (titulo, artista, album, genero)
        VALUES (?, ?, ?, ?)
        """, (
            musica["titulo"],
            musica["artista"],
            musica["album"],
            musica["genero"]
        ))

    conexao.commit()


def main():
    while True:
        menu()
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            cadastrar_musica(cursor, conexao)

        elif opcao == "2":
            listar_musicas(cursor)

        elif opcao == "3":
            buscar_musica(cursor)

        elif opcao == "4":
            editar_musica(cursor, conexao)

        elif opcao == "5":
            excluir_musica(cursor, conexao)

        elif opcao == "6":
            criar_playlist(cursor, conexao)

        elif opcao == "7":
            listar_playlists(cursor)

        elif opcao == "8":
            adicionar_musica_playlist(cursor, conexao)

        elif opcao == "0":
            print("Programa encerrado")
            break

        else:
            print("Opção inválida.")

main()

conexao.close()