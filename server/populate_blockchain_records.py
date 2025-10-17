import sqlite3
import os
import hashlib
from datetime import datetime

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def generate_hash(data):
    """Generate a SHA-256 hash for the given data"""
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

def populate_blockchain_records():
    """Populate the blockchain_records table with all donors and patients data"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Clear existing blockchain records
        c.execute("DELETE FROM blockchain_records")
        print("Cleared existing blockchain records")
        
        # Get all hospitals
        c.execute("SELECT id, name FROM hospital")
        hospitals = c.fetchall()
        hospital_dict = {h[0]: h[1] for h in hospitals}
        
        # Get all donors
        c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id, registration_date FROM donor")
        donors = c.fetchall()
        
        # Get all patients
        c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id, registration_date FROM patient")
        patients = c.fetchall()
        
        # Get all matches
        c.execute("SELECT id, donor_id, patient_id, organ, match_date FROM match_record")
        matches = c.fetchall()
        
        print(f"Found {len(donors)} donors, {len(patients)} patients, and {len(matches)} matches")
        
        # Add hospitals to blockchain
        block_index = 1
        for hospital_id, hospital_name in hospitals:
            previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
            current_hash = generate_hash(f"hospital_{hospital_id}")
            
            c.execute('''
                INSERT INTO blockchain_records 
                (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block_index,
                f"hospital_{hospital_id}",
                previous_hash,
                current_hash,
                'hospital',
                hospital_name,
                'hospital_registration',
                hospital_name,
                datetime.now().isoformat()
            ))
            
            print(f"Added hospital {hospital_name} to blockchain (block {block_index})")
            block_index += 1
        
        # Add donors to blockchain
        for donor_id, unique_id, name, organ, blood_type, hospital_id, registration_date in donors:
            hospital_name = hospital_dict.get(hospital_id, "Unknown Hospital")
            
            previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
            current_hash = generate_hash(f"donor_{donor_id}")
            
            # Encrypt sensitive data as per specification
            encrypted_organ = hashlib.sha256(organ.encode('utf-8')).hexdigest() if organ else ""
            encrypted_blood_type = hashlib.sha256(blood_type.encode('utf-8')).hexdigest() if blood_type else ""
            
            c.execute('''
                INSERT INTO blockchain_records 
                (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block_index,
                unique_id,
                previous_hash,
                current_hash,
                'donor',
                name,
                f"{encrypted_organ[:20]}...{encrypted_blood_type[:20]}" if encrypted_organ and encrypted_blood_type else organ,
                hospital_name,
                registration_date if registration_date else datetime.now().isoformat()
            ))
            
            print(f"Added donor {name} to blockchain (block {block_index})")
            block_index += 1
        
        # Add patients to blockchain
        for patient_id, unique_id, name, organ, blood_type, hospital_id, registration_date in patients:
            hospital_name = hospital_dict.get(hospital_id, "Unknown Hospital")
            
            previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
            current_hash = generate_hash(f"patient_{patient_id}")
            
            # Encrypt sensitive data as per specification
            encrypted_organ = hashlib.sha256(organ.encode('utf-8')).hexdigest() if organ else ""
            encrypted_blood_type = hashlib.sha256(blood_type.encode('utf-8')).hexdigest() if blood_type else ""
            
            c.execute('''
                INSERT INTO blockchain_records 
                (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block_index,
                unique_id,
                previous_hash,
                current_hash,
                'patient',
                name,
                f"{encrypted_organ[:20]}...{encrypted_blood_type[:20]}" if encrypted_organ and encrypted_blood_type else organ,
                hospital_name,
                registration_date if registration_date else datetime.now().isoformat()
            ))
            
            print(f"Added patient {name} to blockchain (block {block_index})")
            block_index += 1
        
        # Add matches to blockchain
        for match_id, donor_id, patient_id, organ, match_date in matches:
            # Get donor name
            c.execute("SELECT name FROM donor WHERE id = ?", (donor_id,))
            donor_record = c.fetchone()
            donor_name = donor_record[0] if donor_record else "Unknown Donor"
            
            # Get patient name
            c.execute("SELECT name FROM patient WHERE id = ?", (patient_id,))
            patient_record = c.fetchone()
            patient_name = patient_record[0] if patient_record else "Unknown Patient"
            
            previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
            current_hash = generate_hash(f"match_{match_id}")
            
            c.execute('''
                INSERT INTO blockchain_records 
                (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block_index,
                f"match_{match_id}",
                previous_hash,
                current_hash,
                'match',
                f"Match between {donor_name} and {patient_name}",
                organ,
                f"Match Record {match_id}",
                match_date if match_date else datetime.now().isoformat()
            ))
            
            print(f"Added match {match_id} to blockchain (block {block_index})")
            block_index += 1
        
        conn.commit()
        conn.close()
        
        print(f"Successfully populated blockchain with {block_index-1} records!")
        return True
        
    except Exception as e:
        print(f"Error populating blockchain records: {e}")
        return False

if __name__ == "__main__":
    populate_blockchain_records()