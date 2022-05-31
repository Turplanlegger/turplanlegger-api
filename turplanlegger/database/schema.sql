CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY,
    name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL,
    auth_method text NOT NULL,
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS routes (
    id serial PRIMARY KEY,
    route jsonb,
    route_history jsonb ARRAY,
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS item_lists (
    id serial PRIMARY KEY,
    name text,
    type text,
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS lists_items (
    id serial PRIMARY KEY,
    content text,
    checked boolean DEFAULT FALSE,
    item_list int REFERENCES item_lists (id),
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS trips (
    id serial PRIMARY KEY,
    name text NOT NULL,
    date_start timestamp without time zone CHECK (date_start < date_end),
    date_end timestamp without time zone CHECK (date_start < date_end),
    route int REFERENCES routes (id),
    owner int REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);
