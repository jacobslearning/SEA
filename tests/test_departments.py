import pytest
from app import app
from routes.utils import get_db
from werkzeug.security import generate_password_hash

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

def test_departments_page_loads(client):
    login_as_admin(client)
    response = client.get('/departments', follow_redirects=True)
    assert response.status_code == 200
    assert b"Add Department" in response.data

def test_department_edit(client):
    login_as_admin(client)
    response = client.post('/department/edit/2', data={
        'name': 'new department',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Department new department updated" in response.data

def test_department_delete(client):
    login_as_admin(client)
    response = client.post('/department/delete/7', follow_redirects=True)
    assert response.status_code == 200
    assert b"Department deleted" in response.data

def test_create_department(client):
    login_as_admin(client)
    response = client.post('/department/create', data={
        'name': 'new department',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"new department" in response.data

def test_create_department_requires_login(client):
    response = client.post('/department/create', data={
        'name': 'department name',
    }, follow_redirects=True)

    assert b"Login" in response.data or response.status_code == 403

def test_department_user_can_not_add(client):
    login_as_user(client)
    response = client.get('/departments', follow_redirects=True)

    assert response.status_code == 200
    assert b"Add Department" not in response.data

