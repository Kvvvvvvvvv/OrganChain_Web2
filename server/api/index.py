from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import uuid
import datetime
import os

app = Flask(__name__, 
            template_folder='../../client/templates',
            static_folder='../../client/static')
app.secret_key = "secret123"

# Use absolute path for database
DB = os.path.join(os.path.dirname(__file__), "database.db")

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

# Import all routes from the main app
from app import *

# Vercel entry point
def handler(request):
    return app(request.environ, start_response)

def start_response(status, headers):
    pass
