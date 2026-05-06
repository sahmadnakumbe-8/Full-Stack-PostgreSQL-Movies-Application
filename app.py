"""Command line interface for the Movies I Own database application."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from movies import DatabaseDriverError, DatabaseOperationError, MovieCollectionDB


BASE_DIR = Path(__file__).resolve().parent


VALID_CONDITIONS = {
    "new": "New",
    "good": "Good",
    "fair": "Fair",
    "collector": "Collector",
}

VALID_RATINGS = {"G", "PG", "PG-13", "R", "NR"}


def parse_int_in_range(value_text: str, field_name: str, minimum: int, maximum: int) -> int:
    """Parse an integer and validate that it falls within the accepted range."""

    cleaned = value_text.strip()
    if not cleaned.isdigit():
        raise ValueError(f"{field_name} must be a whole number.")

    value = int(cleaned)
    if not minimum <= value <= maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}.")

    return value


def normalize_rating(rating_text: str) -> str:
    """Normalize the MPAA rating to one of the allowed database values."""

    cleaned = rating_text.strip().upper()
    if cleaned in VALID_RATINGS:
        return cleaned

    raise ValueError("MPAA rating must be one of: G, PG, PG-13, R, or NR.")


def normalize_condition(condition_text: str) -> str:
    """Normalize copy condition input to the allowed database values."""

    cleaned = condition_text.strip().lower()
    if cleaned in VALID_CONDITIONS:
        return VALID_CONDITIONS[cleaned]

    raise ValueError(
        "Condition must be one of: New, Good, Fair, or Collector."
    )


def normalize_purchase_date(date_text: str) -> str | None:
    """Accept YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY and normalize to YYYY-MM-DD."""

    cleaned = date_text.strip()
    if not cleaned:
        return None


    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d/%m/%y", "%m/%d/%y"):
        try:
            return datetime.strptime(cleaned, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(
        "Purchase date must use YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY, for example 2026-05-05, 05/05/2026, or 07/13/2026."
    )


def normalize_yes_no(value_text: str, field_name: str) -> bool:
    """Accept yes/no or y/n input and return a boolean value."""

    cleaned = value_text.strip().lower()
    if cleaned in {"y", "yes"}:
        return True
    if cleaned in {"n", "no"}:
        return False

    raise ValueError(f"{field_name} must be yes or no.")


def format_lent_status(value: bool | None) -> str:
    """Render lent-out status as a user-friendly label."""

    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "N/A"


def print_heading(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_menu() -> None:
    print_heading("Movies I Own - PostgreSQL Database Application")
    print("1. Test database connection")
    print("2. Initialize database schema")
    print("3. Load sample seed data")
    print("4. Add a movie")
    print("5. Add an owned copy")
    print("6. View collection")
    print("7. Search movies by title")
    print("8. Run built-in reports")
    print("0. Exit")


def prompt_for_movie(db: MovieCollectionDB) -> None:
    title = input("Title: ").strip()
    release_year = parse_int_in_range(
        input("Release year (1888-2100): "), "Release year", 1888, 2100
    )
    runtime_minutes = parse_int_in_range(
        input("Runtime in minutes (1-500): "), "Runtime in minutes", 1, 500
    )
    mpaa_rating = normalize_rating(input("MPAA rating (G, PG, PG-13, R, NR): "))
    genre_name = input("Genre: ").strip()
    studio_name = input("Studio: ").strip()
    directors = [
        part.strip()
        for part in input("Directors (comma separated): ").split(",")
        if part.strip()
    ]
    imdb_input = input("IMDb score (optional): ").strip()
    note_input = input("Notes (optional): ").strip()

    movie_id = db.add_movie(
        title=title,
        release_year=release_year,
        runtime_minutes=runtime_minutes,
        mpaa_rating=mpaa_rating,
        genre_name=genre_name,
        studio_name=studio_name,
        directors=directors,
        imdb_score=float(imdb_input) if imdb_input else None,
        notes=note_input or None,
    )
    print(f"Movie saved with movie_id={movie_id}")


def prompt_for_copy(db: MovieCollectionDB) -> None:
    rows = db.fetch_collection()
    if not rows:
        raise ValueError("No movies are available yet. Add a movie first or load sample seed data.")

    valid_movie_ids = {row["movie_id"] for row in rows}

    print("Use option 4 first if the movie does not exist yet.")
    print("Available movies:")
    for row in rows:
        print(f"  {row['movie_id']}: {row['title']} ({row['release_year']})")

    movie_id_text = input("Movie ID number from the list above: ").strip()
    if not movie_id_text.isdigit():
        raise ValueError(
            "Movie ID must be a number like 1 or 2. Enter the date later at the purchase date prompt."
        )

    movie_id = int(movie_id_text)
    if movie_id not in valid_movie_ids:
        valid_id_list = ", ".join(str(movie_id) for movie_id in sorted(valid_movie_ids))
        raise ValueError(f"Movie ID {movie_id} is not in the list above. Choose one of: {valid_id_list}.")

    format_name = input("Format (DVD, Blu-ray, Digital, VHS, 4K): ").strip()
    shelf_location = input("Shelf location: ").strip()
    condition = input("Condition (New, Good, Fair, Collector): ").strip()
    price = input("Purchase price (optional): ").strip()
    purchase_date = input(
        "Purchase date YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY (optional, example 05/05/2026 or 07/13/2026): "
    ).strip()
    quantity_text = input("Quantity: ").strip()
    lent_out = normalize_yes_no(
        input("Is this movie currently lent out? (yes/no): "),
        "Lent out status",
    )

    copy_id = db.add_owned_copy(
        movie_id=movie_id,
        format_name=format_name,
        shelf_location=shelf_location,
        condition=normalize_condition(condition),
        purchase_price=float(price) if price else None,
        purchase_date=normalize_purchase_date(purchase_date),
        quantity=int(quantity_text) if quantity_text else 1,
        is_lent_out=lent_out,
    )
    print(f"Owned copy saved with copy_id={copy_id}")


def show_collection(db: MovieCollectionDB) -> None:
    rows = db.fetch_collection()
    if not rows:
        print("No movies found.")
        return

    print_heading("Current Collection")
    sorted_rows = sorted(rows, key=lambda row: (row["title"].lower(), row["release_year"]))
    for index, row in enumerate(sorted_rows, start=1):
        print(
            f"{index}. {row['title']} ({row['release_year']}) | "
            f"{row['genre_name'] or 'N/A'} | {row['studio_name'] or 'N/A'} | "
            f"Director(s): {row['directors'] or 'N/A'} | "
            f"Format: {row['format_name'] or 'N/A'} | "
            f"Qty: {row['quantity'] or 0} | Shelf: {row['shelf_location'] or 'N/A'} | "
            f"Condition: {row['item_condition'] or 'N/A'} | Lent: {format_lent_status(row['is_lent_out'])}"
        )


def show_search_results(db: MovieCollectionDB) -> None:
    keyword = input("Search title keyword: ").strip()
    rows = db.search_movies(keyword)
    if not rows:
        print("No matching titles found.")
        return

    print_heading(f"Search Results for '{keyword}'")
    for row in rows:
        print(
            f"[{row['movie_id']}] {row['title']} ({row['release_year']}) | "
            f"Runtime: {row['runtime_minutes']} min | Rating: {row['mpaa_rating']} | "
            f"IMDb: {row['imdb_score']}"
        )


def show_reports(db: MovieCollectionDB) -> None:
    reports = db.fetch_reports()

    print_heading("Report: Copies by Format")
    for row in reports["copies_by_format"]:
        print(f"{row['format_name']}: {row['total_items']}")

    print_heading("Report: Movies Lent Out")
    if reports["movies_lent_out"]:
        for row in reports["movies_lent_out"]:
            print(f"{row['title']} | {row['format_name']} | Shelf: {row['shelf_location']}")
    else:
        print("No titles are currently lent out.")

    print_heading("Report: Collection Value")
    total_value = reports["collection_value"][0]["total_value"]
    print(f"Estimated purchase value: ${total_value}")


def main() -> None:
    try:
        db = MovieCollectionDB(BASE_DIR / "settings.json")
    except FileNotFoundError:
        print("settings.json was not found. Create it before running the application.")
        return
    except Exception as exc:
        print(f"Unable to start application: {exc}")
        return

    actions = {
        "1": lambda: print(db.test_connection()),
        "2": lambda: (db.initialize_schema(), print("Schema initialized successfully.")),
        "3": lambda: (db.seed_sample_data(), print("Sample data loaded successfully.")),
        "4": lambda: prompt_for_movie(db),
        "5": lambda: prompt_for_copy(db),
        "6": lambda: show_collection(db),
        "7": lambda: show_search_results(db),
        "8": lambda: show_reports(db),
    }

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please select a valid menu option.")
            continue

        try:
            action()
        except (DatabaseDriverError, DatabaseOperationError, ValueError) as exc:
            print(f"Operation failed: {exc}")


if __name__ == "__main__":
    main()
