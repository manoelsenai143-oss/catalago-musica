SELECT *
FROM "USUARIO";

SELECT *
FROM "ARTISTA";

SELECT titulo, "duração"
FROM "MUSICA"
WHERE id_genero = 1;

SELECT nome_album, ano_album
FROM "ALBUM"
WHERE ano_album >= 2015;

SELECT 
    "MUSICA".titulo,
    "ALBUM".nome_album
FROM "MUSICA"
JOIN "ALBUM"
    ON "MUSICA".id_album = "ALBUM".id_album;

SELECT 
    "MUSICA".titulo,
    "ARTISTA".nome_artista
FROM "MUSICA"
JOIN "ALBUM"
    ON "MUSICA".id_album = "ALBUM".id_album
JOIN "ARTISTA"
    ON "ALBUM".id_artista = "ARTISTA".id_artista;

SELECT 
    "MUSICA".titulo,
    "ARTISTA".nome_artista,
    "GENERO".nome_genero
FROM "MUSICA"
JOIN "ALBUM"
    ON "MUSICA".id_album = "ALBUM".id_album
JOIN "ARTISTA"
    ON "ALBUM".id_artista = "ARTISTA".id_artista
JOIN "GENERO"
    ON "MUSICA".id_genero = "GENERO".id_genero;


UPDATE "ARTISTA"
SET nome_artista = 'Kanye West'
WHERE id_artista = 9;

UPDATE "PLAYLIST"
SET nome_playlist = 'Minhas músicas favoritas'
WHERE id_playlist = 1;


DELETE FROM "PLAYLIST_MUSICA"
WHERE id_playlist = 10
AND id_musica = 10;