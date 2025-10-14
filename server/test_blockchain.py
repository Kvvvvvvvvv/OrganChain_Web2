import sqlite3
import os
from blockchain_service import add_match_to_chain

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def add_test_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Add test hospitals if they don't exist
    c.execute("SELECT COUNT(*) FROM hospital")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO hospital (name, email, location, password) VALUES (?, ?, ?, ?)",
                  ("Test Hospital 1", "hospital1@test.com", "Location 1", "password1"))
        c.execute("INSERT INTO hospital (name, email, location, password) VALUES (?, ?, ?, ?)",
                  ("Test Hospital 2", "hospital2@test.com", "Location 2", "password2"))
    
    # Check if test donor already exists
    c.execute("SELECT COUNT(*) FROM donor WHERE name='John Doe'")
    if c.fetchone()[0] == 0:
        # Add test donor
        c.execute("INSERT INTO donor (hospital_id, name, age, gender, blood_type, organ, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (1, "John Doe", 35, "Male", "O+", "Kidney", "Not Matched"))
    
    # Check if test patient already exists
    c.execute("SELECT COUNT(*) FROM patient WHERE name='Jane Smith'")
    if c.fetchone()[0] == 0:
        # Add test patient
        c.execute("INSERT INTO patient (hospital_id, name, age, gender, blood_type, organ, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (2, "Jane Smith", 45, "Female", "O+", "Kidney", "Not Matched"))
    
    conn.commit()
    conn.close()
    print("Test data added successfully!")

def trigger_match():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Get donor and patient data
    c.execute("SELECT id, name, age, hospital_id FROM donor WHERE status='Not Matched' LIMIT 1")
    donor = c.fetchone()
    
    c.execute("SELECT id, name, age, hospital_id FROM patient WHERE status='Not Matched' LIMIT 1")
    patient = c.fetchone()
    
    if donor and patient:
        donor_id, donor_name, donor_age, donor_hospital_id = donor
        patient_id, patient_name, patient_age, patient_hospital_id = patient
        
        # Get hospital names
        c.execute("SELECT name FROM hospital WHERE id=?", (donor_hospital_id,))
        donor_hospital_result = c.fetchone()
        donor_hospital_name = donor_hospital_result[0] if donor_hospital_result else "Unknown Hospital"
        
        c.execute("SELECT name FROM hospital WHERE id=?", (patient_hospital_id,))
        patient_hospital_result = c.fetchone()
        patient_hospital_name = patient_hospital_result[0] if patient_hospital_result else "Unknown Hospital"
        
        # Create match data for blockchain
        match_data = {
            'donorName': donor_name,
            'donorAge': donor_age,
            'donorHospital': donor_hospital_name,
            'organ': 'Kidney',
            'bloodType': 'O+',
            'patientName': patient_name,
            'patientAge': patient_age,
            'patientHospital': patient_hospital_name,
            'date': '2025-10-12'
        }
        
        # Add match to blockchain
        try:
            receipt = add_match_to_chain(match_data)
            print(f"Match added to blockchain successfully!")
            print(f"Transaction hash: {receipt.transactionHash.hex()}")
            print(f"Gas used: {receipt.gasUsed}")
            
            # Update database status
            c.execute("UPDATE donor SET status='Matched' WHERE id=?", (donor_id,))
            c.execute("UPDATE patient SET status='Matched' WHERE id=?", (patient_id,))
            conn.commit()
            print("Database updated successfully!")
            
        except Exception as e:
            print(f"Error adding match to blockchain: {e}")
    else:
        print("No unmatched donor/patient found!")
    
    conn.close()

if __name__ == "__main__":
    add_test_data()
    trigger_match()