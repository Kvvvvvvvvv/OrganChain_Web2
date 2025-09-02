from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# ...existing code...

# ----------------- VIEW MATCH RECORDS -----------------
@app.route('/match_records')
def match_records():
    if 'admin' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
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
            'patient_hospital': row[6]
        }
        matches.append(match)
    conn.close()
    return render_template('match_records.html', matches=matches)
from flask import Flask, render_template, request, redirect, session
import sqlite3

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
    
    # Donor table
    c.execute('''
    CREATE TABLE IF NOT EXISTS donor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER,
        name TEXT,
        age INTEGER,
        gender TEXT,
        blood_type TEXT,
        organ TEXT,
        status TEXT DEFAULT 'Not Matched',
        FOREIGN KEY (hospital_id) REFERENCES hospital(id)
    )
    ''')
    
    # Patient table
    c.execute('''
    CREATE TABLE IF NOT EXISTS patient (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER,
        name TEXT,
        age INTEGER,
        gender TEXT,
        blood_type TEXT,
        organ TEXT,
        status TEXT DEFAULT 'Not Matched',
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
                return redirect('/add_hospital')
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
    c.execute("SELECT id, name, age, gender, blood_type, organ, status FROM donor WHERE hospital_id=?", (hospital_id,))
    donors = c.fetchall()
    c.execute("SELECT id, name, age, gender, blood_type, organ, status FROM patient WHERE hospital_id=?", (hospital_id,))
    patients = c.fetchall()
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
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO donor (hospital_id,name,age,gender,blood_type,organ) VALUES (?,?,?,?,?,?)",
                  (hospital_id,name,age,gender,blood_type,organ))
        conn.commit()
        conn.close()
        return "Donor added successfully!"
    
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
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO patient (hospital_id,name,age,gender,blood_type,organ) VALUES (?,?,?,?,?,?)",
                  (hospital_id,name,age,gender,blood_type,organ))
        conn.commit()
        conn.close()
        return "Patient added successfully!"
    
    return render_template('add_patient.html')

# ----------------- VIEW MATCHES -----------------
@app.route('/matches')
def matches():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    SELECT d.id as donor_id, p.id as patient_id, d.name as donor, p.name as patient, d.organ, d.blood_type, d.hospital_id as donor_hospital_id, p.hospital_id as patient_hospital_id
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
        display_results.append((donor_name, patient_name, organ, blood))
    conn.commit()
    conn.close()
    return render_template('matches.html', results=display_results)

# ----------------- LOGOUT -----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
