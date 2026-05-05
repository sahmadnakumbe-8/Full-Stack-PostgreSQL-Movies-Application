# Data Dictionary

## `genres`

| Column | Type | Description |
| --- | --- | --- |
| `genre_id` | integer | Primary key for each genre |
| `genre_name` | varchar(50) | Unique genre name |

## `studios`

| Column | Type | Description |
| --- | --- | --- |
| `studio_id` | integer | Primary key for each studio |
| `studio_name` | varchar(100) | Unique studio name |

## `formats`

| Column | Type | Description |
| --- | --- | --- |
| `format_id` | integer | Primary key for each format |
| `format_name` | varchar(30) | Unique format name |

## `people`

| Column | Type | Description |
| --- | --- | --- |
| `person_id` | integer | Primary key for a person |
| `full_name` | varchar(100) | Director or other credited person |

## `movies`

| Column | Type | Description |
| --- | --- | --- |
| `movie_id` | integer | Primary key for each movie |
| `title` | varchar(150) | Movie title |
| `release_year` | integer | Year released |
| `runtime_minutes` | integer | Runtime in minutes |
| `mpaa_rating` | varchar(10) | Content rating |
| `genre_id` | integer | Foreign key to `genres` |
| `studio_id` | integer | Foreign key to `studios` |
| `imdb_score` | numeric(3,1) | Optional IMDb score |
| `notes` | text | Optional descriptive notes |
| `created_at` | timestamp | Date the record was created |

## `movie_directors`

| Column | Type | Description |
| --- | --- | --- |
| `movie_id` | integer | Foreign key to `movies` |
| `person_id` | integer | Foreign key to `people` |

## `owned_copies`

| Column | Type | Description |
| --- | --- | --- |
| `copy_id` | integer | Primary key for each physical or digital owned copy |
| `movie_id` | integer | Foreign key to `movies` |
| `format_id` | integer | Foreign key to `formats` |
| `shelf_location` | varchar(50) | Where the copy is stored |
| `item_condition` | varchar(20) | Condition of the item |
| `purchase_price` | numeric(10,2) | Purchase price |
| `purchase_date` | date | Date purchased |
| `quantity` | integer | Number of copies owned |
| `is_lent_out` | boolean | Whether the copy is currently lent out |
