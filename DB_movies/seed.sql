SET search_path TO movies_app, public;

INSERT INTO genres (genre_name) VALUES
    ('Action'),
    ('Adventure'),
    ('Drama'),
    ('Science Fiction'),
    ('Comedy')
ON CONFLICT (genre_name) DO NOTHING;

INSERT INTO studios (studio_name) VALUES
    ('Warner Bros'),
    ('Universal Pictures'),
    ('Paramount Pictures'),
    ('Disney')
ON CONFLICT (studio_name) DO NOTHING;

INSERT INTO formats (format_name) VALUES
    ('DVD'),
    ('Blu-ray'),
    ('4K'),
    ('Digital')
ON CONFLICT (format_name) DO NOTHING;

INSERT INTO people (full_name) VALUES
    ('Christopher Nolan'),
    ('Steven Spielberg'),
    ('Patty Jenkins')
ON CONFLICT (full_name) DO NOTHING;

INSERT INTO movies (
    title,
    release_year,
    runtime_minutes,
    mpaa_rating,
    genre_id,
    studio_id,
    imdb_score,
    notes
)
SELECT 'Inception', 2010, 148, 'PG-13', g.genre_id, s.studio_id, 8.8, 'Mind-bending heist film'
FROM genres AS g, studios AS s
WHERE g.genre_name = 'Science Fiction' AND s.studio_name = 'Warner Bros'
ON CONFLICT (title, release_year) DO NOTHING;

INSERT INTO movies (
    title,
    release_year,
    runtime_minutes,
    mpaa_rating,
    genre_id,
    studio_id,
    imdb_score,
    notes
)
SELECT 'Wonder Woman', 2017, 141, 'PG-13', g.genre_id, s.studio_id, 7.4, 'Superhero origin story'
FROM genres AS g, studios AS s
WHERE g.genre_name = 'Action' AND s.studio_name = 'Warner Bros'
ON CONFLICT (title, release_year) DO NOTHING;

INSERT INTO movie_directors (movie_id, person_id)
SELECT m.movie_id, p.person_id
FROM movies AS m
JOIN people AS p ON p.full_name = 'Christopher Nolan'
WHERE m.title = 'Inception'
ON CONFLICT DO NOTHING;

INSERT INTO movie_directors (movie_id, person_id)
SELECT m.movie_id, p.person_id
FROM movies AS m
JOIN people AS p ON p.full_name = 'Patty Jenkins'
WHERE m.title = 'Wonder Woman'
ON CONFLICT DO NOTHING;

INSERT INTO owned_copies (
    movie_id,
    format_id,
    shelf_location,
    item_condition,
    purchase_price,
    purchase_date,
    quantity,
    is_lent_out
)
SELECT m.movie_id, f.format_id, 'Shelf A1', 'Good', 19.99, DATE '2024-06-14', 1, FALSE
FROM movies AS m
JOIN formats AS f ON f.format_name = 'Blu-ray'
WHERE m.title = 'Inception'
ON CONFLICT (movie_id, format_id, shelf_location) DO NOTHING;

INSERT INTO owned_copies (
    movie_id,
    format_id,
    shelf_location,
    item_condition,
    purchase_price,
    purchase_date,
    quantity,
    is_lent_out
)
SELECT m.movie_id, f.format_id, 'Shelf B2', 'Collector', 24.99, DATE '2024-07-20', 1, TRUE
FROM movies AS m
JOIN formats AS f ON f.format_name = '4K'
WHERE m.title = 'Wonder Woman'
ON CONFLICT (movie_id, format_id, shelf_location) DO NOTHING;
