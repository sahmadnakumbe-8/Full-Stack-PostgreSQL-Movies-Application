"""Command line interface for the Movies I Own database application."""

from __future__ import annotations

from pathlib import Path

from movies import DatabaseDriverError, DatabaseOperationError, MovieCollectionDB


BASE_DIR = Path(__file__).resolve().parent


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
    release_year = int(input("Release year: ").strip())
    runtime_minutes = int(input("Runtime in minutes: ").strip())
    mpaa_rating = input("MPAA rating (G, PG, PG-13, R, NR): ").strip().upper()
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
    movie_id = int(input("Movie ID: ").strip())
    format_name = input("Format (DVD, Blu-ray, Digital, VHS, 4K): ").strip()
    shelf_location = input("Shelf location: ").strip()
    condition = input("Condition (New, Good, Fair, Collector): ").strip()
    price = input("Purchase price (optional): ").strip()
    purchase_date = input("Purchase date YYYY-MM-DD (optional): ").strip()
    quantity_text = input("Quantity: ").strip()
    lent_out = input("Is lent out? (y/n): ").strip().lower() == "y"

    copy_id = db.add_owned_copy(
        movie_id=movie_id,
        format_name=format_name,
        shelf_location=shelf_location,
        condition=condition,
        purchase_price=float(price) if price else None,
        purchase_date=purchase_date or None,
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
    for row in rows:
        print(
            f"[{row['movie_id']}] {row['title']} ({row['release_year']}) | "
            f"{row['genre_name']} | {row['studio_name']} | "
            f"Director(s): {row['directors'] or 'N/A'} | "
            f"Format: {row['format_name'] or 'N/A'} | "
            f"Qty: {row['quantity'] or 0} | Shelf: {row['shelf_location'] or 'N/A'} | "
            f"Condition: {row['item_condition'] or 'N/A'} | Lent: {row['is_lent_out']}"
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
