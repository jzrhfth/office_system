from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# Database Configuration for MAMP
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'office_supplies_db',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@app.route('/inventory')
@login_required
def inventory():
    return render_template('admin/inventory.html')

@app.route('/requests')
@login_required
def requests():
    return render_template('admin/requests.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['admin_logged_in'] = True
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('admin/login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('admin/profile.html')

@app.route('/change_password')
@login_required
def change_password():
    return render_template('admin/change_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)