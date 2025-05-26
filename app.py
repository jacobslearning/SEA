from flask import Flask, flash, g, render_template, request, redirect, session, url_for
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'test'
app.config['DATABASE'] = 'database.db'

# database helper functions

def get_db():
    if 'db' not in g:
        g.db = sql.connect(app.config['DATABASE'])
        g.db.row_factory = sql.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cursor = get_db().execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    return cursor.lastrowid

def current_user():
    if 'user_id' in session:
        return query_db('SELECT * FROM User WHERE id = ?', [session['user_id']], one=True)
    return None

# login decorater 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'Admin':
            flash("Unauthorised Access", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'User' 

        if not username or not password:
            flash('Username and password are required.', 'danger')
        elif query_db('SELECT id FROM User WHERE username = ?', [username], one=True):
            flash('Username is already taken.', 'danger')
        else:
            password_hash = generate_password_hash(password)
            execute_db('INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)', (username, password_hash, role))
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = query_db('SELECT * FROM User WHERE username = ?', [username], one=True)
        
        if user is None:
            flash('Incorrect username.', 'danger')
        elif not check_password_hash(user['password_hash'], password):
            flash('Incorrect password.', 'danger')
        else:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# assets 
@app.route('/assets')
@login_required
def assets():
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()

    if user['role'] == 'Admin':
         cursor.execute('''
            SELECT a.*, u.username AS owner_username, d.name AS department_name
            FROM Asset a
            LEFT JOIN User u ON a.owner_id = u.id
            LEFT JOIN Department d ON a.department_id = d.id
        ''')
    else:
        cursor.execute('''
            SELECT a.*, u.username AS owner_username, d.name AS department_name
            FROM Asset a
            LEFT JOIN User u ON a.owner_id = u.id
            LEFT JOIN Department d ON a.department_id = d.id
            WHERE a.owner_id = ?
        ''', (user['id'],))

    assets = cursor.fetchall()

    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    cursor.execute("SELECT id, username FROM User ORDER BY username ASC")
    users = cursor.fetchall()

    return render_template('assets.html', assets=assets, user=user, departments=departments, users=users)

@app.route('/asset/create', methods=['POST'])
@login_required
def create_asset():
    data = request.form
    connection = get_db()
    cursor = connection.cursor()

    date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO Asset (name, description, type, serial_number, date_created, in_use, approved, owner_id, department_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'], data['description'], data['type'], data['serial_number'], date_created,
        int(data.get('in_use', 1)),int(data.get('approved', 1)), data['assigned_user_id'], data['department_id']
    ))
    connection.commit()
    flash("Asset created and awaiting approval", "success")
    return redirect(url_for('assets'))

@app.route('/asset/edit/<int:asset_id>', methods=['POST'])
@login_required
def edit_asset(asset_id):
    data = request.form
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Asset WHERE id = ?", (asset_id,))
    asset = cursor.fetchone()

    if asset is None or (user['role'] != 'Admin' and asset['owner_id'] != user['id']):
        flash("Unauthorised Access", "danger")
        return redirect(url_for('assets'))

    cursor.execute("""
        UPDATE Asset SET
        name = ?, description = ?, type = ?, serial_number = ?, in_use = ?, department_id = ?, owner_id = ?,
        approved = ?
        WHERE id = ?
    """, (
        data['name'], data['description'], data['type'], data['serial_number'],
        int(data.get('in_use', 1)), data['department_id'], data['assigned_user_id'],
        int(data.get('approved', 0)) if user['role'] == 'Admin' else asset['approved'],
        asset_id
    ))
    connection.commit()
    flash("Asset updated", "success")
    return redirect(url_for('assets'))

@app.route('/asset/delete/<int:asset_id>', methods=['POST'])
@login_required
def delete_asset(asset_id):
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Asset WHERE id = ?", (asset_id,))
    asset = cursor.fetchone()

    if asset is None or (user['role'] != 'Admin' and asset['owner_id'] != user['id']):
        flash("Unauthorised Access", "danger")
        return redirect(url_for('assets'))

    cursor.execute("DELETE FROM Asset WHERE id = ?", (asset_id,))
    connection.commit()
    flash("Asset deleted", "info")
    return redirect(url_for('assets'))

@app.route('/asset/approve/<int:asset_id>', methods=['POST'])
@login_required
def approve_asset(asset_id):
    user = current_user()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('assets'))

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE Asset SET approved = 1 WHERE id = ?", (asset_id,))
    connection.commit()
    flash("Asset approved", "success")
    return redirect(url_for('assets'))


@app.route('/departments')
@login_required
def departments():
    print("departments page")

# users routes
@app.route('/users')
@login_required
def users():
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()
    
    if user['role'] == 'Admin':
        cursor.execute("SELECT id, username, password_hash, role FROM User")
    else:
        cursor.execute("SELECT id, username, password_hash, role FROM User WHERE id = ?", (int(user['id']),))
    users = cursor.fetchall()
    return render_template('users.html', users=users, user=user)

@app.route('/user/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    user = current_user()
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if user['role'] != 'Admin' and user['id'] != user_id:
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users'))
    
    if user['role'] != 'Admin':
        role = "User"

    connection = get_db()
    cursor = connection.cursor()
    # if value is [HIDDEN], user is not changing their password, if value is different, password should be hashed and updated in DB
    if password == '[HIDDEN]':
        cursor.execute('UPDATE User SET username = ?, role = ? WHERE id = ?', (username, role, user_id))
    else:
        password_hash = generate_password_hash(password)
        cursor.execute('UPDATE User SET username = ?, password_hash = ?, role = ? WHERE id = ?', (username, password_hash, role, user_id))
    connection.commit()
    flash(f"User {username} updated", "success")
    return redirect(url_for('users'))

@app.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = current_user()
    if user['role'] != 'Admin' and user['id'] != user_id:
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users'))
    
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Asset WHERE owner_id = ?', (int(user_id),))
    cursor.execute('DELETE FROM User WHERE id = ?', (int(user_id),))
    connection.commit()
    flash(f"User deleted", "info")
    return redirect(url_for('users'))

@app.route('/user/promote/<int:user_id>', methods=['POST'])
def promote_user(user_id):
    user = current_user()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users'))
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('UPDATE User SET role = "Admin" WHERE id = ?', (user_id,))
    connection.commit()
    flash(f"User promoted to Admin", "success")
    return redirect(url_for('users'))

@app.route('/user/create', methods=['POST'])
def create_user():
    user = current_user()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users'))
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    password_hash = generate_password_hash(password)

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO User (username,password_hash,role) VALUES (?,?,?)', (username, password_hash, role))
    connection.commit()
    flash(f"User {username} created", "success")
    return redirect(url_for('users'))
# add flash alerts for success/edit success on every route. 
@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()

    if(user['role'] == 'Admin'):
        cursor.execute('''
            SELECT a.*, u.username AS owner_username, d.name AS department_name
            FROM Asset a
            LEFT JOIN User u ON a.owner_id = u.id
            LEFT JOIN Department d ON a.department_id = d.id
            WHERE a.approved = 0
        ''')
    else:
        cursor.execute('''
            SELECT a.*, u.username AS owner_username, d.name AS department_name
            FROM Asset a
            LEFT JOIN User u ON a.owner_id = u.id
            LEFT JOIN Department d ON a.department_id = d.id
            WHERE a.owner_id = ? AND a.approved = 0
        ''', (user['id'],))
    assets = [dict(row) for row in cursor.fetchall()]
    return render_template('dashboard.html', user=user, assets=assets)


if __name__ == '__main__':
   app.run(debug = True)