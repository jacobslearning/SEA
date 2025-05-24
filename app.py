from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'test'

if __name__ == '__main__':
   app.run(debug = True)