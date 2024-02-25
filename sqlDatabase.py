import sqlite3

DATABASE = 'C:\\Users\\admin\\Desktop\\flaskProject\\database\\users_vouchers.db'


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except sqlite3.Error as e:
        print(e)
    return conn


def query_db(query, args=()):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    data = cur.fetchall()
    conn.close()
    return data
