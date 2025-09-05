from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import uuid
import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Admin table
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')
    
    # Hospital table
    c.execute('''
    CREATE TABLE IF NOT EXISTS hospital (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        location TEXT,
        password TEXT
    )
    ''')
    
    # Donor table with unique_id and registration_date for FCFS
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
    
    # Patient table with unique_id and registration_date for FCFS
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
        status TEXT DEFAULT 'Not Matched',
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hospital_id) REFERENCES hospital(id)
    )
    ''')
    
    # Match table
    c.execute('''
    CREATE TABLE IF NOT EXISTS match_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        patient_id INTEGER,
        donor_hospital_id INTEGER,
        patient_hospital_id INTEGER,
        organ TEXT,
        blood_type TEXT,
        match_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (donor_id) REFERENCES donor(id),
        FOREIGN KEY (patient_id) REFERENCES patient(id)
    )
    ''')
    
    # Check if columns exist and add them if they don't
    c.execute("PRAGMA table_info(donor)")
    donor_columns = [column[1] for column in c.fetchall()]
    
    c.execute("PRAGMA table_info(patient)")
    patient_columns = [column[1] for column in c.fetchall()]
    
    # Add unique_id column if it doesn't exist
    if 'unique_id' not in donor_columns:
        c.execute("ALTER TABLE donor ADD COLUMN unique_id TEXT")
    
    if 'unique_id' not in patient_columns:
        c.execute("ALTER TABLE patient ADD COLUMN unique_id TEXT")
    
    # Add registration_date column if it doesn't exist
    if 'registration_date' not in donor_columns:
        c.execute("ALTER TABLE donor ADD COLUMN registration_date TEXT")
    
    if 'registration_date' not in patient_columns:
        c.execute("ALTER TABLE patient ADD COLUMN registration_date TEXT")
    
    # Update existing records with unique IDs and registration dates if they don't have them
    c.execute("UPDATE donor SET unique_id = ? WHERE unique_id IS NULL", (str(uuid.uuid4()),))
    c.execute("UPDATE patient SET unique_id = ? WHERE unique_id IS NULL", (str(uuid.uuid4()),))
    
    # Set registration_date for existing records (use current timestamp)
    current_time = datetime.datetime.now().isoformat()
    c.execute("UPDATE donor SET registration_date = ? WHERE registration_date IS NULL", (current_time,))
    c.execute("UPDATE patient SET registration_date = ? WHERE registration_date IS NULL", (current_time,))
    
    # Insert default admin if not exists
    c.execute("SELECT * FROM admin WHERE email='admin@gmail.com'")
    if not c.fetchone():
        c.execute("INSERT INTO admin (email, password) VALUES (?, ?)", ('admin@gmail.com','1234'))
    
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    message = None
    hospital_details = None
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        if role == 'admin':
            c.execute("SELECT * FROM admin WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            if user:
                session['admin'] = user[0]
                return redirect('/manage_hospitals')
        elif role == 'hospital':
            c.execute("SELECT * FROM hospital WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            if user:
                session['hospital'] = user[0]
                session['hospital_name'] = user[1]
                session['hospital_email'] = user[2]
                session['hospital_location'] = user[3]
                return redirect('/hospital_dashboard')
            else:
                message = "Invalid credentials"
        conn.close()
    return render_template('admin_login.html', message=message)

# ----------------- ADMIN -----------------

# Admin: View all donors
@app.route('/admin_donors')
def admin_donors():
    if 'admin' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT d.id, d.unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, d.registration_date, h.name as hospital_name
            FROM donor d
            JOIN hospital h ON d.hospital_id = h.id
            ORDER BY d.registration_date ASC
        ''')
        donors = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback for old database structure
        c.execute('''
            SELECT d.id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, h.name as hospital_name
            FROM donor d
            JOIN hospital h ON d.hospital_id = h.id
            ORDER BY d.id ASC
        ''')
        old_donors = c.fetchall()
        donors = [(d[0], 'N/A', d[1], d[2], d[3], d[4], d[5], d[6], 'N/A', d[7]) for d in old_donors]
    
    conn.close()
    return render_template('admin_donors.html', donors=donors)

