REVOKE ALL ON SCHEMA public FROM PUBLIC;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'movies_owner') THEN
        CREATE ROLE movies_owner LOGIN PASSWORD 'owner_change_me';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'movies_reader') THEN
        CREATE ROLE movies_reader LOGIN PASSWORD 'reader_change_me';
    END IF;
END $$;

GRANT CONNECT ON DATABASE movies_i_own TO movies_owner, movies_reader;
GRANT USAGE ON SCHEMA movies_app TO movies_owner, movies_reader;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA movies_app
TO movies_owner;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA movies_app
TO movies_owner;

GRANT SELECT
ON ALL TABLES IN SCHEMA movies_app
TO movies_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA movies_app
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO movies_owner;

ALTER DEFAULT PRIVILEGES IN SCHEMA movies_app
GRANT SELECT ON TABLES TO movies_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA movies_app
GRANT USAGE, SELECT ON SEQUENCES TO movies_owner;
