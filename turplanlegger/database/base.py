import time

import psycopg
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool


class Database:
    def __init__(self, app=None):
        self.app = None
        if app:
            self.init_db

    def init_db(self, app):
        self.logger = app.logger
        self.uri = app.config.get('DATABASE_URI')
        self.dbname = app.config.get('DATABASE_NAME')
        self.max_retries = app.config.get('DATABASE_MAX_RETRIES', 5)

        self.pool = ConnectionPool(
                conninfo=self.uri,
                dbname=self.dbname,
                client_encoding='UTF8',
                row_factory=namedtuple_row)


        self.logger.debug('Database connected')

        with app.open_resource('database/schema.sql') as f:
            try:
                self.conn.cursor().execute(f.read())
            except Exception as e:
                raise
                self.logger.exception(e)

        if (app.config.get('CREATE_ADMIN_USER', False)
                and not self.check_admin_user(app.config.get('ADMIN_EMAIL'))):
            self.logger.debug('Did not find admin user, creating one')
            from turplanlegger.utils.admin_user import create_admin_user
            create_admin_user(
                email=app.config.get('ADMIN_EMAIL'),
                password=app.config.get('ADMIN_PASSWORD')
            )

    def close(self, db):
        db.close()

    def destroy(self):
        conn = self.conn
        cursor = conn.cursor()
        for table in [
            'trips',
            'item_lists',
            'lists_items',
            'users',
            'routes',
            'notes',
            'trips_notes_references',
            'trips_routes_references',
            'trips_item_lists_references'
        ]:
            cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
        conn.commit()
        conn.close()

    def truncate_table(self, table: str):
        cursor = self.conn.cursor()
        cursor.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE')
        self.conn.commit()

    # Item List
    def get_item_list(self, id, deleted=False):
        select = """
            SELECT * FROM item_lists WHERE id = %s
        """
        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchone(select, [id])

    def get_item_list_by_owner(self, owner_id: str, deleted=False):
        select = """
            SELECT * FROM item_lists WHERE owner = %s
        """
        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchall(select, (owner_id,))

    def create_item_list(self, item_list):
        insert = """
            INSERT INTO item_lists (name, type, owner)
            VALUES (%(name)s, %(type)s, %(owner)s)
            RETURNING *
        """
        return self._insert(insert, vars(item_list))

    def delete_item_list(self, id):
        update = """
            UPDATE item_lists
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE id = %(id)s AND deleted = FALSE
            RETURNING deleted
        """
        return self._updateone(update, {'id': id}, returning=True)

    def rename_item_list(self, id, name):
        update = """
            UPDATE item_lists
                SET name=%(name)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'name': name}, returning=True)

    def change_item_list_owner(self, id, owner):
        update = """
            UPDATE item_lists
                SET owner=%(owner)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'owner': owner}, returning=True)

    def create_list_item(self, item_list_item):
        insert = """
            INSERT INTO lists_items (content, checked, item_list, owner)
            VALUES (%(content)s, %(checked)s, %(item_list)s, %(owner)s)
            RETURNING *
        """
        return self._insert(insert, vars(item_list_item))

    def delete_list_item(self, id):
        update = """
            UPDATE lists_items
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE id = %(id)s AND deleted = FALSE
            RETURNING deleted
        """
        return self._updateone(update, {'id': id}, returning=True)

    def delete_list_items_all(self, item_list_id):
        update = """
            UPDATE lists_items
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE item_list = %(item_list_id)s AND deleted = FALSE
        """
        return self._updateone(update, {'item_list_id': item_list_id})

    def toggle_list_item_check(self, id: int, checked: bool):
        update = """
            UPDATE lists_items
                SET checked=%(checked)s
                WHERE id = %(id)s AND deleted = FALSE
        """
        return self._updateone(update, {'id': id, 'checked': checked})

    def get_list_item(self, id, deleted=False):
        select = """
            SELECT * FROM lists_items WHERE id = %s
        """
        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchone(select, [id])

    def get_list_items(self, item_list_id, checked=None, deleted=False):
        select = """
            SELECT * FROM lists_items WHERE item_list = %s
        """

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'

        if checked is False:
            select += ' AND checked = FALSE'
        elif checked is True:
            select += ' AND checked = TRUE'

        return self._fetchall(select, [item_list_id])

    # Route
    def get_route(self, id, deleted=False):
        select = 'SELECT * FROM routes WHERE id = %s'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchone(select, (id,))

    def get_routes_by_owner(self, owner_id: str, deleted=False):
        select = 'SELECT * FROM routes WHERE owner = %s'
        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchall(select, (owner_id,))

    def create_route(self, route):
        insert = """
            INSERT INTO routes (route, owner, name, comment)
            VALUES (%(route)s, %(owner)s, %(name)s, %(comment)s)
            RETURNING *
        """
        return self._insert(insert, vars(route))

    def delete_route(self, id):
        update = """
            UPDATE routes
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE id = %(id)s AND deleted = FALSE
            RETURNING deleted
        """
        return self._updateone(update, {'id': id}, returning=True)

    def change_route_owner(self, id, owner):
        update = """
            UPDATE routes
                SET owner=%(owner)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'owner': owner}, returning=True)

    # Note
    def get_note(self, id, deleted=False):
        select = """
            SELECT * FROM notes WHERE id = %s
        """
        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchone(select, (id,))

    def get_note_by_owner(self, owner_id: str, deleted=False):
        select = 'SELECT * FROM notes WHERE owner = %s'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchall(select, (owner_id,))

    def create_note(self, note):
        insert = """
            INSERT INTO notes (owner, name, content)
            VALUES (%(owner)s, %(name)s, %(content)s)
            RETURNING *
        """
        return self._insert(insert, vars(note))

    def delete_note(self, id):
        update = """
            UPDATE notes
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE id = %(id)s AND deleted = FALSE
            RETURNING deleted
        """
        return self._updateone(update, {'id': id}, returning=True)

    def change_note_owner(self, id, owner):
        update = """
            UPDATE notes
                SET owner=%(owner)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'owner': owner}, returning=True)

    def rename_note(self, id, name):
        update = """
            UPDATE notes
                SET name=%(name)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'name': name}, returning=True)

    def update_note(self, id, content):
        update = """
            UPDATE notes
                SET content=%(content)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'content': content}, returning=True)

    # User
    def get_user(self, id, deleted=False):
        select = 'SELECT * FROM users WHERE id = %s::VARCHAR'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'

        return self._fetchone(select, (id,))

    def get_user_by(self, type: str, value, deleted=False):
        select = 'SELECT * FROM users WHERE'

        if type == 'email':
            select += ' email = %s'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'

        return self._fetchone(select, (value,))

    def create_user(self, user):
        insert = """
            INSERT INTO users (id, name, last_name, email, auth_method, password,  private)
            VALUES (%(id)s, %(name)s, %(last_name)s, %(email)s, %(auth_method)s, %(password)s, %(private)s)
            ON CONFLICT DO NOTHING
            RETURNING *
        """
        return self._insert(insert, vars(user))

    def rename_user(self, user):
        update = """
            UPDATE users
                SET name=%(name)s, last_name=%(last_name)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, vars(user), returning=True)

    def delete_user(self, id: int):
        update = """
            UPDATE users
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE id = %s AND deleted = FALSE
            RETURNING deleted
        """
        return self._updateone(update, (id,), returning=True)

    def toggle_private_user(self, id: int, private: bool):
        update = """
            UPDATE users
                SET private=%(private)s
                WHERE id = %(id)s
        """
        return self._updateone(update, {'id': id, 'private': private})

    def check_admin_user(self, email):
        select = 'SELECT id FROM users WHERE email=%s'
        return self._fetchone(select, (email,))

    # Trip
    def create_trip(self, trip):
        insert_trip = """
            INSERT INTO trips (name, owner, private, start_time, end_time)
            VALUES (%(name)s, %(owner)s, %(private)s,  %(start_time)s,  %(end_time)s)
            RETURNING *
        """
        return self._insert(insert_trip, vars(trip))

    def delete_trip(self, trip_id):
        update = """
            UPDATE trips
                SET deleted=TRUE, delete_time=CURRENT_TIMESTAMP
                WHERE id = %(id)s AND deleted = FALSE
            RETURNING deleted
        """
        return self._updateone(update, {'id': trip_id}, returning=True)

    def change_trip_owner(self, id, owner):
        update = """
            UPDATE trips
                SET owner=%(owner)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'owner': owner}, returning=True)

    def add_trip_note_reference(self, trip_id, note_id):
        insert_ref = """
            INSERT INTO trips_notes_references (trip_id, note_id)
            VALUES (%(trip_id)s, %(note_id)s)
            RETURNING *
        """
        return self._insert(insert_ref, {'trip_id': trip_id, 'note_id': note_id})

    def add_trip_item_list_reference(self, trip_id, item_list_id):
        insert_ref = """
            INSERT INTO trips_item_lists_references (trip_id, item_list_id)
            VALUES (%(trip_id)s, %(item_list_id)s)
            RETURNING *
        """
        return self._insert(insert_ref,  {'trip_id': trip_id, 'item_list_id': item_list_id})

    def add_trip_route_reference(self, trip_id, route_id):
        insert_ref = """
            INSERT INTO trips_routes_references (trip_id, route_id)
            VALUES (%(trip_id)s, %(route_id)s)
            RETURNING *
        """
        return self._insert(insert_ref,  {'trip_id': trip_id, 'route_id': route_id})

    def get_trip(self, id, deleted=False):
        select = 'SELECT * FROM trips WHERE id = %s'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchone(select, (id,))

    def get_trips_by_owner(self, owner_id: str, deleted=False):
        select = 'SELECT * FROM trips WHERE owner = %s'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchall(select, (owner_id,))

    def get_trip_notes(self, id):
        select = 'SELECT note_id FROM trips_notes_references WHERE trip_id = %s'
        return self._fetchall(select, (id,))

    def get_trip_routes(self, id):
        select = 'SELECT route_id FROM trips_routes_references WHERE trip_id = %s'
        return self._fetchall(select, (id,))

    def get_trip_item_lists(self, id):
        select = 'SELECT item_list_id FROM trips_item_lists_references WHERE item_list_id = %s'
        return self._fetchall(select, (id,))

    # Helpers
    def _insert(self, query, vars):
        """
        Insert, with return.
        """
        cursor = self.conn.cursor()
        # self._log(cursor, '_insert', query, vars)
        cursor.execute(query, vars)
        return cursor.fetchone()

    def _fetchone(self, query, vars):
        """
        Return none or one row.
        """
        cursor = self.conn.cursor()
        # self._log(cursor, '_fetchone', query, vars)
        cursor.execute(query, vars)
        self.conn.commit()
        return cursor.fetchone()

    def _fetchall(self, query, vars):
        """
        Return none or multiple row.
        """
        cursor = self.conn.cursor()
        # self._log(cursor, '_fetchall', query, vars)
        cursor.execute(query, vars)
        return cursor.fetchall()

    def _updateone(self, query, vars, returning=False):
        """
        Update, with optional return.
        """
        cursor = self.conn.cursor()
        # self._log(cursor, '-updateone', query, vars)
        cursor.execute(query, vars)
        return cursor.fetchone() if returning else None

    def _deleteone(self, query, vars, returning=False):
        """
        Delete, with optional return.
        """
        cursor = self.conn.cursor()
        # self._log(cursor, '_deleteone', query, vars)
        cursor.execute(query, vars)
        self.conn.commit()
        return cursor.fetchone() if returning else None

    def _log(self, cursor, query, vars):
        # self.logger.debug('{stars}\n{query}\n{stars}'.format(
        #     stars='*' * 40, query=cursor.mogrify(query, vars).decode('utf-8')))
        return False
