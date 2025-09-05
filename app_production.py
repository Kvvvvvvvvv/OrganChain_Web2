from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import psycopg2
import os
import uuid
import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    DATABASE_URL = os.environ.get('DATABASE_URL')
else:
    app.config['SECRET_KEY'] = 'dev-secret-key'
    DATABASE_URL = 'sqlite:///database.db'

def get_db_connection():
    """Get database connection based on environment"""
    if os.environ.get('FLASK_ENV') == 'production' and DATABASE_URL:
        # PostgreSQL for production
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return conn
    else:
        # SQLite for development
        return sqlite3.connect('database.db')

def init_db():
    """Initialize database with proper schema"""
    conn = get_db_connection()
    c = conn.cursor()
    
    if os.environ.get('FLASK_ENV') == 'production':
        # PostgreSQL syntax
        c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS hospital (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            location TEXT,
            password TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS donor (
            id SERIAL PRIMARY KEY,
            unique_id TEXT UNIQUE,
            hospital_id INTEGER,
            name TEXT,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            organ TEXT,
            status TEXT DEFAULT 'Not Matched',
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospital(id)
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS patient (
            id SERIAL PRIMARY KEY,
            unique_id TEXT UNIQUE,
            hospital_id INTEGER,
            name TEXT,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            organ TEXT,
            status TEXT DEFAULT 'Waiting',
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospital(id)
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS match_record (
            id SERIAL PRIMARY KEY,
            donor_id INTEGER,
            patient_id INTEGER,
            donor_unique_id TEXT,
            patient_unique_id TEXT,
            match_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (donor_id) REFERENCES donor(id),
            FOREIGN KEY (patient_id) REFERENCES patient(id)
        )
        ''')
    else:
        # SQLite syntax
        c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS hospital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            location TEXT,
            password TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS donor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_id TEXT UNIQUE,
            hospital_id INTEGER,
            name TEXT,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            organ TEXT,
            status TEXT DEFAULT 'Not Matched',
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospital(id)
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS patient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_id TEXT UNIQUE,
            hospital_id INTEGER,
            name TEXT,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            organ TEXT,
            status TEXT DEFAULT 'Waiting',
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES patient(id)
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS match_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER,
            patient_id INTEGER,
            donor_unique_id TEXT,
            patient_unique_id TEXT,
            match_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (donor_id) REFERENCES donor(id),
            FOREIGN KEY (patient_id) REFERENCES patient(id)
        )
        ''')
    
    # Check if columns exist and add them if they don't (for existing databases)
    try:
        if os.environ.get('FLASK_ENV') == 'production':
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='donor' AND column_name='unique_id'")
            if not c.fetchone():
                c.execute("ALTER TABLE donor ADD COLUMN unique_id TEXT")
            
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='donor' AND column_name='registration_date'")
            if not c.fetchone():
                c.execute("ALTER TABLE donor ADD COLUMN registration_date TEXT")
            
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='patient' AND column_name='unique_id'")
            if not c.fetchone():
                c.execute("ALTER TABLE patient ADD COLUMN unique_id TEXT")
            
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='patient' AND column_name='registration_date'")
            if not c.fetchone():
                c.execute("ALTER TABLE patient ADD COLUMN registration_date TEXT")
        else:
            c.execute("PRAGMA table_info(donor)")
            donor_columns = [column[1] for column in c.fetchall()]
            c.execute("PRAGMA table_info(patient)")
            patient_columns = [column[1] for column in c.fetchall()]

            if 'unique_id' not in donor_columns:
                c.execute("ALTER TABLE donor ADD COLUMN unique_id TEXT")
            if 'unique_id' not in patient_columns:
                c.execute("ALTER TABLE patient ADD COLUMN unique_id TEXT")
            if 'registration_date' not in donor_columns:
                c.execute("ALTER TABLE donor ADD COLUMN registration_date TEXT")
            if 'registration_date' not in patient_columns:
                c.execute("ALTER TABLE patient ADD COLUMN registration_date TEXT")
    except Exception as e:
        print(f"Migration error (non-critical): {e}")

    # Update existing records with unique IDs and registration dates if they don't have them
    try:
        c.execute("UPDATE donor SET unique_id = ? WHERE unique_id IS NULL", (str(uuid.uuid4()),))
        c.execute("UPDATE patient SET unique_id = ? WHERE unique_id IS NULL", (str(uuid.uuid4()),))
        current_time = datetime.datetime.now().isoformat()
        c.execute("UPDATE donor SET registration_date = ? WHERE registration_date IS NULL", (current_time,))
        c.execute("UPDATE patient SET registration_date = ? WHERE registration_date IS NULL", (current_time,))
    except Exception as e:
        print(f"Update error (non-critical): {e}")

    # Insert default admin if not exists
    try:
        c.execute("SELECT COUNT(*) FROM admin")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO admin (email, password) VALUES (?, ?)", ("admin@example.com", "admin123"))
    except Exception as e:
        print(f"Admin creation error (non-critical): {e}")

    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = get_db_connection()
        c = conn.cursor()
        
        if user_type == 'admin':
            c.execute("SELECT * FROM admin WHERE email = ? AND password = ?", (email, password))
            user = c.fetchone()
            if user:
                session['user_type'] = 'admin'
                session['user_id'] = user[0]
                session['user_email'] = user[1]
                conn.close()
                return redirect('/manage_hospitals')
        else:
            c.execute("SELECT * FROM hospital WHERE email = ? AND password = ?", (email, password))
            user = c.fetchone()
            if user:
                session['user_type'] = 'hospital'
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[2]
                session['user_location'] = user[3]
                conn.close()
                return redirect('/hospital_dashboard')
        
        conn.close()
        return "Invalid credentials"
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_hospital', methods=['GET', 'POST'])
def add_hospital():
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        location = request.form['location']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO hospital (name, email, location, password) VALUES (?, ?, ?, ?)", 
                     (name, email, location, password))
            conn.commit()
            conn.close()
            return "Hospital added successfully!"
        except Exception as e:
            conn.close()
            return f"Error: {str(e)}"
    
    return render_template('add_hospital.html')

@app.route('/manage_hospitals')
def manage_hospitals():
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM hospital")
    hospitals = c.fetchall()
    conn.close()
    
    return render_template('manage_hospitals.html', hospitals=hospitals)

@app.route('/delete_hospital/<int:hospital_id>')
def delete_hospital(hospital_id):
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM hospital WHERE id = ?", (hospital_id,))
    conn.commit()
    conn.close()
    
    return redirect('/manage_hospitals')

@app.route('/hospital_dashboard')
def hospital_dashboard():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get hospital info
    hospital_name = session.get('user_name')
    hospital_email = session.get('user_email')
    hospital_location = session.get('user_location')
    
    # Get donors with fallback for missing columns
    try:
        c.execute("""
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date 
            FROM donor 
            WHERE hospital_id = ? 
            ORDER BY registration_date ASC
        """, (session.get('user_id'),))
        donors = c.fetchall()
    except Exception:
        c.execute("""
            SELECT id, 'N/A' as unique_id, name, age, gender, blood_type, organ, status, 'N/A' as registration_date 
            FROM donor 
            WHERE hospital_id = ? 
            ORDER BY id ASC
        """, (session.get('user_id'),))
        donors = c.fetchall()
    
    # Get patients with fallback for missing columns
    try:
        c.execute("""
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date 
            FROM patient 
            WHERE hospital_id = ? 
            ORDER BY registration_date ASC
        """, (session.get('user_id'),))
        patients = c.fetchall()
    except Exception:
        c.execute("""
            SELECT id, 'N/A' as unique_id, name, age, gender, blood_type, organ, status, 'N/A' as registration_date 
            FROM patient 
            WHERE hospital_id = ? 
            ORDER BY id ASC
        """, (session.get('user_id'),))
        patients = c.fetchall()
    
    conn.close()
    
    return render_template('hospital_login.html', 
                         hospital_name=hospital_name,
                         hospital_email=hospital_email,
                         hospital_location=hospital_location,
                         donors=donors,
                         patients=patients)

@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_type = request.form['blood_type']
        organ = request.form['organ']
        
        # Generate unique ID and registration date
        unique_id = str(uuid.uuid4())
        registration_date = datetime.datetime.now().isoformat()
        
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT INTO donor (unique_id, hospital_id, name, age, gender, blood_type, organ, registration_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (unique_id, session.get('user_id'), name, age, gender, blood_type, organ, registration_date))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Donor added successfully!', 'unique_id': unique_id})
        except Exception as e:
            # Fallback for older database schema
            try:
                c.execute("""
                    INSERT INTO donor (hospital_id, name, age, gender, blood_type, organ) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session.get('user_id'), name, age, gender, blood_type, organ))
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'message': 'Donor added successfully!', 'unique_id': 'N/A'})
            except Exception as e2:
                conn.close()
                return jsonify({'success': False, 'message': f'Error: {str(e2)}'})
    
    return render_template('add_donor.html')

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_type = request.form['blood_type']
        organ = request.form['organ']
        
        # Generate unique ID and registration date
        unique_id = str(uuid.uuid4())
        registration_date = datetime.datetime.now().isoformat()
        
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT INTO patient (unique_id, hospital_id, name, age, gender, blood_type, organ, registration_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (unique_id, session.get('user_id'), name, age, gender, blood_type, organ, registration_date))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Patient added successfully!', 'unique_id': unique_id})
        except Exception as e:
            # Fallback for older database schema
            try:
                c.execute("""
                    INSERT INTO patient (hospital_id, name, age, gender, blood_type, organ) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session.get('user_id'), name, age, gender, blood_type, organ))
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'message': 'Patient added successfully!', 'unique_id': 'N/A'})
            except Exception as e2:
                conn.close()
                return jsonify({'success': False, 'message': f'Error: {str(e2)}'})
    
    return render_template('add_patient.html')

