DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'access_level') THEN
        CREATE TYPE access_level AS ENUM ('READ', 'MODIFY', 'DELETE');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL,
    auth_method text NOT NULL,
    password text,
    private boolean DEFAULT FALSE,
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS routes (
    id serial PRIMARY KEY,
    route jsonb,
    route_history jsonb ARRAY,
    name text,
    comment text,
    owner UUID REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS route_permissions (
    object_id int NOT NULL REFERENCES routes (id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES users (id),
    access_level access_level NOT NULL,
    PRIMARY KEY (object_id, subject_id)
);

CREATE TABLE IF NOT EXISTS item_lists (
    id serial PRIMARY KEY,
    name text,
    private boolean DEFAULT TRUE,
    owner UUID REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS item_list_permissions (
    object_id int NOT NULL REFERENCES item_lists (id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES users (id),
    access_level access_level NOT NULL,
    PRIMARY KEY (object_id, subject_id)
);

CREATE TABLE IF NOT EXISTS lists_items (
    id serial PRIMARY KEY,
    content text,
    checked boolean DEFAULT FALSE,
    item_list int NOT NULL REFERENCES item_lists (id) ON DELETE CASCADE,
    owner UUID NOT NULL REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS notes (
    id serial PRIMARY KEY,
    name text,
    content text NOT NULL,
    owner UUID NOT NULL REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time timestamp without time zone,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS note_permissions (
    object_id int NOT NULL REFERENCES notes (id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES users (id),
    access_level access_level NOT NULL,
    PRIMARY KEY (object_id, subject_id)
);

CREATE TABLE IF NOT EXISTS trips (
    id serial PRIMARY KEY,
    name text NOT NULL,
    private boolean DEFAULT FALSE,
    owner UUID NOT NULL REFERENCES users (id),
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time timestamp without time zone,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS trip_permissions (
    object_id int NOT NULL REFERENCES trips (id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES users (id),
    access_level access_level NOT NULL,
    PRIMARY KEY (object_id, subject_id)
);

CREATE TABLE IF NOT EXISTS trip_dates (
    id serial PRIMARY KEY,
    start_time timestamp without time zone CHECK (start_time < end_time),
    end_time timestamp without time zone CHECK (start_time < end_time),
    owner UUID REFERENCES users (id) NOT NULL,
    trip_id int NOT NULL REFERENCES trips (id) ON DELETE CASCADE,
    selected boolean DEFAULT FALSE,
    create_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted boolean DEFAULT FALSE,
    delete_time timestamp without time zone
);

CREATE TABLE IF NOT EXISTS trips_notes_references (
    trip_id int NOT NULL REFERENCES trips (id) ON DELETE CASCADE,
    note_id int NOT NULL REFERENCES trips (id) ON DELETE CASCADE,
    PRIMARY KEY (trip_id, note_id)
);

CREATE TABLE IF NOT EXISTS trips_routes_references (
    trip_id int NOT NULL REFERENCES trips (id) ON DELETE CASCADE,
    route_id int NOT NULL REFERENCES routes (id) ON DELETE CASCADE,
    PRIMARY KEY (trip_id, route_id)
);

CREATE TABLE IF NOT EXISTS trips_item_lists_references (
    trip_id int NOT NULL REFERENCES trips (id) ON DELETE CASCADE,
    item_list_id int NOT NULL REFERENCES item_lists (id) ON DELETE CASCADE,
    PRIMARY KEY (trip_id, item_list_id)
);
