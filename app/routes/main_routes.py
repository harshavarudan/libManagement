import sqlite3

from flask import Blueprint, render_template, request, url_for, redirect

from app.services import handle_user_registration

from app.services.users import login
from app.services.users import admin_login

main_bp = Blueprint('main', __name__)


@main_bp.route('/home', methods=['GET'])
@main_bp.route('/', methods=['GET'])
@main_bp.route('/login', methods=['GET'])
def index():
    return render_template('index.html')


@main_bp.route('/userRegistration', methods=['GET'])
def user_registration():
    return render_template('user_registration.html')


@main_bp.route('/userRegistration', methods=['POST'])
def register_new_user():
    print("registering new user")
    user_added = handle_user_registration(request.form['name'], request.form['password'])
    if user_added:
        return render_template('user_registration_status.html', success='User added successfully')
    else:
        return render_template('user_registration_status.html', error='User already exists')


@main_bp.route('/adminHi', methods=['GET'])
def admin_hi():
    con = sqlite3.connect("/Users/harshavardhan/library.db")
    cur = con.cursor()
    cur.execute("SELECT name FROM users")
    rows = cur.fetchall()
    con.close()
    print(rows)

    return render_template('admin_hi.html', name=rows[0])




@main_bp.route('/login', methods=['POST'])
def user_login():
    name = request.form['username']
    password = request.form['password']
    print("name: ", name)
    print("password: ", password)
    if name is None or password is None:
        return render_template('index.html', error='Login failed')
    successful,users_id = login(name, password)
    if successful:
        dashboard = "/users/" + str(users_id) + "/userDashboard"
        return redirect(dashboard)

    else:
        return render_template('index.html', error='Login failed')

@main_bp.route('/librarianLogin', methods=['GET'])
def librarian_login_page():
    return render_template('admin_login.html')

@main_bp.route('/librarianLogin', methods=['POST'])
def librarian_login():
    name = request.form['username']
    password = request.form['password']
    print("name: ", name)
    print("password: ", password)
    if name is None or password is None or name == '' or password == '':
        return render_template('admin_login.html', error='Please enter both username and password')
    successful,users_id = admin_login(name, password)
    if successful:
        dashboard = "/admins/" + str(users_id) + "/adminDashboard"
        return redirect(dashboard)

    else:
        return render_template('admin_login.html', error='Login failed')
