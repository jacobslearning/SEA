from flask import Flask,g, render_template, request, redirect, session
import sqlite3 as sql

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

if __name__ == '__main__':
   app.run(debug = True)