from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import os
from datetime import datetime, timedelta
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'db'),
    'user': os.getenv('MYSQL_USER', 'user'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'testdb')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'teacher':
            flash('Zugriff verweigert. Lehrer-Berechtigung erforderlich.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session['user_type'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash('Datenbankverbindung fehlgeschlagen')
            return render_template('login.html')
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check teacher login
            if username == 'teacher' and password == '@itech':
                session['user_id'] = 'teacher'
                session['user_type'] = 'teacher'
                session['username'] = 'teacher'
                cursor.close()
                conn.close()
                return redirect(url_for('teacher_dashboard'))
            
            # Check student login
            cursor.execute("SELECT * FROM students WHERE username = %s AND password = %s", 
                          (username, hash_password(password)))
            student = cursor.fetchone()
            
            if student:
                session['user_id'] = student['id']
                session['user_type'] = 'student'
                session['username'] = student['username']
                session['student_name'] = f"{student['firstname']} {student['lastname']}"
                cursor.close()
                conn.close()
                return redirect(url_for('student_dashboard'))
            
            cursor.close()
            conn.close()
            flash('Ungültige Anmeldedaten')
        except Exception as e:
            print(f"Login error: {e}")
            flash('Ein Fehler ist aufgetreten')
            if conn:
                conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        class_name = request.form['class_name']
        password = hash_password('test1234')  # Default password
        
        conn = get_db_connection()
        if not conn:
            flash('Datenbankverbindung fehlgeschlagen')
            return render_template('register.html')
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (username, firstname, lastname, email, class_name, password) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, firstname, lastname, email, class_name, password))
            conn.commit()
            flash('Account erfolgreich erstellt! Passwort: test1234')
            return redirect(url_for('device_registration', student_id=cursor.lastrowid))
        except mysql.connector.IntegrityError:
            flash('Benutzername bereits vergeben')
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Ein Fehler ist aufgetreten')
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    return render_template('register.html')

@app.route('/device_registration/<int:student_id>')
def device_registration(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not student:
        flash('Student nicht gefunden')
        return redirect(url_for('register'))
    
    return render_template('device_registration.html', student=student)

@app.route('/api/register_device', methods=['POST'])
def register_device():
    student_id = request.json.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Set registration flag
    cursor.execute("UPDATE students SET device_registration_pending = TRUE WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Bereit für Geräte-Registrierung. Bitte RFID-Tag scannen.'})

@app.route('/api/registration_status/<int:student_id>')
def registration_status(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT rfid_tag FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return jsonify({'registered': student and student['rfid_tag'] is not None})

@app.route('/teacher_dashboard')
@teacher_required
def teacher_dashboard():
    conn = get_db_connection()
    if not conn:
        flash('Datenbankverbindung fehlgeschlagen')
        return redirect(url_for('login'))
        
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get all classes
        cursor.execute("SELECT DISTINCT class_name FROM students ORDER BY class_name")
        classes = cursor.fetchall()
        
        # Get recent scans with student info
        cursor.execute("""
            SELECT s.*, st.firstname, st.lastname, st.class_name, st.email
            FROM rfid_scans s
            LEFT JOIN students st ON s.rfid_tag = st.rfid_tag
            ORDER BY s.timestamp DESC
            LIMIT 50
        """)
        recent_scans = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('teacher_dashboard.html', classes=classes, recent_scans=recent_scans)
    except Exception as e:
        print(f"Teacher dashboard error: {e}")
        flash('Ein Fehler ist aufgetreten')
        if conn:
            conn.close()
        return redirect(url_for('login'))

@app.route('/api/class_data/<class_name>')
@teacher_required
def get_class_data(class_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get students in class
    cursor.execute("SELECT * FROM students WHERE class_name = %s ORDER BY lastname, firstname", (class_name,))
    students = cursor.fetchall()
    
    # Get attendance data for this class
    cursor.execute("""
        SELECT s.*, st.firstname, st.lastname
        FROM rfid_scans s
        JOIN students st ON s.rfid_tag = st.rfid_tag
        WHERE st.class_name = %s
        ORDER BY s.timestamp DESC
        LIMIT 100
    """, (class_name,))
    attendance = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({'students': students, 'attendance': attendance})

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Datenbankverbindung fehlgeschlagen')
        return redirect(url_for('login'))
        
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get student data
        cursor.execute("SELECT * FROM students WHERE id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        if not student:
            flash('Student nicht gefunden')
            return redirect(url_for('login'))
        
        # Get student's scan history
        if student and student['rfid_tag']:
            cursor.execute("""
                SELECT * FROM rfid_scans 
                WHERE rfid_tag = %s 
                ORDER BY timestamp DESC 
                LIMIT 30
            """, (student['rfid_tag'],))
            scans = cursor.fetchall()
        else:
            scans = []
        
        cursor.close()
        conn.close()
        
        return render_template('student_dashboard.html', student=student, scans=scans)
        
    except Exception as e:
        print(f"Student dashboard error: {e}")
        flash('Ein Fehler ist aufgetreten')
        if conn:
            conn.close()
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# API endpoint for RFID scans from Door-Pi
@app.route('/api/rfid_scan', methods=['POST'])
def rfid_scan():
    try:
        data = request.json or {}
        rfid_tag = data.get('rfid_tag')
        timestamp_str = data.get('timestamp', datetime.now().isoformat())
        
        if not rfid_tag:
            return jsonify({'success': False, 'message': 'RFID Tag fehlt'}), 400
        
        # Parse timestamp
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
        except:
            timestamp = datetime.now()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Datenbankverbindung fehlgeschlagen'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Check if a student is waiting for device registration
        cursor.execute("SELECT * FROM students WHERE device_registration_pending = TRUE ORDER BY id DESC LIMIT 1")
        pending_student = cursor.fetchone()
        
        if pending_student:
            # Register device to pending student
            cursor.execute("""
                UPDATE students 
                SET rfid_tag = %s, device_registration_pending = FALSE 
                WHERE id = %s
            """, (rfid_tag, pending_student['id']))
            conn.commit()
            
            # Insert scan record
            cursor.execute("""
                INSERT INTO rfid_scans (rfid_tag, timestamp, scan_count) 
                VALUES (%s, %s, 1)
            """, (rfid_tag, timestamp))
            conn.commit()
            
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Gerät erfolgreich registriert', 'student': pending_student['firstname']})
        
        # Regular scan - check if RFID exists and increment counter
        cursor.execute("SELECT * FROM rfid_scans WHERE rfid_tag = %s ORDER BY timestamp DESC LIMIT 1", (rfid_tag,))
        last_scan = cursor.fetchone()
        
        if last_scan:
            # Insert new record with incremented counter
            cursor.execute("""
                INSERT INTO rfid_scans (rfid_tag, timestamp, scan_count) 
                VALUES (%s, %s, %s)
            """, (rfid_tag, timestamp, last_scan['scan_count'] + 1))
        else:
            # First scan for this RFID
            cursor.execute("""
                INSERT INTO rfid_scans (rfid_tag, timestamp, scan_count) 
                VALUES (%s, %s, 1)
            """, (rfid_tag, timestamp))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scan erfolgreich gespeichert'})
        
    except Exception as e:
        print(f"RFID scan error: {e}")
        return jsonify({'success': False, 'message': 'Ein Fehler ist aufgetreten'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)