"""
db.py — Database connection helper using PyMySQL
(No C compiler needed — pure Python MySQL driver)
"""
import pymysql
import pymysql.cursors
from flask import g, current_app


def get_db():
    """Return the per-request database connection (opens once, reused)."""
    if 'db' not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg['MYSQL_HOST'],
            user=cfg['MYSQL_USER'],
            password=cfg['MYSQL_PASSWORD'],
            database=cfg['MYSQL_DB'],
            cursorclass=pymysql.cursors.Cursor,
            autocommit=False,
            charset='utf8mb4',
        )
    return g.db


def close_db(e=None):
    """Close DB connection at the end of each request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    """Register teardown so connections are closed automatically."""
    app.teardown_appcontext(close_db)