# Admin: View all patients
@app.route('/admin_patients')
def admin_patients():
    if 'admin' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT p.id, p.unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, p.registration_date, h.name as hospital_name
            FROM patient p
            JOIN hospital h ON p.hospital_id = h.id
            ORDER BY p.registration_date ASC
        ''')
        patients = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback for old database structure
        c.execute('''
            SELECT p.id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, h.name as hospital_name
            FROM patient p
            JOIN hospital h ON p.hospital_id = h.id
            ORDER BY p.id ASC
        ''')
        old_patients = c.fetchall()
        patients = [(p[0], 'N/A', p[1], p[2], p[3], p[4], p[5], p[6], 'N/A', p[7]) for p in old_patients]
    
    conn.close()
    return render_template('admin_patients.html', patients=patients)

# Admin: View all matches
@app.route('/admin_matches')
def admin_matches():
    if 'admin' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT 
                mr.id as match_id,
                mr.match_date,
                d.name as donor_name,
                d.unique_id as donor_unique_id,
                p.name as patient_name,
                p.unique_id as patient_unique_id,
                mr.organ,
                mr.blood_type,
                hd.name as donor_hospital,
                hp.name as patient_hospital
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            ORDER BY mr.match_date DESC
        ''')
        matches = c.fetchall()
        match_list = []
        
        for match in matches:
            match_data = {
                'match_id': match[0],
                'match_date': match[1],
                'donor_name': match[2],
                'donor_unique_id': match[3],
                'patient_name': match[4],
                'patient_unique_id': match[5],
                'organ': match[6],
                'blood_type': match[7],
                'donor_hospital': match[8],
                'patient_hospital': match[9]
            }
            match_list.append(match_data)
            
    except sqlite3.OperationalError:
        # Fallback for old database structure
        c.execute('''
            SELECT 
                mr.id as match_id,
                mr.match_date,
                d.name as donor_name,
                p.name as patient_name,
                mr.organ,
                mr.blood_type,
                hd.name as donor_hospital,
                hp.name as patient_hospital
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            ORDER BY mr.match_date DESC
        ''')
        matches = c.fetchall()
        match_list = []
        
        for match in matches:
            match_data = {
                'match_id': match[0],
                'match_date': match[1],
                'donor_name': match[2],
                'donor_unique_id': 'N/A',
                'patient_name': match[3],
                'patient_unique_id': 'N/A',
                'organ': match[4],
                'blood_type': match[5],
                'donor_hospital': match[6],
                'patient_hospital': match[7]
            }
            match_list.append(match_data)
    
    conn.close()
    return render_template('admin_matches.html', matches=match_list)

# Admin: Add hospital
@app.route('/add_hospital', methods=['GET','POST'])
def add_hospital():
    if 'admin' not in session:
        return redirect('/login')
    message = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        location = request.form['location']
        password = request.form['password']
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("INSERT INTO hospital (name,email,location,password) VALUES (?,?,?,?)",
                      (name,email,location,password))
            conn.commit()
            conn.close()
            message = "Hospital added successfully!"
        except sqlite3.IntegrityError:
            message = "A hospital with this email already exists."
        return render_template('add_hospital.html', message=message)
    return render_template('add_hospital.html', message=message)

# Admin: Manage hospitals (list & delete)
@app.route('/manage_hospitals', methods=['GET'])
def manage_hospitals():
    if 'admin' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, email, location FROM hospital")
    hospitals = c.fetchall()
    conn.close()
    message = request.args.get('message')
    return render_template('manage_hospitals.html', hospitals=hospitals, message=message)

@app.route('/delete_hospital', methods=['POST'])
def delete_hospital():
    if 'admin' not in session:
        return redirect('/login')
    hospital_id = request.form['hospital_id']
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM hospital WHERE id=?", (hospital_id,))
    conn.commit()
    conn.close()
    return redirect('/manage_hospitals?message=Hospital+deleted+successfully!')

