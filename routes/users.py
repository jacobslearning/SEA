from flask import Blueprint, render_template, request, flash, url_for, redirect
from werkzeug.security import generate_password_hash
from routes.utils import login_required, current_user, get_db

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/users')
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

@users_blueprint.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    user = current_user()
    data = request.form
    username = data['username']
    password = data['password']
    role = data['role']

    if user['role'] != 'Admin' and user['id'] != user_id:
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users.users'))
    
    if user['role'] != 'Admin':
        role = "User"
    
    if(user['role'] == 'Admin' and user['id'] == user_id and role == 'User'):
        flash("You can not demote yourself to User", "info")
        return redirect(url_for('users.users'))

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
    return redirect(url_for('users.users'))

@users_blueprint.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = current_user()
    if user['role'] != 'Admin' and user['id'] != user_id:
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users.users'))
    
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Asset WHERE owner_id = ?', (int(user_id),))
    cursor.execute('DELETE FROM User WHERE id = ?', (int(user_id),))
    connection.commit()
    flash(f"User deleted", "info")
    if user['id'] == user_id: # User deleted their own account
        return(redirect(url_for('auth.login')))
    return redirect(url_for('users.users'))

@users_blueprint.route('/user/promote/<int:user_id>', methods=['POST'])
@login_required
def promote_user(user_id):
    user = current_user()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users.users'))
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('UPDATE User SET role = "Admin" WHERE id = ?', (user_id,))
    connection.commit()
    flash(f"User promoted to Admin", "success")
    return redirect(url_for('users.users'))

@users_blueprint.route('/user/create', methods=['POST'])
@login_required
def create_user():
    user = current_user()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('users.users'))
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    password_hash = generate_password_hash(password)

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM User WHERE username = ?', (username,))
    users = cursor.fetchall()

    if users:
        flash("A user already exists with this name", "info")
        return redirect(url_for('users.users'))
    
    cursor.execute('INSERT INTO User (username,password_hash,role) VALUES (?,?,?)', (username, password_hash, role))
    connection.commit()
    flash(f"User {username} created", "success")
    return redirect(url_for('users.users'))