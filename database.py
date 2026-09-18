#database.py
import sqlite3
import hashlib


DATABASE = "messaging.db"


def get_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def initialize_database():

    conn = get_conn()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Contacts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            contact TEXT NOT NULL,
            UNIQUE(username, contact)
        )''')

    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

    conn.commit()
    conn.close()


def register_user(username, password):

    conn = get_conn()

    try:

        password_hash = hash_password(password)

        conn.execute(
            """
            INSERT INTO users(username, password)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        conn.commit()

        return True, "Registration successful"

    except sqlite3.IntegrityError:

        return False, "Username already exists"

    finally:

        conn.close()


def authenticate_user(username, password):

    conn = get_conn()

    password_hash = hash_password(password)

    result = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username=? AND password=?
        """,
        (username, password_hash)
    ).fetchone()

    conn.close()

    return result is not None


def add_contact(username, contact):

    conn = get_conn()

    try:

        conn.execute(
            """
            INSERT INTO contacts(username, contact)
            VALUES (?, ?)
            """,
            (username, contact)
        )

        conn.commit()

        return True, "Contact added"

    except sqlite3.IntegrityError:

        return False, "Contact already exists"

    finally:

        conn.close()


def get_contacts(username):

    conn = get_conn()

    rows = conn.execute(
        """
        SELECT contact
        FROM contacts
        WHERE username=?
        """,
        (username,)
    ).fetchall()

    conn.close()

    return [row["contact"] for row in rows]


def save_message(sender, receiver, message):

    conn = get_conn()

    conn.execute(
        """
        INSERT INTO messages
        (sender, receiver, message)
        VALUES (?, ?, ?)
        """,
        (sender, receiver, message)
    )

    conn.commit()
    conn.close()


def get_messages(user1, user2):

    conn = get_conn()

    rows = conn.execute(
        '''
        SELECT sender, receiver, message, timestamp
        FROM messages
        WHERE(sender=? AND receiver=?)
        OR
        (sender=? AND receiver=?)
        ORDER BY timestamp''',
        (user1, user2, user2, user1)
    ).fetchall() #fetchall from database

    conn.close()

    return [dict(row) for row in rows] #process and return all 
