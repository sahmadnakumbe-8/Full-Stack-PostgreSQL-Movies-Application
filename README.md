# Movies I Own - PostgreSQL Project

This project demonstrates relational database design, SQL development, normalization, indexing, documentation, and application security for a movie collection system.

## Project Files

- `app.py`: command line application for working with the database
- `movies.py`: database access layer with exception handling
- `security.sql`: database role and privilege script
- `settings.json`: connection settings used by the Python app
- `DB_movies/schema.sql`: normalized schema, constraints, indexes, and view
- `DB_movies/seed.sql`: sample data
- `DB_movies/reports.sql`: reporting queries
- `docs/data_dictionary.md`: data dictionary
- `docs/erd.md`: ERD and relationship notes

## What "data" means in a relational database

In a relational design, data is organized into related tables. Each table stores one type of entity, each row stores one instance of that entity, and each column stores one attribute. Relationships are enforced with foreign keys so the database can maintain accurate, high-quality information.

## Design Summary

- `movies` stores one row per film title
- `genres`, `studios`, `formats`, and `people` store reusable descriptive data
- `movie_directors` resolves the many-to-many relationship between movies and directors
- `owned_copies` stores ownership details such as format, shelf location, condition, and lending status

## Normalization Notes

- First Normal Form: repeating groups were removed by storing directors and owned copies in separate tables
- Second Normal Form: non-key columns depend on their full primary key
- Third Normal Form: lookup values such as genre, studio, and format are stored separately to reduce duplication

## How to Run

1. Create a PostgreSQL database named `movies_i_own`.
2. Update `settings.json` with your local username and password.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. Use menu option `2` to initialize the schema, then option `3` to load sample data.

## Query Optimization

Indexes were added on:

- movie titles
- release year
- foreign keys used in joins
- owned copy lending status

These indexes improve reporting and search performance.
