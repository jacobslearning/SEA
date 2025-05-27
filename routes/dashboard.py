from flask import Blueprint, render_template, url_for, redirect
from routes.utils import login_required, current_user, get_db

dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/')
def index():
    if current_user():
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

@dashboard_blueprint.route('/dashboard')
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

    metrics = {}

    cursor.execute('SELECT COUNT(*) FROM Asset')
    metrics['total_assets'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM Asset WHERE approved = 0')
    metrics['pending_assets'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM User')
    metrics['total_users'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM Department')
    metrics['total_departments'] = cursor.fetchone()[0]

    return render_template('dashboard.html', user=user, assets=assets, metrics=metrics)