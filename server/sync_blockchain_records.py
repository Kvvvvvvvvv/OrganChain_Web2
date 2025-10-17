import sqlite3
import os
import sys
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from blockchain_service import is_connected, contract, web3, add_record_to_chain, add_match_to_chain, add_hospital_to_blockchain

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def sync_blockchain_records():
    """Sync database records with the blockchain"""
    
    # Check if blockchain is connected
    if not is_connected():
        print("Blockchain is not connected. Please start Ganache on http://127.0.0.1:7545")
        return False
    
    if not contract:
        print("Contract not loaded. Cannot sync records.")
        return False
    
    print("Blockchain is connected. Starting sync process...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Sync hospitals
        print("Syncing hospitals...")
        c.execute("SELECT id, name, email, location FROM hospital")
        hospitals = c.fetchall()
        for hospital in hospitals:
            hospital_id, name, email, location = hospital
            try:
                receipt = add_hospital_to_blockchain(name, email, location)
                if receipt:
                    print(f"Added hospital {name} to blockchain")
                else:
                    print(f"Failed to add hospital {name} to blockchain")
            except Exception as e:
                print(f"Error adding hospital {name} to blockchain: {e}")
        
        # Sync donors
        print("Syncing donors...")
        c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id FROM donor")
        donors = c.fetchall()
        for donor in donors:
            donor_id, unique_id, name, organ, blood_type, hospital_id = donor
            # Get hospital name
            c.execute("SELECT name FROM hospital WHERE id = ?", (hospital_id,))
            hospital_record = c.fetchone()
            hospital_name = hospital_record[0] if hospital_record else "Unknown"
            
            try:
                receipt = add_record_to_chain(
                    donor_id=unique_id,
                    organ_type=organ,
                    hospital=hospital_name,
                    receiver_id=f"donor_{donor_id}"
                )
                if receipt:
                    print(f"Added donor {name} to blockchain")
                else:
                    print(f"Failed to add donor {name} to blockchain")
            except Exception as e:
                print(f"Error adding donor {name} to blockchain: {e}")
        
        # Sync patients
        print("Syncing patients...")
        c.execute("SELECT id, unique_id, name, organ, blood_type, hospital_id FROM patient")
        patients = c.fetchall()
        for patient in patients:
            patient_id, unique_id, name, organ, blood_type, hospital_id = patient
            # Get hospital name
            c.execute("SELECT name FROM hospital WHERE id = ?", (hospital_id,))
            hospital_record = c.fetchone()
            hospital_name = hospital_record[0] if hospital_record else "Unknown"
            
            try:
                receipt = add_record_to_chain(
                    donor_id=f"patient_{patient_id}",
                    organ_type=organ,
                    hospital=hospital_name,
                    receiver_id=unique_id
                )
                if receipt:
                    print(f"Added patient {name} to blockchain")
                else:
                    print(f"Failed to add patient {name} to blockchain")
            except Exception as e:
                print(f"Error adding patient {name} to blockchain: {e}")
        
        # Sync matches
        print("Syncing matches...")
        c.execute("SELECT id, donor_id, patient_id, organ, match_date FROM match_record")
        matches = c.fetchall()
        for match in matches:
            match_id, donor_id, patient_id, organ, match_date = match
            # Get donor info
            c.execute("SELECT name, age, hospital_id FROM donor WHERE id = ?", (donor_id,))
            donor_record = c.fetchone()
            donor_name = donor_record[0] if donor_record else "Unknown"
            donor_age = donor_record[1] if donor_record else 0
            donor_hospital_id = donor_record[2] if donor_record else None
            
            # Get patient info
            c.execute("SELECT name, age, hospital_id FROM patient WHERE id = ?", (patient_id,))
            patient_record = c.fetchone()
            patient_name = patient_record[0] if patient_record else "Unknown"
            patient_age = patient_record[1] if patient_record else 0
            patient_hospital_id = patient_record[2] if patient_record else None
            
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
                match_data = {
                    'donorName': donor_name,
                    'donorAge': donor_age,
                    'donorHospital': donor_hospital_name,
                    'organ': organ,
                    'bloodType': blood_type if blood_type else "Unknown",
                    'patientName': patient_name,
                    'patientAge': patient_age,
                    'patientHospital': patient_hospital_name,
                    'date': match_date
                }
                
                receipt = add_match_to_chain(match_data)
                if receipt:
                    print(f"Added match {match_id} to blockchain")
                else:
                    print(f"Failed to add match {match_id} to blockchain")
            except Exception as e:
                print(f"Error adding match {match_id} to blockchain: {e}")
        
        conn.close()
        print("Blockchain sync completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during blockchain sync: {e}")
        return False

if __name__ == "__main__":
    sync_blockchain_records()