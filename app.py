from flask import Flask, flash, g, render_template, request, redirect, session, url_for
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

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

#TODO: create register/login/dashboard templates
# login decorater 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
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

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    print("current user ", user)
    # TODO: if admin, show admin stuff, if user show user stuff
    connection = get_db()
    cursor = connection.cursor()

    if(user['role'] == 'Admin'):
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
            WHERE a.owner_id = ? AND (a.approved = 0 OR a.approved = 1)
        ''', (user['id'],))
    assets = [dict(row) for row in cursor.fetchall()]
    return render_template('dashboard.html', user=user, assets=assets)


if __name__ == '__main__':
   app.run(debug = True)