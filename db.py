import sqlite3

DB_NAME = "gym_members.db"

def create_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_number TEXT UNIQUE NOT NULL,
            subscription TEXT NOT NULL,
            price REAL NOT NULL,
            start_date TEXT NOT NULL,
            days_left INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_member(name, id_number, subscription, price, start_date, days_left=30):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memberships (name, id_number, subscription, price, start_date, days_left)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, id_number, subscription, price, start_date, days_left))
    conn.commit()
    conn.close()

def get_all_members():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memberships")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_days_left(member_id, days_left):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE memberships SET days_left = ? WHERE id = ?", (days_left, member_id))
    conn.commit()
    conn.close()

def delete_member(member_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memberships WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

