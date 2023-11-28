"""
This script converts all of the http://localhost:port and http://127.0.0.1:port
to http://www.chimp-chat.win. We will be using this domain name for our site.

TODO: Once certs are set up, we will use https instead of http.
"""

import sqlite3
from typing import Optional
import re



def connect_to_db(path: str) -> Optional[tuple[sqlite3.Connection, sqlite3.Cursor]]:
    """
    Connects to the database and returns the connection and cursor objects.
    """
    try:
        conn = sqlite3.connect(path)
        c = conn.cursor()
        return conn, c
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None




def get_single_column(c: sqlite3.Cursor, table: str, column: str) -> list[tuple[str, str]]:
    """
    Returns a list of all of the values in a single column.
    """
    rows = c.execute(f"SELECT id,{column} FROM {table} where {column} like ?", ('%' + 'chimp-chat.win' + '%',)).fetchall()
    return [(row[0], row[1]) for row in rows]



def update_single_column(c: sqlite3.Cursor, table: str, column: str, rows: list[tuple[str,str]] ) -> bool:
    """
    Updates the values in a single column.
    """
    try:
        reg = re.compile(r'www.chimp-chat.win')
        for row_id, row_value in rows:
            new_value = reg.sub('localhost:8000', row_value)
            print(f"UPDATE {table} SET {column} = '{new_value}' WHERE id = {row_id};")
            c.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (new_value, row_id))
        return True
    except sqlite3.Error as e:
        print(f"Error updating database: {e}")
        return False



def convert_single_column(c: sqlite3.Cursor, table: str, column: str) -> bool:
    """
    Converts a single column in a table to the new domain name.
    """
    rows = get_single_column(c, table, column)
    if not rows:
        return False

    return update_single_column(c, table, column, rows)


def main():

    columns = {
        # "accounts_authoruser" : ["host", "profile_image", "url"]
        "posts_posts": ["source", "origin"]
        # "posts_posts": ["source", "origin", "author_host", "author_url", "comments"],
        # "posts_comments": ["author_host", "author_url"]
    }

    con_t = connect_to_db("../db.sqlite3")
    if not con_t:
        return
    conn, c = con_t

    for table, cols in columns.items():
        for col in cols:
            print(f"Converting {col} in {table}")
            if not convert_single_column(c, table, col):
                print(f"Error converting {col} in {table}")
                return

    conn.commit()
    c.close()
    conn.close()


main()






