import sqlite3
import os
import sys
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from blockchain_service import is_connected, contract, web3, get_all_records, get_all_matches

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def update_blockchain_database():
    """Update blockchain records in the database based on the deployed contract"""
    
    # Check if blockchain is connected
    if not is_connected():
        print("Blockchain is not connected. Please start Ganache on http://127.0.0.1:7545")
        return False
    
    if not contract:
        print("Contract not loaded. Cannot update records.")
        return False
    
    print("Blockchain is connected. Updating database records...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Clear existing blockchain records
        c.execute("DELETE FROM blockchain_records")
        print("Cleared existing blockchain records")
        
        # Get all records from blockchain
        print("Fetching records from blockchain...")
        records = get_all_records()
        print(f"Found {len(records)} records in blockchain")
        
        # Get all matches from blockchain
        print("Fetching matches from blockchain...")
        matches = get_all_matches()
        print(f"Found {len(matches)} matches in blockchain")
        
        # Process records
        block_index = 1
        for record in records:
            try:
                donor_id = record['donorId']
                organ_type = record['organType']
                hospital = record['hospital']
                receiver_id = record['receiverId']
                timestamp = record['timestamp']
                
                # Determine record type
                if donor_id.startswith('patient_'):
                    record_type = 'patient'
                    unique_id = donor_id
                    name = 'Patient Record'
                elif donor_id.startswith('hospital_'):
                    record_type = 'hospital'
                    unique_id = donor_id
                    name = hospital
                elif '_match' in organ_type:
                    record_type = 'match'
                    unique_id = f"match_{block_index}"
                    name = 'Match Record'
                else:
                    record_type = 'donor'
                    unique_id = donor_id
                    name = 'Donor Record'
                
                # Generate hashes for blockchain structure
                previous_hash = '0' if block_index == 1 else f"hash_{block_index-1}"
                current_hash = f"hash_{block_index}"
                
                # Insert blockchain record into database
                c.execute('''
                    INSERT INTO blockchain_records 
                    (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block_index,
                    unique_id,
                    previous_hash,
                    current_hash,
                    record_type,
                    name,
                    organ_type,
                    hospital,
                    timestamp
                ))
                
                print(f"Added record {unique_id} to database (block {block_index})")
                block_index += 1
                
            except Exception as e:
                print(f"Error processing record: {e}")
                continue
        
        # Process matches
        for match in matches:
            try:
                donor_name = match['donorName']
                patient_name = match['patientName']
                organ = match['encryptedOrgan']
                hospital = f"{match['donorHospital']}_to_{match['patientHospital']}"
                timestamp = match['date']
                
                record_type = 'match'
                unique_id = f"match_{block_index}"
                name = 'Match Record'
                
                # Generate hashes for blockchain structure
                previous_hash = '0' if block_index == 1 else f"hash_{block_index-1}"
                current_hash = f"hash_{block_index}"
                
                # Insert blockchain record into database
                c.execute('''
                    INSERT INTO blockchain_records 
                    (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block_index,
                    unique_id,
                    previous_hash,
                    current_hash,
                    record_type,
                    name,
                    organ,
                    hospital,
                    timestamp
                ))
                
                print(f"Added match record to database (block {block_index})")
                block_index += 1
                
            except Exception as e:
                print(f"Error processing match: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"Successfully updated {block_index-1} blockchain records in database!")
        return True
        
    except Exception as e:
        print(f"Error updating blockchain database: {e}")
        return False

if __name__ == "__main__":
    update_blockchain_database()