import sqlite3
import os
import hashlib
from datetime import datetime

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def generate_hash(data):
    """Generate a SHA-256 hash for the given data"""
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

def update_blockchain_records():
    """Update the blockchain_records table with any new data from donors, patients, and matches"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get the highest block index currently in the blockchain
        c.execute("SELECT MAX(block_index) FROM blockchain_records")
        max_block_index = c.fetchone()[0]
        if max_block_index is None:
            max_block_index = 0
            
        print(f"Current highest block index: {max_block_index}")
        
        # Get all hospitals
        c.execute("SELECT id, name FROM hospital")
        hospitals = c.fetchall()
        hospital_dict = {h[0]: h[1] for h in hospitals}
        
        # Get existing unique IDs in blockchain
        c.execute("SELECT unique_id FROM blockchain_records")
        existing_ids = {row[0] for row in c.fetchall()}
        
        block_index = max_block_index + 1
        records_added = 0
        
        # Add new hospitals to blockchain
        for hospital_id, hospital_name in hospitals:
            hospital_unique_id = f"hospital_{hospital_id}"
            if hospital_unique_id not in existing_ids:
                previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
                current_hash = generate_hash(hospital_unique_id)
                
                c.execute('''
                    INSERT INTO blockchain_records 
                    (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block_index,
                    hospital_unique_id,
                    previous_hash,
                    current_hash,
                    'hospital',
                    hospital_name,
                    'hospital_registration',
                    hospital_name,
                    datetime.now().isoformat()
                ))
                
                print(f"Added hospital {hospital_name} to blockchain (block {block_index})")
                existing_ids.add(hospital_unique_id)
                block_index += 1
                records_added += 1
        
        # Add new donors to blockchain
        c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id, registration_date FROM donor")
        donors = c.fetchall()
        
        for donor_id, unique_id, name, organ, blood_type, hospital_id, registration_date in donors:
            if unique_id not in existing_ids:
                hospital_name = hospital_dict.get(hospital_id, "Unknown Hospital")
                
                previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
                current_hash = generate_hash(unique_id)
                
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
                existing_ids.add(unique_id)
                block_index += 1
                records_added += 1
        
        # Add new patients to blockchain
        c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id, registration_date FROM patient")
        patients = c.fetchall()
        
        for patient_id, unique_id, name, organ, blood_type, hospital_id, registration_date in patients:
            if unique_id not in existing_ids:
                hospital_name = hospital_dict.get(hospital_id, "Unknown Hospital")
                
                previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
                current_hash = generate_hash(unique_id)
                
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
                existing_ids.add(unique_id)
                block_index += 1
                records_added += 1
        
        # Add new matches to blockchain
        c.execute("SELECT id, donor_id, patient_id, organ, match_date FROM match_record")
        matches = c.fetchall()
        
        for match_id, donor_id, patient_id, organ, match_date in matches:
            match_unique_id = f"match_{match_id}"
            if match_unique_id not in existing_ids:
                # Get donor name
                c.execute("SELECT name FROM donor WHERE id = ?", (donor_id,))
                donor_record = c.fetchone()
                donor_name = donor_record[0] if donor_record else "Unknown Donor"
                
                # Get patient name
                c.execute("SELECT name FROM patient WHERE id = ?", (patient_id,))
                patient_record = c.fetchone()
                patient_name = patient_record[0] if patient_record else "Unknown Patient"
                
                previous_hash = '0' if block_index == 1 else generate_hash(f"block_{block_index-1}")
                current_hash = generate_hash(match_unique_id)
                
                c.execute('''
                    INSERT INTO blockchain_records 
                    (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block_index,
                    match_unique_id,
                    previous_hash,
                    current_hash,
                    'match',
                    f"Match between {donor_name} and {patient_name}",
                    organ,
                    f"Match Record {match_id}",
                    match_date if match_date else datetime.now().isoformat()
                ))
                
                print(f"Added match {match_id} to blockchain (block {block_index})")
                existing_ids.add(match_unique_id)
                block_index += 1
                records_added += 1
        
        conn.commit()
        conn.close()
        
        print(f"Successfully updated blockchain with {records_added} new records!")
        print(f"Total block index is now: {block_index - 1}")
        return True
        
    except Exception as e:
        print(f"Error updating blockchain records: {e}")
        return False

if __name__ == "__main__":
    update_blockchain_records()