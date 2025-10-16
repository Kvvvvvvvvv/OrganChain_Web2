from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory
import os
import sqlite3
import uuid
import datetime
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the blockchain service
from blockchain_layer import SimpleBlockchain, load_key, generate_key
import json

app = Flask(__name__, 
            template_folder='../client/templates',
            static_folder='../client/static')
app.secret_key = "secret123"

# Add custom filter for basename
@app.template_filter('basename')
def basename_filter(path):
    if path:
        return os.path.basename(path)
    return ''

# --- Initialize blockchain ---
if not os.path.exists("secret.key"):
    key = generate_key()
else:
    key = load_key()

blockchain = SimpleBlockchain(key)

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

# Print blockchain status

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Admin table
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        wallet_address TEXT UNIQUE  -- Add wallet address for blockchain integration
    )
    ''')
    
    # Hospital table
    c.execute('''
    CREATE TABLE IF NOT EXISTS hospital (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        location TEXT,
        password TEXT,
        wallet_address TEXT UNIQUE  -- Add wallet address for blockchain integration
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
        medical_document_path TEXT,
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
        medical_document_path TEXT,
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
    
    # Add wallet_address columns if they don't exist
    c.execute("PRAGMA table_info(admin)")
    admin_columns = [column[1] for column in c.fetchall()]
    if 'wallet_address' not in admin_columns:
        c.execute("ALTER TABLE admin ADD COLUMN wallet_address TEXT")
    
    c.execute("PRAGMA table_info(hospital)")
    hospital_columns = [column[1] for column in c.fetchall()]
    if 'wallet_address' not in hospital_columns:
        c.execute("ALTER TABLE hospital ADD COLUMN wallet_address TEXT")
    
    # Add medical_document_path columns if they don't exist
    if 'medical_document_path' not in donor_columns:
        c.execute("ALTER TABLE donor ADD COLUMN medical_document_path TEXT")
    
    if 'medical_document_path' not in patient_columns:
        c.execute("ALTER TABLE patient ADD COLUMN medical_document_path TEXT")
    
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

# Deduplicate historical match records and fix statuses
def dedupe_matches():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Remove extra matches per patient (keep earliest id)
    c.execute('''
        DELETE FROM match_record
        WHERE id NOT IN (
            SELECT MIN(id) FROM match_record GROUP BY patient_id
        )
    ''')
    # Remove extra matches per donor (keep earliest id)
    c.execute('''
        DELETE FROM match_record
        WHERE id NOT IN (
            SELECT MIN(id) FROM match_record GROUP BY donor_id
        )
    ''')
    # Sync donor statuses
    c.execute('''
        UPDATE donor SET status='Matched'
        WHERE id IN (SELECT donor_id FROM match_record)
    ''')
    c.execute('''
        UPDATE donor SET status='Not Matched'
        WHERE id NOT IN (SELECT donor_id FROM match_record)
    ''')
    # Sync patient statuses
    c.execute('''
        UPDATE patient SET status='Matched'
        WHERE id IN (SELECT patient_id FROM match_record)
    ''')
    c.execute('''
        UPDATE patient SET status='Not Matched'
        WHERE id NOT IN (SELECT patient_id FROM match_record)
    ''')
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# Function to sync all database records to blockchain
def sync_all_to_blockchain():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Sync hospitals
    c.execute("SELECT id, name, email, location FROM hospital")
    hospitals = c.fetchall()
    for hospital in hospitals:
        hospital_id, name, email, location = hospital
        try:
            block = blockchain.add_transaction(
                donor_id=f"hospital_{hospital_id}",
                organ_type="hospital_registration",
                hospital=name,
                receiver_id=f"hospital_{hospital_id}"
            )
        except Exception as e:
            print(f"Error adding hospital {hospital_id} to blockchain: {e}")
    
    # Sync donors
    c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id FROM donor")
    donors = c.fetchall()
    for donor in donors:
        donor_id, unique_id, name, organ, blood_type, hospital_id = donor
        # Get hospital name
        c.execute("SELECT name FROM hospital WHERE id = ?", (hospital_id,))
        hospital_record = c.fetchone()
        hospital_name = hospital_record[0] if hospital_record else "Unknown"
        
        try:
            block = blockchain.add_transaction(
                donor_id=unique_id,
                organ_type=organ,
                hospital=hospital_name,
                receiver_id=f"donor_{donor_id}"
            )
        except Exception as e:
            print(f"Error adding donor {donor_id} to blockchain: {e}")
    
    # Sync patients
    c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id FROM patient")
    patients = c.fetchall()
    for patient in patients:
        patient_id, unique_id, name, organ, blood_type, hospital_id = patient
        # Get hospital name
        c.execute("SELECT name FROM hospital WHERE id = ?", (hospital_id,))
        hospital_record = c.fetchone()
        hospital_name = hospital_record[0] if hospital_record else "Unknown"
        
        try:
            block = blockchain.add_transaction(
                donor_id=f"patient_{patient_id}",
                organ_type=organ,
                hospital=hospital_name,
                receiver_id=unique_id
            )
        except Exception as e:
            print(f"Error adding patient {patient_id} to blockchain: {e}")
    
    # Sync matches
    c.execute("SELECT id, donor_id, patient_id, organ, match_date FROM match_record")
    matches = c.fetchall()
    for match in matches:
        match_id, donor_id, patient_id, organ, match_date = match
        # Get donor unique_id
        c.execute("SELECT unique_id, hospital_id FROM donor WHERE id = ?", (donor_id,))
        donor_record = c.fetchone()
        donor_unique_id = donor_record[0] if donor_record else "Unknown"
        donor_hospital_id = donor_record[1] if donor_record else None
        
        # Get patient unique_id
        c.execute("SELECT unique_id, hospital_id FROM patient WHERE id = ?", (patient_id,))
        patient_record = c.fetchone()
        patient_unique_id = patient_record[0] if patient_record else "Unknown"
        patient_hospital_id = patient_record[1] if patient_record else None
        
        # Get hospital names
        donor_hospital_name = "Unknown"
        patient_hospital_name = "Unknown"
        
        if donor_hospital_id:
            c.execute("SELECT name FROM hospital WHERE id = ?", (donor_hospital_id,))
            donor_hospital_record = c.fetchone()
            donor_hospital_name = donor_hospital_record[0] if donor_hospital_record else "Unknown"
            
        if patient_hospital_id:
            c.execute("SELECT name FROM hospital WHERE id = ?", (patient_hospital_id,))
            patient_hospital_record = c.fetchone()
            patient_hospital_name = patient_hospital_record[0] if patient_hospital_record else "Unknown"
        
        try:
            block = blockchain.add_transaction(
                donor_id=donor_unique_id,
                organ_type=f"{organ}_match",
                hospital=f"{donor_hospital_name}_to_{patient_hospital_name}",
                receiver_id=patient_unique_id
            )
        except Exception as e:
            print(f"Error adding match {match_id} to blockchain: {e}")
    
    conn.close()
    
    # Save blockchain to JSON file in the project root
    try:
        with open('../blockchain.json', 'w') as f:
            json.dump(blockchain.get_chain(), f, indent=4)
        print("Blockchain synced successfully!")
    except Exception as e:
        print(f"Error saving blockchain to file: {e}")

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    message = None
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        wallet_address = request.form.get('wallet_address')  # Get wallet address from form
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        if role == 'admin':
            c.execute("SELECT * FROM admin WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            if user:
                # For admin, we can optionally check blockchain authentication
                session['admin'] = user[0]
                session['admin_wallet'] = user[3] if len(user) > 3 else None
                return redirect('/manage_hospitals')
        elif role == 'hospital':
            c.execute("SELECT * FROM hospital WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            if user:
                # For hospital, check if they are registered on the blockchain
                hospital_wallet = user[5] if len(user) > 5 else None
                # Skip blockchain check as per user request
                # if hospital_wallet and BLOCKCHAIN_AVAILABLE:
                #     # Check if hospital is registered on blockchain
                #     try:
                #         from blockchain_service import is_hospital_registered
                #         is_registered = is_hospital_registered(hospital_wallet)
                #         if not is_registered:
                #             message = "Hospital not registered on blockchain"
                #             conn.close()
                #             return render_template('admin_login.html', message=message)
                #     except:
                #         # If blockchain service fails, continue without checking
                #         pass
                
                session['hospital'] = user[0]
                session['hospital_name'] = user[1]
                session['hospital_email'] = user[2]
                session['hospital_location'] = user[3]
                session['hospital_wallet'] = hospital_wallet
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
            SELECT d.id, d.unique_id, d.name, d.age, d.gender, d.blood_type, d.organ, d.status, d.registration_date, h.name as hospital_name, d.medical_document_path
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
        donors = [(d[0], 'N/A', d[1], d[2], d[3], d[4], d[5], d[6], 'N/A', d[7], None) for d in old_donors]
    
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
            SELECT p.id, p.unique_id, p.name, p.age, p.gender, p.blood_type, p.organ, p.status, p.registration_date, h.name as hospital_name, p.medical_document_path
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
        patients = [(p[0], 'N/A', p[1], p[2], p[3], p[4], p[5], p[6], 'N/A', p[7], None) for p in old_patients]
    
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
        wallet_address = request.form.get('wallet_address')  # Get wallet address
        
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            # Include wallet_address in the insert statement
            c.execute("INSERT INTO hospital (name,email,location,password,wallet_address) VALUES (?,?,?,?,?)",
                      (name,email,location,password,wallet_address))
            conn.commit()
            hospital_id = c.lastrowid
            conn.close()
            
            # Add to blockchain
            try:
                block = blockchain.add_transaction(
                    donor_id=f"hospital_{hospital_id}",
                    organ_type="hospital_registration",
                    hospital=name,
                    receiver_id=f"hospital_{hospital_id}"
                )
                
                # Save blockchain to JSON file
                with open('../blockchain.json', 'w') as f:
                    json.dump(blockchain.get_chain(), f, indent=4)
            except Exception as e:
                print(f"Error adding hospital to blockchain: {e}")
                
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
    
    # Get counts for statistics
    c.execute("SELECT COUNT(*) FROM donor")
    donors_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM patient")
    patients_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM match_record")
    matches_count = c.fetchone()[0]
    
    conn.close()
    message = request.args.get('message')
    return render_template('manage_hospitals.html', hospitals=hospitals, donors_count=donors_count, 
                          patients_count=patients_count, matches_count=matches_count, message=message)

@app.route('/delete_hospital', methods=['POST'])
def delete_hospital():
    if 'admin' not in session:
        return redirect('/login')
    hospital_id = request.form['hospital_id']
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Delete match records where this hospital is involved
    c.execute("DELETE FROM match_record WHERE donor_hospital_id=? OR patient_hospital_id=?", (hospital_id, hospital_id))
    # Delete donors and patients for this hospital
    c.execute("DELETE FROM donor WHERE hospital_id=?", (hospital_id,))
    c.execute("DELETE FROM patient WHERE hospital_id=?", (hospital_id,))
    # Delete the hospital itself
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
    hospital_wallet = session.get('hospital_wallet')
    
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
    # Pass hospital_wallet to the template
    return render_template('hospital_login.html', hospital_name=hospital_name, 
                          hospital_email=hospital_email, hospital_location=hospital_location,
                          hospital_wallet=hospital_wallet, donors=donors, patients=patients)

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
        
        # Handle PDF file upload
        medical_document_path = None
        if 'medical_document' in request.files:
            file = request.files['medical_document']
            if file and file.filename != '' and file.filename.lower().endswith('.pdf'):
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                
                # Generate unique filename
                filename = f"donor_{str(uuid.uuid4())}_{file.filename}"
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)
                # Store only the filename, not the full path
                medical_document_path = filename
        
        # Generate unique ID and current timestamp
        unique_id = str(uuid.uuid4())
        registration_date = datetime.datetime.now().isoformat()
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Try new insert with unique_id, status, registration_date, and medical_document_path, fallback to old insert if needed
        try:
            c.execute("INSERT INTO donor (unique_id, hospital_id, name, age, gender, blood_type, organ, status, registration_date, medical_document_path) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (unique_id, hospital_id, name, age, gender, blood_type, organ, 'Not Matched', registration_date, medical_document_path))
        except sqlite3.OperationalError:
            # Fallback to old insert without new columns
            c.execute("INSERT INTO donor (hospital_id, name, age, gender, blood_type, organ, status) VALUES (?,?,?,?,?,?,?)",
                      (hospital_id, name, age, gender, blood_type, organ, 'Not Matched'))
            unique_id = 'N/A'
        
        conn.commit()
        donor_id = c.lastrowid
        conn.close()
        
        # Add to blockchain
        try:
            # Get hospital name
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT name FROM hospital WHERE id = ?", (hospital_id,))
            hospital_record = c.fetchone()
            hospital_name = hospital_record[0] if hospital_record else "Unknown"
            conn.close()
            
            block = blockchain.add_transaction(
                donor_id=unique_id,
                organ_type=organ,
                hospital=hospital_name,
                receiver_id=f"donor_{donor_id}"
            )
            
            # Save blockchain to JSON file
            with open('../blockchain.json', 'w') as f:
                json.dump(blockchain.get_chain(), f, indent=4)
        except Exception as e:
            print(f"Error adding donor to blockchain: {e}")
        
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
        
        # Handle PDF file upload
        medical_document_path = None
        if 'medical_document' in request.files:
            file = request.files['medical_document']
            if file and file.filename != '' and file.filename.lower().endswith('.pdf'):
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                
                # Generate unique filename
                filename = f"patient_{str(uuid.uuid4())}_{file.filename}"
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)
                # Store only the filename, not the full path
                medical_document_path = filename
        
        # Generate unique ID and current timestamp
        unique_id = str(uuid.uuid4())
        registration_date = datetime.datetime.now().isoformat()
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Try new insert with unique_id, status, registration_date, and medical_document_path, fallback to old insert if needed
        try:
            c.execute("INSERT INTO patient (unique_id, hospital_id, name, age, gender, blood_type, organ, status, registration_date, medical_document_path) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (unique_id, hospital_id, name, age, gender, blood_type, organ, 'Not Matched', registration_date, medical_document_path))
        except sqlite3.OperationalError:
            # Fallback to old insert without new columns
            c.execute("INSERT INTO patient (hospital_id, name, age, gender, blood_type, organ, status) VALUES (?,?,?,?,?,?,?)",
                      (hospital_id, name, age, gender, blood_type, organ, 'Not Matched'))
            unique_id = 'N/A'
        
        conn.commit()
        patient_id = c.lastrowid
        conn.close()
        
        # Add to blockchain
        try:
            # Get hospital name
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT name FROM hospital WHERE id = ?", (hospital_id,))
            hospital_record = c.fetchone()
            hospital_name = hospital_record[0] if hospital_record else "Unknown"
            conn.close()
            
            block = blockchain.add_transaction(
                donor_id=f"patient_{patient_id}",
                organ_type=organ,
                hospital=hospital_name,
                receiver_id=unique_id
            )
            
            # Save blockchain to JSON file
            with open('../blockchain.json', 'w') as f:
                json.dump(blockchain.get_chain(), f, indent=4)
        except Exception as e:
            print(f"Error adding patient to blockchain: {e}")
        
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
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date, medical_document_path
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
            SELECT id, unique_id, name, age, gender, blood_type, organ, status, registration_date, medical_document_path
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
    
    # Improved matching algorithm with proper FCFS implementation and blood compatibility
    try:
        # Get all unmatched donors ordered by registration date (FCFS)
        c.execute('''
        SELECT d.id, d.name, d.organ, d.blood_type, d.hospital_id, d.unique_id, d.registration_date, d.age
        FROM donor d
        WHERE d.status='Not Matched'
          AND NOT EXISTS (SELECT 1 FROM match_record mr WHERE mr.donor_id = d.id)
        ORDER BY d.registration_date ASC
        ''')
        donors = c.fetchall()
        
        # Get all unmatched patients ordered by registration date (FCFS)
        c.execute('''
        SELECT p.id, p.name, p.organ, p.blood_type, p.hospital_id, p.unique_id, p.registration_date, p.age
        FROM patient p
        WHERE p.status='Not Matched'
          AND NOT EXISTS (SELECT 1 FROM match_record mr WHERE mr.patient_id = p.id)
        ORDER BY p.registration_date ASC
        ''')
        patients = c.fetchall()
        
        display_results = []
        matched_donor_ids = set()
        matched_patient_ids = set()
        
        # Blood compatibility rules (who can receive from whom)
        # A+ can receive from A+, A-, O+, O-
        # A- can receive from A-, O-
        # B+ can receive from B+, B-, O+, O-
        # B- can receive from B-, O-
        # AB+ can receive from all (universal recipient)
        # AB- can receive from AB-, A-, B-, O-
        # O+ can receive from O+, O-
        # O- can receive from O- (universal donor)
        blood_compatibility = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']  # Universal donor
        }
        
        # Create a mapping of patients by organ and compatible blood types for efficient lookup
        patient_map = {}
        for patient in patients:
            patient_id, patient_name, organ, blood_type, hospital_id, unique_id, reg_date, patient_age = patient
            # For each compatible blood type, add this patient
            if blood_type in blood_compatibility:
                for compatible_blood in blood_compatibility[blood_type]:
                    key = (organ, compatible_blood)
                    if key not in patient_map:
                        patient_map[key] = []
                    patient_map[key].append(patient)
        
        # Match donors with patients based on organ and blood compatibility (FCFS)
        for donor in donors:
            donor_id, donor_name, organ, blood_type, donor_hosp_id, donor_unique_id, donor_reg_date, donor_age = donor
            
            # Skip if donor already matched
            if donor_id in matched_donor_ids:
                continue
                
            # Look for compatible patient
            key = (organ, blood_type)
            if key in patient_map and patient_map[key]:
                # Get the first (earliest registered) compatible patient
                patient = patient_map[key].pop(0)
                patient_id, patient_name, _, _, patient_hosp_id, patient_unique_id, patient_reg_date, patient_age = patient
                
                # Skip if patient already matched
                if patient_id in matched_patient_ids:
                    continue
                
                # Create match in database
                c.execute("UPDATE donor SET status='Matched' WHERE id=?", (donor_id,))
                c.execute("UPDATE patient SET status='Matched' WHERE id=?", (patient_id,))
                c.execute("INSERT INTO match_record (donor_id, patient_id, donor_hospital_id, patient_hospital_id, organ, blood_type) VALUES (?, ?, ?, ?, ?, ?)",
                          (donor_id, patient_id, donor_hosp_id, patient_hosp_id, organ, blood_type))
                
                # Add to blockchain
                try:
                    # Get hospital names
                    c.execute("SELECT name FROM hospital WHERE id = ?", (donor_hosp_id,))
                    donor_hospital_record = c.fetchone()
                    donor_hospital_name = donor_hospital_record[0] if donor_hospital_record else "Unknown"
                    
                    c.execute("SELECT name FROM hospital WHERE id = ?", (patient_hosp_id,))
                    patient_hospital_record = c.fetchone()
                    patient_hospital_name = patient_hospital_record[0] if patient_hospital_record else "Unknown"
                    
                    block = blockchain.add_transaction(
                        donor_id=donor_unique_id,
                        organ_type=f"{organ}_match",
                        hospital=f"{donor_hospital_name}_to_{patient_hospital_name}",
                        receiver_id=patient_unique_id
                    )
                    
                    # Save blockchain to JSON file
                    with open('../blockchain.json', 'w') as f:
                        json.dump(blockchain.get_chain(), f, indent=4)
                except Exception as e:
                    print(f"Error adding match to blockchain: {e}")
                
                matched_donor_ids.add(donor_id)
                matched_patient_ids.add(patient_id)
                display_results.append((donor_name, patient_name, organ, blood_type, donor_unique_id, patient_unique_id))
                
    except sqlite3.OperationalError as e:
        print(f"Error in matching algorithm: {e}")
        # Fallback to old query without unique_id and registration_date
        c.execute('''
        SELECT d.id as donor_id, p.id as patient_id, d.name as donor, p.name as patient,
               d.organ, d.blood_type, d.hospital_id as donor_hospital_id,
               p.hospital_id as patient_hospital_id, d.age as donor_age, p.age as patient_age
        FROM donor d
        JOIN patient p
          ON d.organ = p.organ AND d.blood_type = p.blood_type
        WHERE d.status='Not Matched'
          AND p.status='Not Matched'
          AND NOT EXISTS (SELECT 1 FROM match_record mr WHERE mr.donor_id = d.id)
          AND NOT EXISTS (SELECT 1 FROM match_record mr2 WHERE mr2.patient_id = p.id)
        ORDER BY d.id ASC, p.id ASC
        ''')
        results = c.fetchall()
        display_results = []
        matched_donor_ids = set()
        matched_patient_ids = set()
        for r in results:
            donor_id, patient_id, donor_name, patient_name, organ, blood, donor_hosp_id, patient_hosp_id, donor_age, patient_age = r
            if donor_id in matched_donor_ids or patient_id in matched_patient_ids:
                continue
            c.execute("SELECT 1 FROM match_record WHERE donor_id=? OR patient_id=? LIMIT 1", (donor_id, patient_id))
            if c.fetchone():
                continue
            c.execute("UPDATE donor SET status='Matched' WHERE id=?", (donor_id,))
            c.execute("UPDATE patient SET status='Matched' WHERE id=?", (patient_id,))
            c.execute("INSERT INTO match_record (donor_id, patient_id, donor_hospital_id, patient_hospital_id, organ, blood_type) VALUES (?, ?, ?, ?, ?, ?)",
                      (donor_id, patient_id, donor_hosp_id, patient_hosp_id, organ, blood))
            
            # Add to blockchain
            try:
                # Get hospital names
                c.execute("SELECT name FROM hospital WHERE id = ?", (donor_hosp_id,))
                donor_hospital_record = c.fetchone()
                donor_hospital_name = donor_hospital_record[0] if donor_hospital_record else "Unknown"
                
                c.execute("SELECT name FROM hospital WHERE id = ?", (patient_hosp_id,))
                patient_hospital_record = c.fetchone()
                patient_hospital_name = patient_hospital_record[0] if patient_hospital_record else "Unknown"
                
                block = blockchain.add_transaction(
                    donor_id=f"donor_{donor_id}",
                    organ_type=f"{organ}_match",
                    hospital=f"{donor_hospital_name}_to_{patient_hospital_name}",
                    receiver_id=f"patient_{patient_id}"
                )
                
                # Save blockchain to JSON file
                with open('../blockchain.json', 'w') as f:
                    json.dump(blockchain.get_chain(), f, indent=4)
            except Exception as e:
                print(f"Error adding match to blockchain: {e}")
            
            matched_donor_ids.add(donor_id)
            matched_patient_ids.add(patient_id)
            display_results.append((donor_name, patient_name, organ, blood, 'N/A', 'N/A'))
    
    conn.commit()
    conn.close()
    # Clean up any historical duplicates and sync statuses
    dedupe_matches()
    return render_template('matches.html', results=display_results)

# ----------------- VIEW MATCH RECORDS -----------------
@app.route('/match_records')
def match_records():
    if 'admin' not in session:
        return redirect('/login')
    # Ensure no duplicates before reporting
    dedupe_matches()
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

@app.route('/add_to_chain', methods=['POST'])
def add_to_chain():
    data = request.get_json()
    donor = data.get('donor')
    organ = data.get('organ')
    hospital = data.get('hospital')
    receiver = data.get('receiver')

    block = blockchain.add_transaction(donor, organ, hospital, receiver)

    # Save blockchain to JSON file in the project root
    with open('../blockchain.json', 'w') as f:
        json.dump(blockchain.get_chain(), f, indent=4)

    return {'message': 'Record added to blockchain', 'block_index': block['index']}

@app.route('/chain')
def view_chain():
    return jsonify(blockchain.get_chain(decrypt=True))

@app.route('/sync_to_blockchain')
def sync_to_blockchain():
    try:
        sync_all_to_blockchain()
        return jsonify({"message": "Successfully synced all database records to blockchain"})
    except Exception as e:
        return jsonify({"error": f"Failed to sync to blockchain: {str(e)}"}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'uploads'), filename)

@app.route('/view_pdf/<path:filepath>')
def view_pdf(filepath):
    filename = os.path.basename(filepath)
    title = "Donor Medical Document" if "donor" in filename.lower() else "Patient Medical Document"
    return render_template('view_pdf.html', filepath=filepath, filename=filename, title=title)

if __name__ == '__main__':
    app.run(debug=True)