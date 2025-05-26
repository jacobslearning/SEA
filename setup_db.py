import sqlite3 as sql
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.executescript('''
    DROP TABLE IF EXISTS Asset;
    DROP TABLE IF EXISTS Department;
    DROP TABLE IF EXISTS User;
                         
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

    departments = [
        ('HR',),
        ('Customer Service',),
        ('IT',),
    ]
    cursor.executemany('INSERT INTO Department (name) VALUES (?)', departments)

    password_hash = generate_password_hash("password")
    users = [
        ('Jacob', password_hash, 'User'),
        ('Jake', password_hash, 'User'),
        ('Josh', password_hash, 'User'),
        ('admin', password_hash, 'Admin'),
    ]
    cursor.executemany('INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)', users)

    cursor.execute('SELECT id, username FROM User')
    user_map = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute('SELECT id, name FROM Department')
    dept_map = {row[1]: row[0] for row in cursor.fetchall()}

    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    assets = [
        ('Lenova XP5 15', 'Work laptop', 'Laptop', 'SN12345AL', date_now, 1, 1, user_map['Jacob'], dept_map['IT']),
        ('Iphone 15 Pro Max', 'Company phone', 'Phone', 'SN12346AL', date_now, 1, 1, user_map['Jacob'], dept_map['IT']),
        ('Windows 10 PC', 'Office desktop', 'Desktop', 'SN22345BO', date_now, 1, 0, user_map['Josh'], dept_map['Customer Service']),
        ('Ipad Pro', 'Tablet for presentations', 'Tablet', 'SN22346BO', date_now, 1, 1, user_map['Josh'], dept_map['Customer Service']),
        ('Lenova XP5 15', 'Development laptop', 'Laptop', 'SN32345CA', date_now, 1, 0, user_map['Jake'], dept_map['IT']),
        ('Iphone 14 Pro Max', 'Company phone', 'Phone', 'SN32346CA', date_now, 0, 1, user_map['Jake'], dept_map['HR']),
        ('Windows 10 PC', 'Windows PC for testing', 'Windows', 'SN32347CA', date_now, 1, 1, user_map['Jake'], dept_map['IT']),
        ('DELL 313183XP3', 'Main office workstation', 'Desktop', 'SN42345AD', date_now, 1, 1, user_map['Jacob'], dept_map['IT']),
        ('DELL 48248248XN2', 'Backup laptop', 'Laptop', 'SN42346AD', date_now, 0, 1, user_map['Jacob'], dept_map['IT']),
        ('Iphone 16', 'Company phone', 'Phone', 'SN42347AD', date_now, 1, 1, user_map['Jacob'], dept_map['HR']),
    ]

    cursor.executemany('''
        INSERT INTO Asset (
            name, description, type, serial_number, date_created,
            in_use, approved, owner_id, department_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', assets)

    connection.commit()
    connection.close()
    print("database.db created successfully.")

if __name__ == '__main__':
    init_db()