@app.route('/matches')
def matches():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Find matches with fallback for missing columns
    try:
        c.execute("""
            SELECT d.id, d.unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, d.registration_date,
                   p.id, p.unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, p.registration_date,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM donor d
            JOIN patient p ON d.blood_type = p.blood_type AND d.organ = p.organ
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            WHERE d.status = 'Not Matched' AND p.status = 'Waiting'
            ORDER BY d.registration_date ASC, p.registration_date ASC
        """)
        results = c.fetchall()
    except Exception:
        c.execute("""
            SELECT d.id, 'N/A' as unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, 'N/A' as registration_date,
                   p.id, 'N/A' as unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, 'N/A' as registration_date,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM donor d
            JOIN patient p ON d.blood_type = p.blood_type AND d.organ = p.organ
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            WHERE d.status = 'Not Matched' AND p.status = 'Waiting'
            ORDER BY d.id ASC, p.id ASC
        """)
        results = c.fetchall()
    
    # Process results
    display_results = []
    for row in results:
        display_results.append({
            'donor_id': row[0],
            'donor_unique_id': row[1][:8] + '...' if row[1] != 'N/A' else 'N/A',
            'donor_name': row[2],
            'donor_age': row[3],
            'donor_gender': row[4],
            'donor_blood_type': row[5],
            'donor_organ': row[6],
            'donor_status': row[7],
            'donor_registered': row[8][:10] if row[8] != 'N/A' else 'N/A',
            'patient_id': row[9],
            'patient_unique_id': row[10][:8] + '...' if row[10] != 'N/A' else 'N/A',
            'patient_name': row[11],
            'patient_age': row[12],
            'patient_gender': row[13],
            'patient_blood_type': row[14],
            'patient_organ': row[15],
            'patient_status': row[16],
            'patient_registered': row[17][:10] if row[17] != 'N/A' else 'N/A',
            'donor_hospital': row[18],
            'patient_hospital': row[19]
        })
    
    conn.close()
    return render_template('matches.html', results=display_results)

