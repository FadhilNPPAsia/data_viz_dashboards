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
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username / password !'
                print(msg)
        return render_template('login.html', msg = msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT a.id, a.name, COUNT(b.project_id) as total_dashboard FROM projects a INNER JOIN dashboards b ON a.id = b.project_id GROUP BY b.project_id')
        projects = cursor.fetchall()
        print(projects)
        if session['username'] != "client":
            global isClient
            isClient = 0
        return render_template('home.html', isClient = isClient, projects = projects)
    else:
        return redirect(url_for('login'))

@app.route('/add_dashboard', methods=['GET', 'POST'])
def add_dashboard():
    if request.method == 'POST' and 'project_id' in request.form and 'dashboard_name' in request.form and 'embed_code' in request.form:
        project_id = request.form['project_id']
        project_id = int(project_id)
        dashboard_name = request.form['dashboard_name']
        embed_code = request.form['embed_code']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO dashboards VALUES (NULL, %s, %s, %s)', (dashboard_name, embed_code, project_id))
        mysql.connection.commit()
    return render_template('input_dashboard.html')

@app.route('/home/<project_id>', methods=['GET', 'POST'])
def dashboardlist(project_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT b.id as project_id, a.id, a.name FROM dashboards a INNER JOIN projects b ON a.project_id = b.id WHERE b.id = % s;", (project_id, ))
        dashboards = cursor.fetchall()
        print(dashboards)
        if session['username'] != "client":
            global isClient
            isClient = 0
        return render_template('project.html', isClient = isClient, dashboards = dashboards)
    else:
        return redirect(url_for('login'))

@app.route('/home/<project_id>/<dashboard_id>', methods = ['GET', 'POST'])
def embeddashboard(project_id, dashboard_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT a.id, a.name, a.embed_code FROM dashboards a INNER JOIN projects b ON a.project_id = b.id WHERE b.id = % s AND a.id = % s;", (project_id, dashboard_id, ))
        dashboard_html = cursor.fetchone()
        embed_code = Markup(dashboard_html['embed_code'])
        print(dashboard_html)
        if session['username'] != "client":
            global isClient
            isClient = 0
        return render_template('dashboard.html', isClient = isClient, embed_code = embed_code)
    else:
        return redirect(url_for('login'))
    
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







