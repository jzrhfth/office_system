from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
from datetime import datetime
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get the last MRS number to generate the next one
    cursor.execute("SELECT mrs_no FROM requests WHERE mrs_no LIKE 'MRS-%' ORDER BY created_at DESC LIMIT 1")
    last_request = cursor.fetchone()
    
    current_year = datetime.now().year
    sequence = 1
    
    if last_request and last_request['mrs_no']:
        parts = last_request['mrs_no'].split('-')
        if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            if int(parts[1]) == current_year:
                sequence = int(parts[2]) + 1
    
    new_mrs_no = f"MRS-{current_year}-{sequence:03d}"
    
    cursor.close()
    conn.close()
    return render_template('index.html', new_mrs_no=new_mrs_no)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch Stats
    cursor.execute("SELECT COUNT(*) as count FROM requests")
    total_requests = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM requests WHERE status = 'Pending'")
    pending_requests = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM requests WHERE status = 'Approved'")
    approved_requests = cursor.fetchone()['count']
    
    # Fetch Low Stock Items (Threshold: 10)
    cursor.execute("SELECT COUNT(*) as count FROM inventory WHERE stock_quantity <= 10")
    low_stock_items = cursor.fetchone()['count']
    
    # Fetch Recent Requests with Status Logic
    cursor.execute("SELECT * FROM requests ORDER BY created_at DESC LIMIT 5")
    recent_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('admin/dashboard.html', total_requests=total_requests, pending_requests=pending_requests, approved_requests=approved_requests, recent_requests=recent_requests, low_stock_items=low_stock_items)

@app.route('/inventory')
@login_required
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all items
    cursor.execute("SELECT * FROM inventory ORDER BY created_at DESC")
    inventory_items = cursor.fetchall()
    
    # Calculate Stats
    total_items = len(inventory_items)
    in_stock = sum(1 for i in inventory_items if (i['stock_quantity'] or 0) > 10)
    low_stock = sum(1 for i in inventory_items if 0 < (i['stock_quantity'] or 0) <= 10)
    out_of_stock = sum(1 for i in inventory_items if (i['stock_quantity'] or 0) == 0)
    
    cursor.close()
    conn.close()
    
    return render_template('admin/inventory.html', 
                           inventory_items=inventory_items,
                           total_items=total_items,
                           in_stock=in_stock,
                           low_stock=low_stock,
                           out_of_stock=out_of_stock)

@app.route('/inventory/add', methods=['POST'])
@login_required
def add_inventory_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        stock_quantity = request.form['stock_quantity']
        unit = request.form['unit']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (item_name, stock_quantity, unit) VALUES (%s, %s, %s)", (item_name, stock_quantity, unit))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Item added successfully', 'success')
        return redirect(url_for('inventory'))

@app.route('/inventory/edit/<int:id>', methods=['POST'])
@login_required
def edit_inventory_item(id):
    if request.method == 'POST':
        item_name = request.form['item_name']
        stock_quantity = request.form['stock_quantity']
        unit = request.form['unit']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET item_name=%s, stock_quantity=%s, unit=%s WHERE id=%s", (item_name, stock_quantity, unit, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Item updated successfully', 'success')
        return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>', methods=['POST'])
@login_required
def delete_inventory_item(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Item deleted successfully', 'success')
    return redirect(url_for('inventory'))

@app.route('/requests')
@login_required
def requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM requests ORDER BY created_at DESC")
    requests_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/requests.html', requests=requests_data)

@app.route('/requests/edit/<int:id>', methods=['POST'])
@login_required
def edit_request(id):
    if request.method == 'POST':
        department = request.form['department']
        requester_name = request.form['requester_name']
        approver_name = request.form['approver_name']
        status = request.form['status']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET department=%s, requester_name=%s, approver_name=%s, status=%s WHERE id=%s", 
                       (department, requester_name, approver_name, status, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Request updated successfully', 'success')
        return redirect(url_for('requests'))

@app.route('/requests/delete/<int:id>', methods=['POST'])
@login_required
def delete_request(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM request_items WHERE request_id=%s", (id,))
    cursor.execute("DELETE FROM requests WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Request deleted successfully', 'success')
    return redirect(url_for('requests'))

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

@app.route('/submit_request', methods=['POST'])
def submit_request():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Helper to handle empty dates
        def clean_date(date_str):
            return date_str if date_str else None

        # Helper to handle integers
        def clean_int(val):
            try:
                return int(val) if val else 0
            except (ValueError, TypeError):
                return 0

        # Insert Request
        cursor.execute("""
            INSERT INTO requests (mrs_no, department, request_date, requester_name, requester_position, requester_date, approver_name, approver_position, approver_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """, (
            data.get('mrsNo'),
            data.get('department'),
            clean_date(data.get('date')),
            data.get('requester', {}).get('name'),
            data.get('requester', {}).get('position'),
            clean_date(data.get('requester', {}).get('date')),
            data.get('approver', {}).get('name'),
            data.get('approver', {}).get('position'),
            clean_date(data.get('approver', {}).get('date'))
        ))
        request_id = cursor.lastrowid
        
        # Insert Items
        items = data.get('items', [])
        for item in items:
            # Skip empty items (rows with no description)
            if not item.get('description') or not item.get('description').strip():
                continue

            cursor.execute("""
                INSERT INTO request_items (request_id, item_description, quantity, unit, purpose)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                request_id,
                item.get('description'),
                clean_int(item.get('quantity')),
                item.get('unit'),
                item.get('purpose')
            ))
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Request submitted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)