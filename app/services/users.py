import sqlite3

DB_PATH = "/Users/harshavardhan/library.db"


def handle_user_registration(username, password):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # Check if user already exists
    cur.execute("SELECT name FROM users WHERE name=?", (username,))
    data = cur.fetchone()
    if data:
        return False
    cur.execute("INSERT INTO users (name, password,is_admin) VALUES (?, ?,?)", (username, password, False))
    con.commit()
    con.close()
    return True


def login(username, password):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE name=? and password=?", (username, password))
    data = cur.fetchone()
    if data:
        users_id = data[0]
        return True, users_id
    return False,-1


def admin_login(username, password):
    print("hi")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE name=? and password=? and is_admin=1", (username, password))
    data = cur.fetchone()
    if data:
        return True, data[0]
    return False,-1


