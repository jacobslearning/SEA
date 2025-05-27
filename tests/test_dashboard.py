import pytest
from app import app
from routes.utils import get_db
from werkzeug.security import generate_password_hash
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False 
    app.config['DATABASE'] = 'test.db'  
    client = app.test_client()

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript('''
                             
            DROP TABLE IF EXISTS User;
            DROP TABLE IF EXISTS Department;
            DROP TABLE IF EXISTS Asset;
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
        db.commit()
        password_hash = generate_password_hash("password")
        users = [
            ('admin', password_hash, 'Admin'),
            ('user', password_hash, 'User'),
        ]
        cursor.executemany('INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)', users)
        departments = [
        ('HR',),
        ('Customer Service',),
        ('IT',),
        ('Store Operations',),
        ('Security',),
        ('Marketing',),
    ]
        cursor.executemany('INSERT INTO Department (name) VALUES (?)', departments)
        cursor.execute('SELECT id, username FROM User')
        user_map = {row[1]: row[0] for row in cursor.fetchall()}

        cursor.execute('SELECT id, name FROM Department')
        dept_map = {row[1]: row[0] for row in cursor.fetchall()}

        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        assets = [
            ('Lenova XP5 15', 'Work laptop', 'Laptop', 'SN12345AL32323jjjj', date_now, 1, 1, user_map['user'], dept_map['IT']),
            ('Iphone 15 Pro Max', 'Company phone', 'Phone', 'SN12346AL31ddddeaaac', date_now, 1, 1, user_map['user'], dept_map['IT']),
            ('Windows 10 PC', 'Office desktop', 'Desktop', 'SN22345BO38791389173', date_now, 1, 0, user_map['user'], dept_map['Customer Service']),
        ]

        cursor.executemany('''
            INSERT INTO Asset (
                name, description, type, serial_number, date_created,
                in_use, approved, owner_id, department_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', assets)

        db.commit()

    return client

def login_as_admin(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)

def login_as_user(client):
    client.post('/login', data={
        'username': 'user',
        'password': 'password'
    }, follow_redirects=True)

def test_dashboard_page_loads(client):
    login_as_admin(client)
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"All Pending Assets" in response.data
    assert b"Welcome, admin!" in response.data

def test_metrics_load(client):
    login_as_admin(client)
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Total Assets" in response.data
    assert b"Pending Approvals" in response.data
    assert b"Total Users" in response.data
    assert b"Departments" in response.data
    assert b"3" in response.data
    assert b"1" in response.data
    assert b"2" in response.data
    assert b"6" in response.data

def test_role_loads_as_admin(client):
    login_as_admin(client)
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Role: Admin" in response.data

def test_role_loads_as_user(client):
    login_as_user(client)
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Role: User" in response.data