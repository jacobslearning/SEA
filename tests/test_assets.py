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

def test_assets_page_loads(client):
    login_as_admin(client)
    response = client.get('/assets', follow_redirects=True)
    assert response.status_code == 200
    assert b"Create New Asset" in response.data

def test_asset_edit(client):
    login_as_admin(client)
    response = client.post('/asset/edit/2', data={
        'name': 'iphone 14 pro max test',
        'description': 'test',
        'type': 'Phone',
        'serial_number': 'SN32346CA1111dddeee0909lkop',
        'in_use': '1',
        'department_id': '2',
        'assigned_user_id': '2',
        'approved': '0',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Asset updated" in response.data

def test_asset_delete(client):
    login_as_admin(client)
    response = client.post('/asset/delete/2', follow_redirects=True)
    assert response.status_code == 200
    assert b"Asset deleted" in response.data

def test_create_asset(client):
    login_as_admin(client)
    response = client.post('/asset/create',data={
        'name': 'iphone 14 pro max test test',
        'description': 'test',
        'type': 'Phone',
        'serial_number': 'SN32346CA1111dddeeeefffff2pl432dj1',
        'in_use': '1',
        'department_id': '2',
        'assigned_user_id': '2',
        'approved': '0',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Asset created and awaiting approval" in response.data

def test_create_asset_requires_login(client):
    response = client.post('/asset/create', data={
        'name': 'iphone 14 pro max test test',
        'description': 'test',
        'type': 'Phone',
        'serial_number': 'SN32346CA1111dddeeeefffff2ee56108cn',
        'in_use': '1',
        'department_id': '2',
        'assigned_user_id': '2',
        'approved': '0',
    }, follow_redirects=True)

    assert b"Login" in response.data or response.status_code == 403

def test_asset_user_can_not_approve(client):
    login_as_user(client)
    response = client.post('/asset/approve/3', follow_redirects=True)
    assert b"Unauthorised Access" in response.data


def test_asset_approve(client):
    login_as_admin(client)
    response = client.post('/asset/approve/3', follow_redirects=True)
    assert response.status_code == 200
    assert b"Asset approved" in response.data