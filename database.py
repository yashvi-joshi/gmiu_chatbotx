import sqlite3

DB_NAME = "gmiu.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS circulars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT,
            link TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()


def save_circulars(data):
    conn = connect_db()
    cursor = conn.cursor()

    for circular in data:
        cursor.execute("""
            INSERT INTO circulars (title, date, link)
            VALUES (?, ?, ?)
            ON CONFLICT(link) DO UPDATE SET
                title = excluded.title,
                date = excluded.date
        """, (
            circular["title"],
            circular["date"],
            circular["link"]
        ))

    conn.commit()
    conn.close()


def get_circulars():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, date, link
        FROM circulars
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "link": row[3]
        }
        for row in rows
    ]
