import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'zabytkownik.db')

def get_connection():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def get_cursor(connection=None):
    if connection is None:
        connection=get_connection()
    return connection.cursor()