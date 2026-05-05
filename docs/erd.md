# Entity Relationship Diagram

```mermaid
erDiagram
    GENRES ||--o{ MOVIES : classifies
    STUDIOS ||--o{ MOVIES : produces
    MOVIES ||--o{ OWNED_COPIES : has
    FORMATS ||--o{ OWNED_COPIES : stores_as
    MOVIES ||--o{ MOVIE_DIRECTORS : links
    PEOPLE ||--o{ MOVIE_DIRECTORS : directs

    GENRES {
        int genre_id PK
        string genre_name
    }

    STUDIOS {
        int studio_id PK
        string studio_name
    }

    FORMATS {
        int format_id PK
        string format_name
    }

    PEOPLE {
        int person_id PK
        string full_name
    }

    MOVIES {
        int movie_id PK
        string title
        int release_year
        int runtime_minutes
        string mpaa_rating
        int genre_id FK
        int studio_id FK
    }

    MOVIE_DIRECTORS {
        int movie_id FK
        int person_id FK
    }

    OWNED_COPIES {
        int copy_id PK
        int movie_id FK
        int format_id FK
        string shelf_location
        string item_condition
        decimal purchase_price
        bool is_lent_out
    }
```

## Integrity Rules

- Primary keys uniquely identify each row.
- Foreign keys enforce valid relationships between tables.
- Check constraints restrict invalid values such as impossible release years or unsupported ratings.
- Unique constraints reduce duplicate movie and copy records.
