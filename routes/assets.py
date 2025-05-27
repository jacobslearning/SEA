from flask import Blueprint, render_template, request, flash, url_for, redirect
from datetime import datetime
from routes.utils import login_required, current_user, get_db

assets_blueprint = Blueprint('assets', __name__)

@assets_blueprint.route('/assets')
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

@assets_blueprint.route('/asset/create', methods=['POST'])
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
        int(data.get('in_use', 1)),int(data.get('approved', 0)), data['assigned_user_id'], data['department_id']
    ))
    connection.commit()
    flash("Asset created and awaiting approval", "success")
    return redirect(url_for('assets.assets'))

@assets_blueprint.route('/asset/edit/<int:asset_id>', methods=['POST'])
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
        return redirect(url_for('assets.assets'))

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
    return redirect(url_for('assets.assets'))

@assets_blueprint.route('/asset/delete/<int:asset_id>', methods=['POST'])
@login_required
def delete_asset(asset_id):
    user = current_user()
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Asset WHERE id = ?", (asset_id,))
    asset = cursor.fetchone()

    if asset is None or (user['role'] != 'Admin' and asset['owner_id'] != user['id']):
        flash("Unauthorised Access", "danger")
        return redirect(url_for('assets.assets'))

    cursor.execute("DELETE FROM Asset WHERE id = ?", (asset_id,))
    connection.commit()
    flash("Asset deleted", "info")
    return redirect(url_for('assets.assets'))

@assets_blueprint.route('/asset/approve/<int:asset_id>', methods=['POST'])
@login_required
def approve_asset(asset_id):
    user = current_user()
    if user['role'] != 'Admin':
        flash("Unauthorised Access", "danger")
        return redirect(url_for('assets.assets'))

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE Asset SET approved = 1 WHERE id = ?", (asset_id,))
    connection.commit()
    flash("Asset approved", "success")
    return redirect(url_for('assets.assets'))