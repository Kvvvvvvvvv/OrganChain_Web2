import sqlite3
import os
import uuid
import datetime

# Connect to the database
DB = os.path.join(os.path.dirname(__file__), "database.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Check if there are any hospitals
c.execute("SELECT id FROM hospital LIMIT 1")
hospital = c.fetchone()

if not hospital:
    # Create a test hospital if none exists
    c.execute("INSERT INTO hospital (name, email, location, password) VALUES (?, ?, ?, ?)",
              ("Test Hospital", "test@hospital.com", "Test Location", "password123"))
    hospital_id = c.lastrowid
else:
    hospital_id = hospital[0]

# Add a test donor with the PDF file path
unique_id = str(uuid.uuid4())
registration_date = datetime.datetime.now().isoformat()
medical_document_path = "test_medical_document.pdf"

c.execute("INSERT INTO donor (unique_id, hospital_id, name, age, gender, blood_type, organ, status, registration_date, medical_document_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (unique_id, hospital_id, "John Doe", 30, "Male", "O+", "Kidney", "Not Matched", registration_date, medical_document_path))

# Add a test patient with the PDF file path
unique_id = str(uuid.uuid4())
registration_date = datetime.datetime.now().isoformat()

c.execute("INSERT INTO patient (unique_id, hospital_id, name, age, gender, blood_type, organ, status, registration_date, medical_document_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (unique_id, hospital_id, "Jane Smith", 25, "Female", "O+", "Kidney", "Not Matched", registration_date, medical_document_path))

conn.commit()
conn.close()

print("Test records added successfully!")