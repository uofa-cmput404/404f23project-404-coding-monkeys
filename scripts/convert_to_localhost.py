"""
This script converts all of the http://localhost:port and http://127.0.0.1:port
to http://www.chimp-chat.win. We will be using this domain name for our site.

TODO: Once certs are set up, we will use https instead of http.
"""

import sqlite3
import psycopg2
from typing import Optional
import re


def connect_to_db():
    """Connects to postgres DB"""
    db_params={
        "host":"happy-yak-farm.net",
        "database":"chimp-chat-dev",
        "user":"qHB86EHdP7r^x2V",
        "port":"5432",
        "password":"gusv^Hwi3MvMsVU6fkt7Z7crZ5gWBSKKTBWC"
    }
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        return conn, cursor
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None, None



def get_single_column(c, table, column, useUUID=False):
    """
    Returns a list of all of the values in a single column.
    """
    if useUUID:
        query = f"SELECT uuid, {column} FROM {table} WHERE {column} LIKE %s"
        print(query)
    else:
        query = f"SELECT id, {column} FROM {table} WHERE {column} LIKE %s"
        print(query)

    # Use parameterized query to avoid SQL injection
    rows = c.execute(query, ('%https://chimp-chat-1e0cca1cc8ce.herokuapp.com%',))
    print(rows)

    return [(row[0], row[1]) for row in rows]



def update_single_column(c: psycopg2.extensions.cursor, table: str, column: str, rows: list[tuple[str,str]], useUUID=False) -> bool:
    """
    Updates the values in a single column.
    """
    try:
        reg = re.compile(r'https://chimp-chat-1e0cca1cc8ce.herokuapp.com')
        for row_id, row_value in rows:
            new_value = reg.sub('http://localhost:8000', row_value)
            if useUUID:
                query = f"UPDATE {table} SET {column} = %s WHERE uuid = %s"
            else:
                query = f"UPDATE {table} SET {column} = %s WHERE id = %s"
            
            c.execute(query, (new_value, row_id))

        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        return False





def convert_single_column(c: sqlite3.Cursor, table: str, column: str, useUUID = False) -> bool:
    """
    Converts a single column in a table to the new domain name.
    """
    rows = get_single_column(c, table, column, useUUID)
    if not rows:
        return False

    return update_single_column(c, table, column, rows, useUUID)


def main():

    id_columns = {
        "accounts_authoruser" : ["host", "profile_image", "url"]
    }

    uuid_columns = {
        "posts_posts": ["source", "origin", "author_host", "author_url", "comments"],
        "posts_comments": ["author_host", "author_url"]
    }

    conn, c = connect_to_db()
    print(conn)
    print(c)

    for table, cols in id_columns.items():
        for col in cols:
            print(f"Converting {col} in {table}")
            if not convert_single_column(c, table, col):
                print(f"Error converting {col} in {table}")
                return
    
    for table, cols in uuid_columns.items():
        for col in cols:
            print(f"Converting {col} in {table}")
            if not convert_single_column(c, table, col, useUUID=True):
                print(f"Error converting {col} in {table}")
                return

    conn.commit()
    c.close()
    conn.close()


main()






