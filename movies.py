"""Database access layer for the Movies I Own PostgreSQL project."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SETTINGS = BASE_DIR / "settings.json"


class DatabaseDriverError(RuntimeError):
    """Raised when the PostgreSQL driver is unavailable."""


class DatabaseOperationError(RuntimeError):
    """Raised for recoverable database operation failures."""


@dataclass(slots=True)
class DatabaseConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    schema: str = "movies_app"

    @property
    def dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.dbname} "
            f"user={self.user} password={self.password}"
        )


class MovieCollectionDB:
    """Encapsulates PostgreSQL operations for the movie collection."""

    def __init__(self, settings_path: str | Path = DEFAULT_SETTINGS) -> None:
        self.settings_path = Path(settings_path)
        self.config = self._load_config()

    def _load_config(self) -> DatabaseConfig:
        with self.settings_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        database = raw["database"]
        return DatabaseConfig(
            host=database["host"],
            port=int(database["port"]),
            dbname=database["dbname"],
            user=database["user"],
            password=database["password"],
            schema=database.get("schema", "movies_app"),
        )

    def _connect(self):
        if psycopg is None:
            raise DatabaseDriverError(
                "psycopg is not installed. Install dependencies before running the app."
            )

        return psycopg.connect(
            self.config.dsn,
            autocommit=False,
            row_factory=psycopg.rows.dict_row,
        )

    def _set_search_path(self, cur) -> None:
        cur.execute(f"SET search_path TO {self.config.schema}, public;")

    def test_connection(self) -> str:
        try:
            with self._connect() as conn, conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user, version();")
                row = cur.fetchone()
                return (
                    f"Connected to database '{row['current_database']}' as "
                    f"'{row['current_user']}'."
                )
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(f"Connection test failed: {exc}") from exc

    def execute_sql_file(self, sql_path: str | Path) -> None:
        script_path = Path(sql_path)
        try:
            with script_path.open("r", encoding="utf-8") as handle:
                sql = handle.read()
            with self._connect() as conn, conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(
                f"Failed to execute SQL file '{script_path.name}': {exc}"
            ) from exc

    def initialize_schema(self) -> None:
        self.execute_sql_file(BASE_DIR / "DB_movies" / "schema.sql")

    def seed_sample_data(self) -> None:
        self.execute_sql_file(BASE_DIR / "DB_movies" / "seed.sql")

    def add_movie(
        self,
        title: str,
        release_year: int,
        runtime_minutes: int,
        mpaa_rating: str,
        genre_name: str,
        studio_name: str,
        directors: list[str],
        imdb_score: float | None = None,
        notes: str | None = None,
    ) -> int:
        insert_sql = """
        WITH genre_row AS (
            INSERT INTO genres (genre_name)
            VALUES (%s)
            ON CONFLICT (genre_name) DO UPDATE
            SET genre_name = EXCLUDED.genre_name
            RETURNING genre_id
        ),
        studio_row AS (
            INSERT INTO studios (studio_name)
            VALUES (%s)
            ON CONFLICT (studio_name) DO UPDATE
            SET studio_name = EXCLUDED.studio_name
            RETURNING studio_id
        )
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
        SELECT
            %s,
            %s,
            %s,
            %s,
            genre_row.genre_id,
            studio_row.studio_id,
            %s,
            %s
        FROM genre_row, studio_row
        RETURNING movie_id;
        """
        try:
            with self._connect() as conn, conn.cursor() as cur:
                self._set_search_path(cur)
                cur.execute(
                    insert_sql,
                    (
                        genre_name,
                        studio_name,
                        title,
                        release_year,
                        runtime_minutes,
                        mpaa_rating,
                        imdb_score,
                        notes,
                    ),
                )
                movie_id = cur.fetchone()["movie_id"]

                for director in directors:
                    self._set_search_path(cur)
                    cur.execute(
                        """
                        INSERT INTO people (full_name)
                        VALUES (%s)
                        ON CONFLICT (full_name) DO NOTHING;
                        """,
                        (director.strip(),),
                    )
                    self._set_search_path(cur)
                    cur.execute(
                        """
                        INSERT INTO movie_directors (movie_id, person_id)
                        SELECT %s, person_id
                        FROM people
                        WHERE full_name = %s
                        ON CONFLICT DO NOTHING;
                        """,
                        (movie_id, director.strip()),
                    )

                conn.commit()
                return movie_id
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(f"Unable to add movie '{title}': {exc}") from exc

    def add_owned_copy(
        self,
        movie_id: int,
        format_name: str,
        shelf_location: str,
        condition: str,
        purchase_price: float | None = None,
        purchase_date: str | None = None,
        quantity: int = 1,
        is_lent_out: bool = False,
    ) -> int:
        sql = """
        WITH format_row AS (
            INSERT INTO formats (format_name)
            VALUES (%s)
            ON CONFLICT (format_name) DO UPDATE
            SET format_name = EXCLUDED.format_name
            RETURNING format_id
        )
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
        SELECT
            %s,
            format_row.format_id,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        FROM format_row
        RETURNING copy_id;
        """
        try:
            with self._connect() as conn, conn.cursor() as cur:
                self._set_search_path(cur)
                cur.execute(
                    sql,
                    (
                        format_name,
                        movie_id,
                        shelf_location,
                        condition,
                        purchase_price,
                        purchase_date,
                        quantity,
                        is_lent_out,
                    ),
                )
                copy_id = cur.fetchone()["copy_id"]
                conn.commit()
                return copy_id
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(
                f"Unable to add owned copy for movie ID {movie_id}: {exc}"
            ) from exc

    def fetch_collection(self) -> list[dict[str, Any]]:
        sql = """
        SELECT
            m.movie_id,
            m.title,
            m.release_year,
            g.genre_name,
            s.studio_name,
            STRING_AGG(DISTINCT p.full_name, ', ' ORDER BY p.full_name) AS directors,
            f.format_name,
            oc.quantity,
            oc.shelf_location,
            oc.item_condition,
            oc.is_lent_out
        FROM movies AS m
        JOIN genres AS g ON g.genre_id = m.genre_id
        JOIN studios AS s ON s.studio_id = m.studio_id
        LEFT JOIN movie_directors AS md ON md.movie_id = m.movie_id
        LEFT JOIN people AS p ON p.person_id = md.person_id
        LEFT JOIN owned_copies AS oc ON oc.movie_id = m.movie_id
        LEFT JOIN formats AS f ON f.format_id = oc.format_id
        GROUP BY
            m.movie_id,
            m.title,
            m.release_year,
            g.genre_name,
            s.studio_name,
            f.format_name,
            oc.quantity,
            oc.shelf_location,
            oc.item_condition,
            oc.is_lent_out
        ORDER BY m.title, m.release_year;
        """
        try:
            with self._connect() as conn, conn.cursor() as cur:
                self._set_search_path(cur)
                cur.execute(sql)
                return list(cur.fetchall())
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(f"Unable to fetch collection: {exc}") from exc

    def search_movies(self, title_keyword: str) -> list[dict[str, Any]]:
        sql = """
        SELECT
            movie_id,
            title,
            release_year,
            runtime_minutes,
            mpaa_rating,
            imdb_score
        FROM movies
        WHERE title ILIKE %s
        ORDER BY title;
        """
        try:
            with self._connect() as conn, conn.cursor() as cur:
                self._set_search_path(cur)
                cur.execute(sql, (f"%{title_keyword}%",))
                return list(cur.fetchall())
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(f"Unable to search for movies: {exc}") from exc

    def fetch_reports(self) -> dict[str, list[dict[str, Any]]]:
        report_queries = {
            "copies_by_format": """
                SELECT format_name, SUM(quantity) AS total_items
                FROM owned_copies AS oc
                JOIN formats AS f ON f.format_id = oc.format_id
                GROUP BY format_name
                ORDER BY total_items DESC, format_name;
            """,
            "movies_lent_out": """
                SELECT m.title, f.format_name, oc.shelf_location
                FROM owned_copies AS oc
                JOIN movies AS m ON m.movie_id = oc.movie_id
                JOIN formats AS f ON f.format_id = oc.format_id
                WHERE oc.is_lent_out = TRUE
                ORDER BY m.title;
            """,
            "collection_value": """
                SELECT COALESCE(SUM(purchase_price * quantity), 0)::numeric(10,2) AS total_value
                FROM owned_copies;
            """,
        }
        output: dict[str, list[dict[str, Any]]] = {}
        try:
            with self._connect() as conn, conn.cursor() as cur:
                for report_name, sql in report_queries.items():
                    self._set_search_path(cur)
                    cur.execute(sql)
                    output[report_name] = list(cur.fetchall())
            return output
        except Exception as exc:  # pragma: no cover
            raise DatabaseOperationError(f"Unable to fetch reports: {exc}") from exc
