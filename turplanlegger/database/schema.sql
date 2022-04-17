CREATE TABLE IF NOT EXISTS users (
    id int PRIMARY KEY,
    name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL
);

CREATE TABLE IF NOT EXISTS routes (
    id int PRIMARY KEY,
    route text ARRAY
);

CREATE TABLE IF NOT EXISTS trips (
    id int PRIMARY KEY,
    name text NOT NULL,
    date_start timestamp without time zone NOT NULL,
    date_end timestamp without time zone NOT NULL,
    route int REFERENCES routes (id),
    owner int REFERENCES users (id)
);
