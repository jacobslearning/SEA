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
        ('Store Operations',),
        ('Security',),
        ('Marketing',),
    ]
    cursor.executemany('INSERT INTO Department (name) VALUES (?)', departments)

    password_hash = generate_password_hash("password")
    users = [
        ('harry', password_hash, 'User'),
        ('jacob', password_hash, 'User'),
        ('josh', password_hash, 'User'),
        ('tHisIsCool12', password_hash, 'User'),
        ('Harry_Truman', password_hash, 'User'),
        ('Doris_Day', password_hash, 'Admin'),
        ('Joe_DiMaggio', password_hash, 'User'),
        ('Joe_McCarthy', password_hash, 'User'),
        ('Richard_Nixon', password_hash, 'User'),
        ('Marilyn_Monroe', password_hash, 'User'),
        ('Rosenbergs', password_hash, 'User'),
        ('Roy_Cohn', password_hash, 'User'),
        ('Juan_Perón', password_hash, 'User'),
        ('Einstein', password_hash, 'User'),
        ('James_Dean', password_hash, 'User'),
        ('Elvis_Presley', password_hash, 'User'),
        ('Brigitte_Bardot', password_hash, 'User'),
        ('Nikita_Khrushchev', password_hash, 'User'),
        ('Princess_Grace', password_hash, 'User'),
        ('Peyton_Place', password_hash, 'User'),
        ('Mickey_Mantle', password_hash, 'User'),
        ('Jack_Kerouac', password_hash, 'User'),
        ('Charles_de_Gaulle', password_hash, 'User'),
        ('Buddy_Holly', password_hash, 'User'),
        ('Hemingway', password_hash, 'User'),
        ('Bob_Dylan', password_hash, 'User'),
        ('John_Glenn', password_hash, 'User'),
        ('Pope_Paul', password_hash, 'User'),
        ('Malcolm_X', password_hash, 'User'),
        ('JFK', password_hash, 'User'),
        ('Ho_Chi_Minh', password_hash, 'User'),
        ('Ronald_Reagan', password_hash, 'Admin'),
        ('Sally_Ride', password_hash, 'User'),
        ('Bernhard_Goetz', password_hash, 'User'),
        ('admin', password_hash, 'Admin'),
        
    ]
    cursor.executemany('INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)', users)

    cursor.execute('SELECT id, username FROM User')
    user_map = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute('SELECT id, name FROM Department')
    dept_map = {row[1]: row[0] for row in cursor.fetchall()}

    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    assets = [
        ('Lenova XP5 15', 'Work laptop', 'Laptop', 'SN12345AL32323', date_now, 1, 1, user_map['jacob'], dept_map['IT']),
        ('Iphone 15 Pro Max', 'Company phone', 'Phone', 'SN12346AL', date_now, 1, 1, user_map['jacob'], dept_map['IT']),
        ('Windows 10 PC', 'Office desktop', 'Desktop', 'SN22345BO', date_now, 1, 0, user_map['harry'], dept_map['Customer Service']),
        ('Ipad Pro', 'Tablet for presentations', 'Tablet', 'SN22346BO', date_now, 1, 1, user_map['harry'], dept_map['Customer Service']),
        ('Lenova XP5 15', 'Development laptop', 'Laptop', 'SN32345CA', date_now, 1, 0, user_map['harry'], dept_map['IT']),
        ('Iphone 14 Pro Max', 'Company phone', 'Phone', 'SN32346CA', date_now, 0, 1, user_map['harry'], dept_map['HR']),
        ('Windows 10 PC', 'Windows PC for testing', 'Windows', 'SN32347CA', date_now, 1, 1, user_map['harry'], dept_map['IT']),
        ('DELL 313183XP3', 'Main office workstation', 'Desktop', 'SN42345AD3232323', date_now, 1, 1, user_map['jacob'], dept_map['IT']),
        ('DELL 48248248XN2', 'Backup laptop', 'Laptop', 'SN42346AD11134', date_now, 0, 1, user_map['jacob'], dept_map['IT']),
        ('Iphone 16', 'Company phone', 'Phone', 'SN42347ADDDDDDF', date_now, 1, 1, user_map['jacob'], dept_map['HR']),
        ('HP EliteBook 840', 'Work laptop', 'Laptop', 'HPEL-2485KWS-001', date_now, 1, 0, user_map['Bob_Dylan'], dept_map['IT']),
        ('iPhone 14', 'Company phone', 'Phone', 'IPHN-7453MNS-119', date_now, 1, 1, user_map['JFK'], dept_map['HR']),
        ('Dell OptiPlex 7090', 'Office desktop', 'Desktop', 'DELL-OPT7090-663', date_now, 1, 0, user_map['Elvis_Presley'], dept_map['Customer Service']),
        ('iPad Air', 'Tablet for presentations', 'Tablet', 'IPAD-2023AIR-384', date_now, 1, 0, user_map['Sally_Ride'], dept_map['Marketing']),
        ('MacBook Pro 16"', 'Development laptop', 'Laptop', 'MBPRO16-MKT-881FF', date_now, 1, 0, user_map['James_Dean'], dept_map['IT']),
        ('Zebra TC52', 'Inventory scanner', 'Device', 'ZEBRA-TC52-455KFF', date_now, 0, 1, user_map['Juan_Perón'], dept_map['Store Operations']),
        ('Samsung Galaxy Tab S8', 'Tablet for stock check', 'Tablet', 'SMSNG-TABS8-922FFFF', date_now, 1, 1, user_map['Joe_DiMaggio'], dept_map['Store Operations']),
        ('DELL 313183XP3', 'Main office workstation', 'Desktop', 'SN42345ADEEEEA', date_now, 1, 0, user_map['Richard_Nixon'], dept_map['IT']),
        ('HP EliteBook 840', 'Backup laptop', 'Laptop', 'SN42346AD33113D', date_now, 0, 1, user_map['Princess_Grace'], dept_map['Marketing']),
        ('iPhone 16', 'Company phone', 'Phone', 'SN42347ADDDDAAAA', date_now, 1, 1, user_map['Malcolm_X'], dept_map['Security']),
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
