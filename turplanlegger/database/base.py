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
        for table in ['trips', 'lists', 'users', 'routes']:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        conn.commit()
        conn.close()

    # Lists
    def get_list(self, id):
        select = """
            SELECT * FROM lists WHERE id = %s
        """
        return self._fetchone(select, [id])

    def create_list(self, list):
        insert = """
            INSERT INTO lists (name, type, owner)
            VALUES (%(name)s, %(type)s, %(owner)s)
            RETURNING *
        """
        return self._insert(insert, vars(list))

    def rename_list(self, id, name):
        update = """
            UPDATE lists
                SET name=%(name)s
                WHERE id = %(id)s
            RETURNING *
        """
        return self._updateone(update, {'id': id, 'name': name}, returning=True)

    def create_list_iteam(self, list_item):
        insert = """
            INSERT INTO lists_items (content, checked, list, owner)
            VALUES (%(content)s, %(checked)s, %(list)s, %(owner)s)
            RETURNING *
        """
        return self._insert(insert, vars(list_item))

    def get_list_item(self, id):
        select = """
            SELECT * FROM lists_items WHERE id = %s
        """
        return self._fetchone(select, [id])

    def get_list_items(self, list_id, checked=None):
        select = """
            SELECT * FROM lists_items WHERE list = %s
        """
        if checked is False:
            select += ' AND checked = FALSE'
        elif checked is True:
            select += ' AND checked = TRUE'

        return self._fetchall(select, [list_id])

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

    def _log(self, cursor, query, vars):
        self.logger.debug('{stars}\n{query}\n{stars}'.format(
            stars='*' * 40, query=cursor.mogrify(query, vars).decode('utf-8')))