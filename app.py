from flask import Flask, redirect
from routes.assets import assets_blueprint
from routes.auth import auth_blueprint
from routes.dashboard import dashboard_blueprint
from routes.departments import departments_blueprint
from routes.users import users_blueprint
from routes.utils import init_app

app = Flask(__name__)
app.secret_key = 'test'
app.config['DATABASE'] = 'database.db'
init_app(app)

# registering all endpoints by their blueprint, held in routes/
app.register_blueprint(assets_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(departments_blueprint)
app.register_blueprint(users_blueprint)

@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

# make it so admins cant demote themselves back to user
if __name__ == '__main__':
   app.run(debug = True, host="0.0.0.0", port=5000)