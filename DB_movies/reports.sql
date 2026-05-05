SET search_path TO movies_app, public;

SELECT
    g.genre_name,
    COUNT(*) AS movie_count
FROM movies AS m
JOIN genres AS g ON g.genre_id = m.genre_id
GROUP BY g.genre_name
ORDER BY movie_count DESC, g.genre_name;

SELECT
    f.format_name,
    SUM(oc.quantity) AS total_copies
FROM owned_copies AS oc
JOIN formats AS f ON f.format_id = oc.format_id
GROUP BY f.format_name
ORDER BY total_copies DESC, f.format_name;

SELECT
    m.title,
    m.release_year,
    oc.shelf_location,
    oc.item_condition
FROM movies AS m
JOIN owned_copies AS oc ON oc.movie_id = m.movie_id
WHERE oc.is_lent_out = TRUE
ORDER BY m.title;

SELECT
    ROUND(COALESCE(SUM(oc.purchase_price * oc.quantity), 0), 2) AS estimated_collection_value
FROM owned_copies AS oc;
