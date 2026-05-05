CREATE SCHEMA IF NOT EXISTS movies_app;
SET search_path TO movies_app, public;

CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    genre_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS studios (
    studio_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    studio_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS formats (
    format_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    format_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS people (
    person_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movies (
    movie_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    release_year INTEGER NOT NULL CHECK (release_year BETWEEN 1888 AND 2100),
    runtime_minutes INTEGER NOT NULL CHECK (runtime_minutes > 0),
    mpaa_rating VARCHAR(10) NOT NULL CHECK (mpaa_rating IN ('G', 'PG', 'PG-13', 'R', 'NR')),
    genre_id INTEGER NOT NULL REFERENCES genres(genre_id),
    studio_id INTEGER NOT NULL REFERENCES studios(studio_id),
    imdb_score NUMERIC(3,1),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_movie_title_year UNIQUE (title, release_year)
);

CREATE TABLE IF NOT EXISTS movie_directors (
    movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES people(person_id) ON DELETE RESTRICT,
    PRIMARY KEY (movie_id, person_id)
);

CREATE TABLE IF NOT EXISTS owned_copies (
    copy_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    format_id INTEGER NOT NULL REFERENCES formats(format_id),
    shelf_location VARCHAR(50) NOT NULL,
    item_condition VARCHAR(20) NOT NULL CHECK (item_condition IN ('New', 'Good', 'Fair', 'Collector')),
    purchase_price NUMERIC(10,2),
    purchase_date DATE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    is_lent_out BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_movie_copy UNIQUE (movie_id, format_id, shelf_location)
);

CREATE INDEX IF NOT EXISTS idx_movies_title ON movies (title);
CREATE INDEX IF NOT EXISTS idx_movies_release_year ON movies (release_year);
CREATE INDEX IF NOT EXISTS idx_movies_genre_id ON movies (genre_id);
CREATE INDEX IF NOT EXISTS idx_movies_studio_id ON movies (studio_id);
CREATE INDEX IF NOT EXISTS idx_owned_copies_movie_id ON owned_copies (movie_id);
CREATE INDEX IF NOT EXISTS idx_owned_copies_format_id ON owned_copies (format_id);
CREATE INDEX IF NOT EXISTS idx_owned_copies_lent_out ON owned_copies (is_lent_out);

CREATE OR REPLACE VIEW vw_collection_summary AS
SELECT
    m.movie_id,
    m.title,
    m.release_year,
    g.genre_name,
    s.studio_name,
    STRING_AGG(DISTINCT p.full_name, ', ' ORDER BY p.full_name) AS directors,
    SUM(COALESCE(oc.quantity, 0)) AS total_copies
FROM movies AS m
JOIN genres AS g ON g.genre_id = m.genre_id
JOIN studios AS s ON s.studio_id = m.studio_id
LEFT JOIN movie_directors AS md ON md.movie_id = m.movie_id
LEFT JOIN people AS p ON p.person_id = md.person_id
LEFT JOIN owned_copies AS oc ON oc.movie_id = m.movie_id
GROUP BY m.movie_id, m.title, m.release_year, g.genre_name, s.studio_name;
