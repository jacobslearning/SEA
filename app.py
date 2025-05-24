from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'test'
app.config['DATABASE'] = 'database.db'

# database helper functions

def get_db():
    if 'db' not in g:
        g.db = sql.connect(app.config['DATABASE'])
        g.db.row_factory = sql.Row  # So you can access columns by name
    return g.db

if __name__ == '__main__':
   app.run(debug = True)