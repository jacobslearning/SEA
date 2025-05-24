import sqlite3 as sql

def init_db():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'User'))
    );

    CREATE TABLE IF NOT EXISTS Department (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Asset (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        type TEXT,
        serial_number TEXT UNIQUE,
        date_created TEXT,
        in_use INTEGER NOT NULL DEFAULT 1,
        approved INTEGER NOT NULL DEFAULT 0,
        owner_id INTEGER,
        department_id INTEGER,
        FOREIGN KEY(owner_id) REFERENCES User(id),
        FOREIGN KEY(department_id) REFERENCES Department(id)
    );
    ''')
# TODO: insert some sample data in here 
    connection.commit()
    connection.close()
    print("database.db initialized successfully.")

if __name__ == '__main__':
    init_db()
