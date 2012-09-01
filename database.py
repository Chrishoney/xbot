from datetime import datetime
import os
import sys

import MySQLdb as db

HOST='localhost'
USER=os.getenv('USER')
PASSWD='password'
DB='seen'
PORT='3306'
UNIX_SOCKET='/tmp/msql.sock'

def connection():
    connection = MySQLdb.connect(
            host=HOST,
            user=USER,
            passwd=PASSWD,
            db=DB,
            port=PORT,
            unix_socket=UNIX_SOCKET
    )
    return connection

def get_cursor(connection):
    return connection.cursor()

def teardown(connection, cursor):
    try:
        connection.commit()
    except MySQLdb.DatabaseError:
        connection.rollback()
    finally:
        connection.close()
        cursor.close()

def execute(connection, command, args, cursor=None):
    if cursor is None:
        cursor = get_cursor(connection)
    cursor.execute(command, args)
    return cursor


def insert_seen(connection, name, time):
    connection.execute('''INSERT INTO seen (name, time)
                          VALUES (?, ?)''', (name, time))
    teardown(connection, cursor)

def check_seen(connection, name):
    cursor = connection.execute('''SELECT * FROM seen WHERE NAME=?''', name)
    row = cursor.fetchone()
    teardown(connection, cursor)
    return row

def create_database(connection, name=DB):
    cursor = connection.execute('''CREATE DATABASE ?''', name)
    teardown(connection, cursor)
    
def create_table(connection, name=DB):
    cursor = connection.execute('''CREATE TABLE ? (
                                   id INT NOT NULL AUTO_INCREMENT,
                                   name VARCHAR(120) NOT NULL,
                                   date DATETIME,
                                   PRIMARY KEY (id));''', name)
    teardown(connection, cursor)

if __name__ == '__main__':
    if 'y' in raw_input('really create db and table? > ')[0].lower()
        conn = connection()
        create_database()
        create_table()
    sys.exit()
