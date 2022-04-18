CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY,
    name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL,
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
    id serial PRIMARY KEY,
    route text ARRAY,
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lists (
    id serial PRIMARY KEY,
    name text,
    type text,
    items text ARRAY,
    items_checked text ARRAY,
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trips (
    id serial PRIMARY KEY,
    name text NOT NULL,
    date_start timestamp without time zone CHECK (date_start < date_end),
    date_end timestamp without time zone CHECK (date_start < date_end),
    route int REFERENCES routes (id),
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);
