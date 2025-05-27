from flask import Blueprint, render_template, request, flash, url_for, redirect, session
from routes.utils import login_required, query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard.dashboard'))
            
    return render_template('login.html')

@auth_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))