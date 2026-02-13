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

    # --- Chart Data Calculation ---
    
    # 1. Weekly Data (Current Week, Mon-Sun)
    weekly_counts = [0] * 7
    cursor.execute("""
        SELECT DAYOFWEEK(request_date) as day_num, COUNT(*) as count 
        FROM requests 
        WHERE YEARWEEK(request_date, 1) = YEARWEEK(CURDATE(), 1) 
        GROUP BY day_num
    """)
    for row in cursor.fetchall():
        # DAYOFWEEK: 1=Sun, 2=Mon ... 7=Sat. Convert to 0=Mon ... 6=Sun
        if row['day_num']:
            idx = (row['day_num'] + 5) % 7
            weekly_counts[idx] = row['count']

    # 2. Monthly Data (Current Year, Jan-Dec)
    monthly_counts = [0] * 12
    cursor.execute("""
        SELECT MONTH(request_date) as month_num, COUNT(*) as count 
        FROM requests 
        WHERE YEAR(request_date) = YEAR(CURDATE()) 
        GROUP BY month_num
    """)
    for row in cursor.fetchall():
        # MONTH: 1=Jan ... 12=Dec. Index: 0..11
        if row['month_num']:
            idx = row['month_num'] - 1
            if 0 <= idx < 12:
                monthly_counts[idx] = row['count']

    # 3. Yearly Data (Last 5 Years)
    current_year = datetime.now().year
    start_year = current_year - 4
    years_labels = list(range(start_year, current_year + 1))
    yearly_counts_map = {}
    cursor.execute("SELECT YEAR(request_date) as year_num, COUNT(*) as count FROM requests WHERE YEAR(request_date) >= %s GROUP BY year_num", (start_year,))
    for row in cursor.fetchall():
        yearly_counts_map[row['year_num']] = row['count']
    yearly_counts = [yearly_counts_map.get(year, 0) for year in years_labels]
    
    cursor.close()
    conn.close()
    return render_template('admin/dashboard.html', total_requests=total_requests, pending_requests=pending_requests, approved_requests=approved_requests, recent_requests=recent_requests, low_stock_items=low_stock_items, weekly_data=weekly_counts, monthly_data=monthly_counts, yearly_data=yearly_counts, years_labels=years_labels)

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
        category = request.form['category']
        stock_quantity = request.form['stock_quantity']
        unit = request.form['unit']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (item_name, category, stock_quantity, unit) VALUES (%s, %s, %s, %s)", (item_name, category, stock_quantity, unit))
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
        category = request.form['category']
        stock_quantity = request.form['stock_quantity']
        unit = request.form['unit']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET item_name=%s, category=%s, stock_quantity=%s, unit=%s WHERE id=%s", (item_name, category, stock_quantity, unit, id))
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

@app.route('/requests/approve/<int:id>', methods=['POST'])
@login_required
def approve_request(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deduct inventory based on request items
    cursor.execute("SELECT item_description, quantity FROM request_items WHERE request_id = %s", (id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute("UPDATE inventory SET stock_quantity = stock_quantity - %s WHERE item_name = %s", (item[1], item[0]))

    cursor.execute("UPDATE requests SET status='Approved' WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Request approved successfully', 'success')
    return redirect(url_for('requests'))

@app.route('/requests/decline/<int:id>', methods=['POST'])
@login_required
def decline_request(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    approver_name = session.get('username', 'Admin')
    cursor.execute("UPDATE requests SET status='Declined', approver_name=%s WHERE id=%s", (approver_name, id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Request declined successfully', 'success')
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

@app.route('/get_request_items/<int:id>')
@login_required
def get_request_items(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT item_description, quantity, unit, purpose FROM request_items WHERE request_id = %s", (id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(items)

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
            session['first_name'] = user.get('first_name') or user.get('firstname')
            session['last_name'] = user.get('last_name') or user.get('lastname')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('admin/login.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = session.get('username')
        
        cursor.execute("UPDATE admin SET first_name=%s, last_name=%s, email=%s WHERE username=%s", 
                       (first_name, last_name, email, username))
        conn.commit()
        session['first_name'] = first_name
        session['last_name'] = last_name
        session.modified = True
        flash('Profile updated successfully', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('profile'))

    username = session.get('username')
    cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
    admin = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not admin:
        session.clear()
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))

    return render_template('admin/profile.html', admin=admin)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        username = session['username']
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return redirect(url_for('change_password'))
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Verify current password (assuming plain text as per login logic)
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, current_password))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("UPDATE admin SET password = %s WHERE username = %s", (new_password, username))
            conn.commit()
            flash('Password changed successfully!', 'success')
        else:
            flash('Incorrect current password.', 'error')
            
        cursor.close()
        conn.close()
        return redirect(url_for('change_password'))
        
    return render_template('admin/change_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def time_ago(date):
    """
    Calculates the time difference between a given datetime and now,
    and returns a human-readable string.
    """
    if not date:
        return ""
    now = datetime.now()
    if date.tzinfo:
        now = datetime.now(date.tzinfo)

    diff = now - date
    s = diff.total_seconds()

    if s < 60:
        return 'just now'
    elif s < 3600:
        return f'{int(s/60)}m ago'
    elif s < 86400:
        return f'{int(s/3600)}h ago'
    elif s < 2592000: # 30 days
        days = int(s/86400)
        return f'{days}d ago'
    else:
        return date.strftime('%b %d, %Y')

@app.route('/api/pending_count')
@login_required
def pending_count():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM requests WHERE status = 'Pending'")
    count = cursor.fetchone()['count']
    cursor.close()
    conn.close()
    return jsonify({'count': count})

@app.route('/api/notifications')
@login_required
def get_notifications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, mrs_no, department, requester_name, created_at, status FROM requests ORDER BY created_at DESC LIMIT 15")
    requests = cursor.fetchall()
    cursor.close()
    conn.close()

    notifications = []
    for req in requests:
        is_unread = req['status'] == 'Pending'
        text = f"New request from <strong>{req['requester_name']}</strong> ({req['department']}) with MRS No. {req['mrs_no']}."
        if not is_unread:
            text = f"Request {req['mrs_no']} from <strong>{req['requester_name']}</strong> was {req['status'].lower()}."

        notifications.append({'id': req['id'], 'text': text, 'time': time_ago(req['created_at']), 'unread': is_unread, 'url': url_for('requests')})
    return jsonify(notifications)

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

def check_db_schema():
    """Checks and updates the database schema for missing columns."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # List of columns to check and add if missing
        columns_to_check = [
            ('first_name', 'VARCHAR(100)'),
            ('last_name', 'VARCHAR(100)'),
            ('email', 'VARCHAR(100)')
        ]
        
        for col_name, col_type in columns_to_check:
            cursor.execute(f"SHOW COLUMNS FROM admin LIKE '{col_name}'")
            if not cursor.fetchone():
                print(f"Adding missing column '{col_name}' to admin table...")
                cursor.execute(f"ALTER TABLE admin ADD COLUMN {col_name} {col_type}")
        
        # Ensure default admin user has first_name and last_name set
        cursor.execute("""
            UPDATE admin 
            SET first_name = 'System', last_name = 'Admin' 
            WHERE username = 'admin' AND (first_name IS NULL OR last_name IS NULL)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Schema check warning: {e}")

if __name__ == '__main__':
    check_db_schema() # Run schema check on startup
    app.run(debug=True)