import os
import random
import sqlite3

db_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "..", "..", "..", "..", "db",
    "pixiv.db"
)

def init_db():

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    sql = "CREATE TABLE IF NOT EXISTS illu_url(\
        illu_id integer,\
        title TEXT,\
        author TEXT,\
        url TEXT,\
        enable INTEGER\
    );"
    cursor.execute(sql)

    conn.commit()
    conn.close()    

def save_illu_info(illu_id: int, title: str, author: str, url: str):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    sql = "SELECT illu_id FROM illu_url WHERE illu_id = %d"%(illu_id)
    cursor.execute(sql)
    if len(list(cursor)) > 0:
        conn.close()
        return 0

    title = title.replace("'", "''")
    title = title.replace('"', '""')
    author = author.replace("'", "''")
    author = author.replace('"', '""')

    sql = "INSERT INTO illu_url (illu_id, title, author, url, enable)\
        VALUES (%d, \'%s\', \'%s\', \'%s\', 1);"%(illu_id, title, author, url)
    cursor.execute(sql)
    conn.commit()

    conn.close()
    return 1

async def get_n_illu(number: int = 5):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    sql = "SELECT illu_id, title, author, url FROM illu_url\
        WHERE illu_id IN ( \
            SELECT illu_id \
            FROM illu_url \
            WHERE enable = 1 \
            ORDER BY RANDOM() \
            LIMIT %d\
        )"%(number)
    cursor.execute(sql)

    illu_list = [
        {
            "id": illu_info[0],
            "title": illu_info[1],
            "author": illu_info[2],
            "url": illu_info[3]
        }
    for illu_info in cursor]

    conn.close()

    return illu_list