@app.route('/match_records')
def match_records():
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get match records with fallback for missing columns
    try:
        c.execute("""
            SELECT mr.id, mr.donor_id, mr.patient_id, mr.donor_unique_id, mr.patient_unique_id, mr.match_date, mr.status,
                   d.name as donor_name, p.name as patient_name,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            ORDER BY mr.match_date DESC
        """)
        matches = c.fetchall()
    except Exception:
        c.execute("""
            SELECT mr.id, mr.donor_id, mr.patient_id, 'N/A' as donor_unique_id, 'N/A' as patient_unique_id, mr.match_date, mr.status,
                   d.name as donor_name, p.name as patient_name,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            ORDER BY mr.match_date DESC
        """)
        matches = c.fetchall()
    
    # Process matches
    match_list = []
    for match in matches:
        match_list.append({
            'id': match[0],
            'donor_id': match[1],
            'patient_id': match[2],
            'donor_unique_id': match[3][:8] + '...' if match[3] != 'N/A' else 'N/A',
            'patient_unique_id': match[4][:8] + '...' if match[4] != 'N/A' else 'N/A',
            'match_date': match[5],
            'status': match[6],
            'donor_name': match[7],
            'patient_name': match[8],
            'donor_hospital': match[9],
            'patient_hospital': match[10]
        })
    
    conn.close()
    return render_template('match_records.html', matches=match_list)

