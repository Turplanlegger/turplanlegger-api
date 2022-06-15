import time

import psycopg2
from psycopg2.extras import NamedTupleCursor


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

        self.conn = self.connect()
        self.logger.debug('Database connected')

        with app.open_resource('database/schema.sql') as f:
            try:
                self.conn.cursor().execute(f.read())
                self.conn.commit()
            except Exception as e:
                raise
                self.logger.exception(e)

    def connect(self):
        retry = 0
        while True:
            try:
                conn = psycopg2.connect(
                    dsn=self.uri,
                    dbname=self.dbname,
                    cursor_factory=NamedTupleCursor
                )
                conn.set_client_encoding('UTF8')
                break
            except Exception as e:
                self.logger.exception(str(e))
                retry += 1
                if retry > self.max_retries:
                    conn = None
                    break
                else:
                    backoff = 2 ** retry
                    print(f'Retry attempt {retry}/{self.max_retries} (wait={backoff}s)...')
                    time.sleep(backoff)

        if conn:
            return conn
        else:
            raise RuntimeError('Database connect error. Failed to connect'
                               f' after {self.max_retries} retries.')

    def close(self, db):
        db.close()

    def destroy(self):
        conn = self.conn
        cursor = conn.cursor()
        for table in ['trips', 'item_lists', 'lists_items', 'users', 'routes', 'notes']:
            cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE')

        conn.commit()
        conn.close()

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
        select = """
            SELECT * FROM routes WHERE id = %s
        """
        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'
        return self._fetchone(select, [id])

    def create_route(self, route, owner):
        insert = """
            INSERT INTO routes (route, owner)
            VALUES (%(route)s, %(owner)s)
            RETURNING *
        """
        return self._insert(insert, {'route': route, 'owner': owner})

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
                SET deleted=TRUE, deleted_time=CURRENT_TIMESTAMP
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
        select = 'SELECT * FROM users WHERE id = %s'

        if deleted:
            select += ' AND deleted = TRUE'
        else:
            select += ' AND deleted = FALSE'

        return self._fetchone(select, (id,))

    # User
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
            INSERT INTO users (name, last_name, email, auth_method, password,  private)
            VALUES (%(name)s, %(last_name)s, %(email)s, %(auth_method)s, %(password)s, %(private)s)
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

    # Helpers
    def _insert(self, query, vars):
        """
        Insert, with return.
        """
        cursor = self.conn.cursor()
        self._log(cursor, query, vars)
        cursor.execute(query, vars)
        self.conn.commit()
        return cursor.fetchone()

    def _fetchone(self, query, vars):
        """
        Return none or one row.
        """
        cursor = self.conn.cursor()
        self._log(cursor, query, vars)
        cursor.execute(query, vars)
        return cursor.fetchone()

    def _fetchall(self, query, vars):
        """
        Return none or multiple row.
        """
        cursor = self.conn.cursor()
        self._log(cursor, query, vars)
        cursor.execute(query, vars)
        return cursor.fetchall()

    def _updateone(self, query, vars, returning=False):
        """
        Update, with optional return.
        """
        cursor = self.conn.cursor()
        self._log(cursor, query, vars)
        cursor.execute(query, vars)
        self.conn.commit()
        return cursor.fetchone() if returning else None

    def _deleteone(self, query, vars, returning=False):
        """
        Delete, with optional return.
        """
        cursor = self.conn.cursor()
        self._log(cursor, query, vars)
        cursor.execute(query, vars)
        self.conn.commit()
        return cursor.fetchone() if returning else None

    def _log(self, cursor, query, vars):
        self.logger.debug('{stars}\n{query}\n{stars}'.format(
            stars='*' * 40, query=cursor.mogrify(query, vars).decode('utf-8')))