# ----------------- HOSPITAL -----------------
@app.route('/hospital_dashboard')
def hospital_dashboard():
    if 'hospital' not in session:
        return redirect('/login')
    hospital_id = session['hospital']
    hospital_name = session.get('hospital_name')
    hospital_email = session.get('hospital_email')
    hospital_location = session.get('hospital_location')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Check if new columns exist, fallback to old query if not
    try:
        c.execute("SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date FROM donor WHERE hospital_id=? ORDER BY registration_date ASC", (hospital_id,))
        donors = c.fetchall()
        c.execute("SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date FROM patient WHERE hospital_id=? ORDER BY registration_date ASC", (hospital_id,))
        patients = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback to old query if new columns don't exist yet
        c.execute("SELECT id, name, age, gender, blood_type, organ, status FROM donor WHERE hospital_id=?", (hospital_id,))
        old_donors = c.fetchall()
        donors = [(d[0], 'N/A', d[1], d[2], d[3], d[4], d[5], d[6], 'N/A') for d in old_donors]
        
        c.execute("SELECT id, name, age, gender, blood_type, organ, status FROM patient WHERE hospital_id=?", (hospital_id,))
        old_patients = c.fetchall()
        patients = [(p[0], 'N/A', p[1], p[2], p[3], p[4], p[5], p[6], 'N/A') for p in old_patients]
    
    conn.close()
    return render_template('hospital_login.html', hospital_name=hospital_name, hospital_email=hospital_email, hospital_location=hospital_location, donors=donors, patients=patients)

@app.route('/add_donor', methods=['GET','POST'])
def add_donor():
    if 'hospital' not in session:
        return redirect('/login')
    hospital_id = session['hospital']
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_type = request.form['blood_type']
        organ = request.form['organ']
        
        # Generate unique ID and current timestamp
        unique_id = str(uuid.uuid4())
        registration_date = datetime.datetime.now().isoformat()
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Try new insert with unique_id and registration_date, fallback to old insert if needed
        try:
            c.execute("INSERT INTO donor (unique_id, hospital_id, name, age, gender, blood_type, organ, registration_date) VALUES (?,?,?,?,?,?,?,?)",
                      (unique_id, hospital_id, name, age, gender, blood_type, organ, registration_date))
        except sqlite3.OperationalError:
            # Fallback to old insert without new columns
            c.execute("INSERT INTO donor (hospital_id, name, age, gender, blood_type, organ) VALUES (?,?,?,?,?,?)",
                      (hospital_id, name, age, gender, blood_type, organ))
            unique_id = 'N/A'
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Donor added successfully!', 'unique_id': unique_id})
    
    return render_template('add_donor.html')

@app.route('/add_patient', methods=['GET','POST'])
def add_patient():
    if 'hospital' not in session:
        return redirect('/login')
    hospital_id = session['hospital']
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_type = request.form['blood_type']
        organ = request.form['organ']
        
        # Generate unique ID and current timestamp
        unique_id = str(uuid.uuid4())
        registration_date = datetime.datetime.now().isoformat()
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Try new insert with unique_id and registration_date, fallback to old insert if needed
        try:
            c.execute("INSERT INTO patient (unique_id, hospital_id, name, age, gender, blood_type, organ, registration_date) VALUES (?,?,?,?,?,?,?,?)",
                      (unique_id, hospital_id, name, age, gender, blood_type, organ, registration_date))
        except sqlite3.OperationalError:
            # Fallback to old insert without new columns
            c.execute("INSERT INTO patient (hospital_id, name, age, gender, blood_type, organ) VALUES (?,?,?,?,?,?)",
                      (hospital_id, name, age, gender, blood_type, organ))
            unique_id = 'N/A'
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Patient added successfully!', 'unique_id': unique_id})
    
    return render_template('add_patient.html')

# ----------------- HOSPITAL VIEWS -----------------
@app.route('/hospital_donors')
def hospital_donors():
    if 'hospital' not in session:
        return redirect('/login')
    
    hospital_id = session['hospital']
    hospital_name = session.get('hospital_name')
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date
            FROM donor
            WHERE hospital_id = ?
            ORDER BY registration_date ASC
        ''', (hospital_id,))
        donors = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback for old database structure
        c.execute('''
            SELECT id, name, age, gender, blood_type, organ, status
            FROM donor
            WHERE hospital_id = ?
            ORDER BY id ASC
        ''', (hospital_id,))
        old_donors = c.fetchall()
        donors = [(d[0], 'N/A', d[1], d[2], d[3], d[4], d[5], d[6], 'N/A') for d in old_donors]
    
    conn.close()
    return render_template('hospital_donors.html', donors=donors, hospital_name=hospital_name)

@app.route('/hospital_patients')
def hospital_patients():
    if 'hospital' not in session:
        return redirect('/login')
    
    hospital_id = session['hospital']
    hospital_name = session.get('hospital_name')
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date
            FROM patient
            WHERE hospital_id = ?
            ORDER BY registration_date ASC
        ''', (hospital_id,))
        patients = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback for old database structure
        c.execute('''
            SELECT id, name, age, gender, blood_type, organ, status
            FROM patient
            WHERE hospital_id = ?
            ORDER BY id ASC
        ''', (hospital_id,))
        old_patients = c.fetchall()
        patients = [(p[0], 'N/A', p[1], p[2], p[3], p[4], p[5], p[6], 'N/A') for p in old_patients]
    
    conn.close()
    return render_template('hospital_patients.html', patients=patients, hospital_name=hospital_name)