# Additional routes for hospital-specific and admin views
@app.route('/hospital_matches')
def hospital_matches():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get matches where current hospital is involved
    try:
        c.execute("""
            SELECT d.id, d.unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, d.registration_date,
                   p.id, p.unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, p.registration_date,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM donor d
            JOIN patient p ON d.blood_type = p.blood_type AND d.organ = p.organ
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            WHERE (d.hospital_id = ? OR p.hospital_id = ?) 
            AND d.status = 'Not Matched' AND p.status = 'Waiting'
            ORDER BY d.registration_date ASC, p.registration_date ASC
        """, (session.get('user_id'), session.get('user_id')))
        results = c.fetchall()
    except Exception:
        c.execute("""
            SELECT d.id, 'N/A' as unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, 'N/A' as registration_date,
                   p.id, 'N/A' as unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, 'N/A' as registration_date,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM donor d
            JOIN patient p ON d.blood_type = p.blood_type AND d.organ = p.organ
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            WHERE (d.hospital_id = ? OR p.hospital_id = ?) 
            AND d.status = 'Not Matched' AND p.status = 'Waiting'
            ORDER BY d.id ASC, p.id ASC
        """, (session.get('user_id'), session.get('user_id')))
        results = c.fetchall()
    
    # Process results
    display_results = []
    for row in results:
        display_results.append({
            'donor_id': row[0],
            'donor_unique_id': row[1][:8] + '...' if row[1] != 'N/A' else 'N/A',
            'donor_name': row[2],
            'donor_age': row[3],
            'donor_gender': row[4],
            'donor_blood_type': row[5],
            'donor_organ': row[6],
            'donor_status': row[7],
            'donor_registered': row[8][:10] if row[8] != 'N/A' else 'N/A',
            'patient_id': row[9],
            'patient_unique_id': row[10][:8] + '...' if row[10] != 'N/A' else 'N/A',
            'patient_name': row[11],
            'patient_age': row[12],
            'patient_gender': row[13],
            'patient_blood_type': row[14],
            'patient_organ': row[15],
            'patient_status': row[16],
            'patient_registered': row[17][:10] if row[17] != 'N/A' else 'N/A',
            'donor_hospital': row[18],
            'patient_hospital': row[19]
        })
    
    conn.close()
    return render_template('hospital_matches.html', results=display_results)

@app.route('/admin_donors')
def admin_donors():
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all donors with fallback for missing columns
    try:
        c.execute("""
            SELECT d.id, d.unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, d.registration_date,
                   h.name as hospital_name
            FROM donor d
            JOIN hospital h ON d.hospital_id = h.id
            ORDER BY d.registration_date ASC
        """)
        donors = c.fetchall()
    except Exception:
        c.execute("""
            SELECT d.id, 'N/A' as unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, 'N/A' as registration_date,
                   h.name as hospital_name
            FROM donor d
            JOIN hospital h ON d.hospital_id = h.id
            ORDER BY d.id ASC
        """)
        donors = c.fetchall()
    
    conn.close()
    return render_template('admin_donors.html', donors=donors)

