INSERT INTO "USUARIO" (nome_usuario, email, senha)
VALUES
('Manoel', 'manoel@email.com', '1234'),
('Eduardo', 'eduardo@email.com', '1234'),
('Felipe', 'felipe@email.com', '1234'),
('Murilo', 'murilo@email.com', '1234'),
('Kael', 'kael@email.com', '1234'),
('Guilherme', 'guilherme@email.com', '1234'),
('Nicolas', 'nicolas@email.com', '1234'),
('Fernando', 'fernando@email.com', '1234'),
('Jaison', 'jaison@email.com', '1234'),
('Rosolem', 'rosolem@email.com', '1234');

INSERT INTO "ARTISTA" (nome_artista)
VALUES
('Bruno Mars'),
('The Weeknd'),
('Imagine Dragons'),
('Linkin Park'),
('Coldplay'),
('Ed Sheeran'),
('Adele'),
('Dua Lipa'),
('Kanye West'),
('Post Malone');

INSERT INTO "GENERO" (nome_genero)
VALUES
('Pop'),
('Rock'),
('Rap'),
('Hip Hop'),
('Eletronica'),
('Jazz'),
('Funk'),
('R&B'),
('Indie'),
('MPB');

INSERT INTO "ALBUM" (nome_album, ano_album, id_artista)
VALUES
('Doo-Wops & Hooligans', 2010, 1),
('After Hours', 2020, 2),
('Evolve', 2017, 3),
('Hybrid Theory', 2000, 4),
('Parachutes', 2000, 5),
('+', 2011, 6),
('25', 2015, 7),
('Future Nostalgia', 2020, 8),
('My Beautiful Dark Twisted Fantasy', 2010, 9),
('Hollywood''s Bleeding', 2019, 10);

INSERT INTO "MUSICA" (titulo, "duração", id_album, id_genero)
VALUES
('Just the Way You Are', 220, 1, 1),
('Blinding Lights', 200, 2, 8),
('Believer', 204, 3, 2),
('In the End', 216, 4, 2),
('Yellow', 266, 5, 9),
('Perfect', 263, 6, 1),
('Hello', 295, 7, 8),
('Levitating', 203, 8, 5),
('power', 231, 9, 1),
('Circles', 215, 10, 3);

INSERT INTO "PLAYLIST" (nome_playlist, id_usuario)
VALUES                                                            
('Minhas favoritas', 1),
('Para estudar', 2),
('Rock', 3),
('Pop', 4),
('Musicas para viajar', 5),
('Treino', 6),
('Relaxar', 7),
('Melhores do ano', 8),
('Playlist do fim de semana', 9),
('Favoritas', 10);

INSERT INTO "PLAYLIST_MUSICA" (id_playlist, id_musica)
VALUES
(1, 1),
(2, 2),
(3, 4),
(4, 3),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10);
