import psycopg2
from flask import g, current_app as app
from urllib import parse
import logging
import contextlib
from psycopg2 import pool
import psycopg2.extras
import atexit

pool=None

@contextlib.contextmanager
def get_db_connection():
    try:
        global pool
        pool = psycopg2.pool.ThreadedConnectionPool(1, 20,
                                              user = app.config['DB_USER'],
                                              password = app.config['DB_PASSWORD'],
                                              host = app.config['DB_HOST'],
                                              port = app.config['DB_PORT'],
                                              database = app.config['DB_NAME'])
        connection = pool.getconn() 
        yield connection 
    finally: 
        pool.putconn(connection)

@contextlib.contextmanager
def get_db_cursor(commit=False): 
    with get_db_connection() as connection:
      cursor = connection.cursor(
                  cursor_factory=psycopg2.extras.RealDictCursor)
      try: 
          yield cursor 
          if commit: 
              connection.commit() 
      finally: 
          cursor.close()

def writeSQL(sql_query, data): 
    row=None
    with get_db_cursor(commit=True) as cursor:
       cursor.execute(sql_query, data)
       row = cursor.rowcount
    return row

def writeFetchSQL(sql_query, data): 
    row=None
    with get_db_cursor(commit=True) as cursor:
       cursor.execute(sql_query, data)
       row = cursor.fetchone()['id']
    return row

def readSQL(sql_query, data):
    row=None
    with get_db_cursor() as cursor:
       cursor.execute(sql_query, data) 
       row = cursor.fetchone()
    return row

def readManySQL(sql_query, data):
    row=None
    with get_db_cursor() as cursor:
       cursor.execute(sql_query, data) 
       row = cursor.fetchall()
    return row

@atexit.register
def close_connection_pool():
    global pool
    if pool:
        pool.closeall()
