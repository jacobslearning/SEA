from flask import Blueprint, render_template, request, flash, url_for, redirect
from routes.utils import login_required, current_user, get_db

departments_blueprint = Blueprint('departments', __name__)

@departments_blueprint.route('/departments')
@login_required
def departments():
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    return render_template('departments.html', user=user, departments=departments)

@departments_blueprint.route('/department/create', methods=['POST'])
@login_required
def create_department():
    user = current_user()
    data = request.form
    connection = get_db()
    cursor = connection.cursor()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('departments.departments'))
    
    cursor.execute('INSERT INTO Department (name) VALUES (?)', (data['name'],))
    connection.commit()
    flash(f"Department {data['name']} created", "success")
    return redirect(url_for('departments.departments'))

@departments_blueprint.route('/department/edit/<int:dept_id>', methods=['POST'])
@login_required
def edit_department(dept_id):
    user = current_user()
    data = request.form
    connection = get_db()
    cursor = connection.cursor()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('departments.departments'))
    
    cursor.execute('UPDATE Department SET name = ? WHERE id = ?', (data['name'], dept_id))
    connection.commit()
    flash(f"Department {data['name']} updated", "success")
    return redirect(url_for('departments.departments'))

@departments_blueprint.route('/department/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('departments.departments'))
    cursor.execute('DELETE FROM Asset WHERE owner_id = ?', (int(user['id']),))
    cursor.execute('DELETE FROM Department WHERE id = ?', (dept_id,))
    connection.commit()
    flash(f"Department deleted", "info")
    return redirect(url_for('departments.departments'))