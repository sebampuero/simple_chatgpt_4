import psycopg2

import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
        except psycopg2.OperationalError:
            raise

    def __del__(self):
        if self.conn:
            self.conn.close()

    def execute(self, sql, *args):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, args)
            self.conn.commit()
            return cur
        except:
            logger.error(f"Error with {sql} and args {args}", exc_info=True)
            return None

    def fetch_one(self, sql, *args):
        cur = self.execute(sql, *args)
        return cur.fetchone() if cur else None

    def fetch_all(self, sql, *args):
        cur = self.execute(sql, *args)
        return cur.fetchall() if cur else None