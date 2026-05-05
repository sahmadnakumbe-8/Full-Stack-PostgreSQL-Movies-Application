# Movies I Own - PostgreSQL Project

This project demonstrates relational database design, normalization, SQL development, reporting, indexing, documentation, and security for a personal movie collection.

## Project Purpose

The database stores information about movies you own, the format of each copy, where each copy is stored, and whether a copy is currently lent out. The system is designed using accepted relational database practices and includes constraints, foreign keys, indexes, reports, and security roles.

## Included Files

- `app.py`: command-line user interface
- `movies.py`: PostgreSQL data access layer
- `security.sql`: database role and privilege script
- `settings.json`: connection settings for the Python app
- `requirements.txt`: Python dependency list
- `DB_movies/schema.sql`: schema, constraints, indexes, and view
- `DB_movies/seed.sql`: sample starter data
- `DB_movies/reports.sql`: example reporting queries
- `docs/data_dictionary.md`: data dictionary
- `docs/erd.md`: entity relationship diagram and integrity rules
- `.devcontainer/`: containerized development environment

## Relational Data Meaning

In a relational system, data is stored in tables made up of rows and columns. Each table represents one entity, each row represents one occurrence of that entity, and each column represents one attribute. Related tables are connected by primary and foreign keys.

## Normalization Summary

- First Normal Form: multi-valued data such as directors and owned copies are stored in separate tables
- Second Normal Form: non-key attributes depend on the whole key
- Third Normal Form: lookup values such as genre, studio, and format are stored in their own tables to reduce duplication

## How to Run

1. Create a PostgreSQL database named `movies_i_own`.
2. Update `settings.json` with your PostgreSQL username and password.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run the program with `python3 app.py`.
5. In the menu, choose `2` to build the schema and `3` to load sample data.

## Performance Notes

Indexes are included on:

- movie title
- release year
- foreign keys used in joins
- lending status

These indexes improve search and reporting speed.
