from flask import Flask, render_template, Markup, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit
from flask_login import current_user, logout_user
from dotenv import load_dotenv
import MySQLdb.cursors
import re
import os

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY_ENV')
app.config['MYSQL_HOST'] = os.getenv('HOST')
app.config['MYSQL_USER'] = os.getenv('USER')
app.config['MYSQL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')

socketio = SocketIO(app)

mysql = MySQL(app)
isClient = 1
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        msg='Have an account?'
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
            user = cursor.fetchone()
            if user:
                session['loggedin'] = True
                session['id'] = user['id']
                session['username'] = user['username']
                msg = 'Logged in successfully !'
                print(msg)
                print(session['username'])
                if session['username'] == "client":
                    isClient = 1
                else:
                    isClient = 0
                print("isClient = " + str(isClient))
                return render_template('home.html', isClient = isClient)
            else:
                msg = 'Incorrect username / password !'
                print(msg)
        return render_template('login.html', msg = msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        if session['username'] != "client":
            global isClient
            isClient = 0
        return render_template('home.html', isClient = isClient)
    else:
        return redirect(url_for('login'))

@app.route('/dashboardlist/<projectname>')
def dashboardlist(projectname):
    return render_template('')
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@socketio.on('disconnect')
def disconnect_user():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)

@app.route('/dashboard_1')
def dashboard_1_page():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM dashboards WHERE id = 1')
        dashboard = cursor.fetchone()
        title = dashboard['name']
        embed_code = dashboard['embed_code']
        embed_code = Markup(embed_code)
        return render_template('dashboard_1.html', variable = embed_code, title = title)
    return redirect(url_for('login'))

@app.route('/dashboard_2')
def dashboard_2_page():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM dashboards WHERE id = 2')
        dashboard = cursor.fetchone()
        title = dashboard['name']
        embed_code = dashboard['embed_code']
        embed_code = Markup(embed_code)
        return render_template('dashboard_2.html', variable = embed_code, title = title)
    return redirect(url_for('login'))







