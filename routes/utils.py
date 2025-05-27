from flask import session, current_app, g, flash, redirect, url_for
import sqlite3 as sql
from functools import wraps

def get_db():
    if 'db' not in g:
        g.db = sql.connect(current_app.config['DATABASE'])
        g.db.row_factory = sql.Row
    return g.db

def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

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

# login decorater, run this before a function that requires the user to be logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# run this before a function that requires an admin to be logged in
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'Admin':
            flash("Unauthorised Access", "danger")
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function