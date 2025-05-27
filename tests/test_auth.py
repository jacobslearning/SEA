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

def test_login_page_loads(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Register" in response.data

def test_register_user(client):
    response = client.post('/register',data={
        'username': 'test_user',
        'password': 'password',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful. Please log in" in response.data

def test_register_user_no_details(client):
    response = client.post('/register', follow_redirects=True)
    assert response.status_code == 200
    assert b"Username and password are required." in response.data

def test_register_username_taken(client):
    response = client.post('/register',data={
        'username': 'user',
        'password': 'password',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Username is already taken." in response.data

def test_login_incorrect_username(client):
    response = client.post('/login',data={
        'username': 'no_user',
        'password': 'password',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Incorrect username." in response.data

def test_login_incorrect_password(client):
    response = client.post('/login',data={
        'username': 'user',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Incorrect password." in response.data

def test_login(client):
    response = client.post('/login',data={
        'username': 'user',
        'password': 'password',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome, user!" in response.data

def test_logout(client):
    login_as_user(client)
    response = client.post('/logout',data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
    assert b"Login" in response.data