# ----------------- HOSPITAL MATCHES -----------------
@app.route('/hospital_matches')
def hospital_matches():
    if 'hospital' not in session:
        return redirect('/login')
    
    hospital_id = session['hospital']
    hospital_name = session.get('hospital_name')
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Get matches where this hospital is either donor or patient hospital
    try:
        c.execute('''
            SELECT 
                mr.id as match_id,
                mr.match_date,
                d.name as donor_name,
                d.unique_id as donor_unique_id,
                d.organ as donor_organ,
                d.blood_type as donor_blood_type,
                p.name as patient_name,
                p.unique_id as patient_unique_id,
                p.organ as patient_organ,
                p.blood_type as patient_blood_type,
                hd.name as donor_hospital_name,
                hp.name as patient_hospital_name,
                mr.donor_hospital_id,
                mr.patient_hospital_id
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            WHERE mr.donor_hospital_id = ? OR mr.patient_hospital_id = ?
            ORDER BY mr.match_date DESC
        ''', (hospital_id, hospital_id))
        
        matches = c.fetchall()
        match_list = []
        
        for match in matches:
            match_data = {
                'match_id': match[0],
                'match_date': match[1],
                'donor_name': match[2],
                'donor_unique_id': match[3],
                'donor_organ': match[4],
                'donor_blood_type': match[5],
                'patient_name': match[6],
                'patient_unique_id': match[7],
                'patient_organ': match[8],
                'patient_blood_type': match[9],
                'donor_hospital_name': match[10],
                'patient_hospital_name': match[11],
                'donor_hospital_id': match[12],
                'patient_hospital_id': match[13],
                'is_donor_hospital': match[12] == hospital_id,
                'is_patient_hospital': match[13] == hospital_id
            }
            match_list.append(match_data)
            
    except sqlite3.OperationalError:
        # Fallback for old database structure
        c.execute('''
            SELECT 
                mr.id as match_id,
                mr.match_date,
                d.name as donor_name,
                d.organ as donor_organ,
                d.blood_type as donor_blood_type,
                p.name as patient_name,
                p.organ as patient_organ,
                p.blood_type as patient_blood_type,
                hd.name as donor_hospital_name,
                hp.name as patient_hospital_name,
                mr.donor_hospital_id,
                mr.patient_hospital_id
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            WHERE mr.donor_hospital_id = ? OR mr.patient_hospital_id = ?
            ORDER BY mr.match_date DESC
        ''', (hospital_id, hospital_id))
        
        matches = c.fetchall()
        match_list = []
        
        for match in matches:
            match_data = {
                'match_id': match[0],
                'match_date': match[1],
                'donor_name': match[2],
                'donor_unique_id': 'N/A',
                'donor_organ': match[3],
                'donor_blood_type': match[4],
                'patient_name': match[5],
                'patient_unique_id': 'N/A',
                'patient_organ': match[6],
                'patient_blood_type': match[7],
                'donor_hospital_name': match[8],
                'patient_hospital_name': match[9],
                'donor_hospital_id': match[10],
                'patient_hospital_id': match[11],
                'is_donor_hospital': match[10] == hospital_id,
                'is_patient_hospital': match[11] == hospital_id
            }
            match_list.append(match_data)
    
    conn.close()
    return render_template('hospital_matches.html', matches=match_list, hospital_name=hospital_name)

