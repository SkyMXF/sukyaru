import os
import hashlib
import sqlite3

db_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "..", "..", "..", "..", "db",
    "reminder.db"
)
md5_salt = "mxf"

def get_md5(text):
    md5_obj = hashlib.md5()
    md5_obj.update((text + md5_salt).encode("utf-8"))
    return md5_obj.hexdigest()

def init_db():

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    sql = "CREATE TABLE IF NOT EXISTS user_key(\
        uQQ integer,\
        uKey TEXT\
    );"
    cursor.execute(sql)
    sql = "CREATE TABLE IF NOT EXISTS reminds(\
        uQQ integer,\
        remind_at REAL,\
        content TEXT\
    );"
    cursor.execute(sql)

    conn.commit()
    conn.close()    

async def save_reminds(user_qq: int, remind_at: float, text: str):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    sql = "INSERT INTO reminds (uQQ, remind_at, content)\
        VALUES (%d, %f, '%s');"%(user_qq, remind_at, text)
    cursor.execute(sql)
    conn.commit()

    sql = "SELECT ROWID, uQQ, remind_at, content FROM reminds \
        WHERE uQQ = %d \
        AND remind_at = %f \
        AND content = '%s'"%(user_qq, remind_at, text)
    cursor.execute(sql)

    rowid = None
    for remind_info in cursor:
        rowid = remind_info[0]
        break

    conn.close()

    return rowid

async def read_reminds(user_qq: int = None) -> list:

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    if user_qq is None:
        sql = "SELECT rowid, uQQ, remind_at, content FROM reminds"
        cursor.execute(sql)
    else:
        sql = "SELECT rowid, uQQ, remind_at, content FROM reminds WHERE uQQ = %d"%(user_qq)
        cursor.execute(sql)

    remind_list = [
        {
            "rowid": remind_info[0],
            "qq": remind_info[1],
            "time": remind_info[2],
            "text": remind_info[3]
        }
    for remind_info in cursor]

    conn.close()

    return remind_list

async def remove_remind(rowid: int):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    sql = "DELETE FROM reminds WHERE rowid = %d;"%(rowid)
    cursor.execute(sql)
    conn.commit()

    conn.close()

async def get_key(user_qq: int):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    sql = "SELECT uQQ, uKey FROM user_key WHERE uQQ = %d;"%(user_qq)
    cursor.execute(sql)

    results = list(cursor)
    if len(results) > 0:
        key = results[0][1]
    else:
        key = get_md5(str(user_qq))
        sql = "INSERT INTO user_key (uQQ, uKey)\
            VALUES (%d, '%s');"%(user_qq, key)
        cursor.execute(sql)
        conn.commit()

    conn.close()

    return key

def get_qq(user_key: str):

    user_qq = None

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    sql = "SELECT uQQ FROM user_key WHERE uKey = '%s';"%(user_key)
    cursor.execute(sql)

    user_info = list(cursor)
    if len(user_info) > 0:
        user_qq = user_info[0][0]

    conn.close()

    return user_qq