@app.route('/admin_patients')
def admin_patients():
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all patients with fallback for missing columns
    try:
        c.execute("""
            SELECT p.id, p.unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, p.registration_date,
                   h.name as hospital_name
            FROM patient p
            JOIN hospital h ON p.hospital_id = h.id
            ORDER BY p.registration_date ASC
        """)
        patients = c.fetchall()
    except Exception:
        c.execute("""
            SELECT p.id, 'N/A' as unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, 'N/A' as registration_date,
                   h.name as hospital_name
            FROM patient p
            JOIN hospital h ON p.hospital_id = h.id
            ORDER BY p.id ASC
        """)
        patients = c.fetchall()
    
    conn.close()
    return render_template('admin_patients.html', patients=patients)

@app.route('/admin_matches')
def admin_matches():
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all matches with fallback for missing columns
    try:
        c.execute("""
            SELECT d.id, d.unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, d.registration_date,
                   p.id, p.unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, p.registration_date,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM donor d
            JOIN patient p ON d.blood_type = p.blood_type AND d.organ = p.organ
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            WHERE d.status = 'Not Matched' AND p.status = 'Waiting'
            ORDER BY d.registration_date ASC, p.registration_date ASC
        """)
        results = c.fetchall()
    except Exception:
        c.execute("""
            SELECT d.id, 'N/A' as unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, 'N/A' as registration_date,
                   p.id, 'N/A' as unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, 'N/A' as registration_date,
                   h1.name as donor_hospital, h2.name as patient_hospital
            FROM donor d
            JOIN patient p ON d.blood_type = p.blood_type AND d.organ = p.organ
            JOIN hospital h1 ON d.hospital_id = h1.id
            JOIN hospital h2 ON p.hospital_id = h2.id
            WHERE d.status = 'Not Matched' AND p.status = 'Waiting'
            ORDER BY d.id ASC, p.id ASC
        """)
        results = c.fetchall()
    
    # Process results
    display_results = []
    for row in results:
        display_results.append({
            'donor_id': row[0],
            'donor_unique_id': row[1][:8] + '...' if row[1] != 'N/A' else 'N/A',
            'donor_name': row[2],
            'donor_age': row[3],
            'donor_gender': row[4],
            'donor_blood_type': row[5],
            'donor_organ': row[6],
            'donor_status': row[7],
            'donor_registered': row[8][:10] if row[8] != 'N/A' else 'N/A',
            'patient_id': row[9],
            'patient_unique_id': row[10][:8] + '...' if row[10] != 'N/A' else 'N/A',
            'patient_name': row[11],
            'patient_age': row[12],
            'patient_gender': row[13],
            'patient_blood_type': row[14],
            'patient_organ': row[15],
            'patient_status': row[16],
            'patient_registered': row[17][:10] if row[17] != 'N/A' else 'N/A',
            'donor_hospital': row[18],
            'patient_hospital': row[19]
        })
    
    conn.close()
    return render_template('admin_matches.html', results=display_results)

@app.route('/hospital_donors')
def hospital_donors():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get hospital's donors with fallback for missing columns
    try:
        c.execute("""
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date 
            FROM donor 
            WHERE hospital_id = ? 
            ORDER BY registration_date ASC
        """, (session.get('user_id'),))
        donors = c.fetchall()
    except Exception:
        c.execute("""
            SELECT id, 'N/A' as unique_id, name, age, gender, blood_type, organ, status, 'N/A' as registration_date 
            FROM donor 
            WHERE hospital_id = ? 
            ORDER BY id ASC
        """, (session.get('user_id'),))
        donors = c.fetchall()
    
    conn.close()
    return render_template('admin_donors.html', donors=donors)

@app.route('/hospital_patients')
def hospital_patients():
    if session.get('user_type') != 'hospital':
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get hospital's patients with fallback for missing columns
    try:
        c.execute("""
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date 
            FROM patient 
            WHERE hospital_id = ? 
            ORDER BY registration_date ASC
        """, (session.get('user_id'),))
        patients = c.fetchall()
    except Exception:
        c.execute("""
            SELECT id, 'N/A' as unique_id, name, age, gender, blood_type, organ, status, 'N/A' as registration_date 
            FROM patient 
            WHERE hospital_id = ? 
            ORDER BY id ASC
        """, (session.get('user_id'),))
        patients = c.fetchall()
    
    conn.close()
    return render_template('admin_patients.html', patients=patients)

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    # Run on all interfaces for production
    app.run(host='0.0.0.0', port=port, debug=False)