# ----------------- VIEW MATCHES -----------------
@app.route('/matches')
def matches():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Try new query with unique_id and registration_date, fallback to old query if needed
    try:
        c.execute('''
        SELECT d.id as donor_id, p.id as patient_id, d.name as donor, p.name as patient, 
               d.organ, d.blood_type, d.hospital_id as donor_hospital_id, 
               p.hospital_id as patient_hospital_id, d.unique_id as donor_unique_id,
               p.unique_id as patient_unique_id
        FROM donor d
        JOIN patient p
        ON d.organ = p.organ AND d.blood_type = p.blood_type
        WHERE d.status='Not Matched' AND p.status='Not Matched'
        ORDER BY d.registration_date ASC, p.registration_date ASC
        ''')
        results = c.fetchall()
        display_results = []
        for r in results:
            donor_id, patient_id, donor_name, patient_name, organ, blood, donor_hosp_id, patient_hosp_id, donor_unique_id, patient_unique_id = r
            # Update status
            c.execute("UPDATE donor SET status='Matched' WHERE id=?", (donor_id,))
            c.execute("UPDATE patient SET status='Matched' WHERE id=?", (patient_id,))
            # Insert into match_record
            c.execute("INSERT INTO match_record (donor_id, patient_id, donor_hospital_id, patient_hospital_id, organ, blood_type) VALUES (?, ?, ?, ?, ?, ?)",
                      (donor_id, patient_id, donor_hosp_id, patient_hosp_id, organ, blood))
            display_results.append((donor_name, patient_name, organ, blood, donor_unique_id, patient_unique_id))
    except sqlite3.OperationalError:
        # Fallback to old query without unique_id and registration_date
        c.execute('''
        SELECT d.id as donor_id, p.id as patient_id, d.name as donor, p.name as patient, 
               d.organ, d.blood_type, d.hospital_id as donor_hospital_id, 
               p.hospital_id as patient_hospital_id
        FROM donor d
        JOIN patient p
        ON d.organ = p.organ AND d.blood_type = p.blood_type
        WHERE d.status='Not Matched' AND p.status='Not Matched'
        ''')
        results = c.fetchall()
        display_results = []
        for r in results:
            donor_id, patient_id, donor_name, patient_name, organ, blood, donor_hosp_id, patient_hosp_id = r
            # Update status
            c.execute("UPDATE donor SET status='Matched' WHERE id=?", (donor_id,))
            c.execute("UPDATE patient SET status='Matched' WHERE id=?", (patient_id,))
            # Insert into match_record
            c.execute("INSERT INTO match_record (donor_id, patient_id, donor_hospital_id, patient_hospital_id, organ, blood_type) VALUES (?, ?, ?, ?, ?, ?)",
                      (donor_id, patient_id, donor_hosp_id, patient_hosp_id, organ, blood))
            display_results.append((donor_name, patient_name, organ, blood, 'N/A', 'N/A'))
    
    conn.commit()
    conn.close()
    return render_template('matches.html', results=display_results)

# ----------------- VIEW MATCH RECORDS -----------------
@app.route('/match_records')
def match_records():
    if 'admin' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Try new query with unique_id, fallback to old query if needed
    try:
        c.execute('''
            SELECT mr.match_date, d.name, p.name, mr.organ, mr.blood_type, hd.name, hp.name,
                   d.unique_id, p.unique_id
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            ORDER BY mr.match_date DESC
        ''')
        rows = c.fetchall()
        matches = []
        for row in rows:
            match = {
                'match_date': row[0],
                'donor_name': row[1],
                'patient_name': row[2],
                'organ': row[3],
                'blood_type': row[4],
                'donor_hospital': row[5],
                'patient_hospital': row[6],
                'donor_unique_id': row[7],
                'patient_unique_id': row[8]
            }
            matches.append(match)
    except sqlite3.OperationalError:
        # Fallback to old query without unique_id
        c.execute('''
            SELECT mr.match_date, d.name, p.name, mr.organ, mr.blood_type, hd.name, hp.name
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            ORDER BY mr.match_date DESC
        ''')
        rows = c.fetchall()
        matches = []
        for row in rows:
            match = {
                'match_date': row[0],
                'donor_name': row[1],
                'patient_name': row[2],
                'organ': row[3],
                'blood_type': row[4],
                'donor_hospital': row[5],
                'patient_hospital': row[6],
                'donor_unique_id': 'N/A',
                'patient_unique_id': 'N/A'
            }
            matches.append(match)
    
    conn.close()
    return render_template('match_records.html', matches=matches)

# ----------------- LOGOUT -----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)