import sqlite3
import json
import os
import sys
from cryptography.fernet import Fernet

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the blockchain service
from blockchain_layer import SimpleBlockchain, load_key, generate_key

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def migrate_blockchain_data():
    try:
        # Load the blockchain data from JSON file
        blockchain_json_path = os.path.join(os.path.dirname(__file__), '..', 'blockchain.json')
        if not os.path.exists(blockchain_json_path):
            print("Blockchain JSON file not found. Skipping migration.")
            return
            
        with open(blockchain_json_path, 'r') as f:
            chain = json.load(f)
        
        # Initialize blockchain
        if not os.path.exists("secret.key"):
            key = generate_key()
        else:
            key = load_key()
            
        blockchain = SimpleBlockchain(key)
        
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get donor and patient data from database for additional info
        donor_dict = {}
        try:
            c.execute("SELECT unique_id, name, organ, hospital_id FROM donor")
            for row in c.fetchall():
                donor_dict[row[0]] = {
                    'name': row[1],
                    'organ': row[2],
                    'hospital_id': row[3]
                }
        except:
            pass
        
        # Get patient data
        patient_dict = {}
        try:
            c.execute("SELECT unique_id, name, organ, hospital_id FROM patient")
            for row in c.fetchall():
                patient_dict[row[0]] = {
                    'name': row[1],
                    'organ': row[2],
                    'hospital_id': row[3]
                }
        except:
            pass
        
        # Get hospital data
        hospital_dict = {}
        try:
            c.execute("SELECT id, name FROM hospital")
            for row in c.fetchall():
                hospital_dict[row[0]] = row[1]
        except:
            pass
        
        # Prepare blockchain records for migration
        blockchain_records = []
        
        for block in chain:
            # Skip genesis block (index 1) as it has no data
            if block['index'] == 1:
                continue
                
            for entry in block['data']:
                try:
                    decrypted = blockchain.decrypt_data(entry['data_encrypted'])
                    
                    # Determine record type
                    record_type = 'unknown'
                    unique_id = 'N/A'
                    name = 'N/A'
                    organ = 'N/A'
                    hospital = 'N/A'
                    
                    if 'donor_id' in decrypted:
                        donor_id = decrypted['donor_id']
                        if donor_id.startswith('patient_'):
                            record_type = 'patient'
                            unique_id = donor_id
                            # Get patient name from database
                            patient_id = donor_id.replace('patient_', '')
                            if patient_id in patient_dict:
                                name = patient_dict[patient_id]['name']
                                organ = patient_dict[patient_id]['organ']
                                hospital_id = patient_dict[patient_id]['hospital_id']
                                if hospital_id in hospital_dict:
                                    hospital = hospital_dict[hospital_id]
                        elif donor_id.startswith('hospital_'):
                            record_type = 'hospital'
                            unique_id = donor_id
                            hospital = decrypted.get('hospital', 'N/A')
                            name = hospital
                        else:
                            record_type = 'donor'
                            unique_id = donor_id
                            # Get donor name from database
                            if donor_id in donor_dict:
                                name = donor_dict[donor_id]['name']
                                organ = donor_dict[donor_id]['organ']
                                hospital_id = donor_dict[donor_id]['hospital_id']
                                if hospital_id in hospital_dict:
                                    hospital = hospital_dict[hospital_id]
                    elif 'organ_type' in decrypted and '_match' in decrypted['organ_type']:
                        record_type = 'match'
                        unique_id = f"match_{block['index']}"
                        name = "Match Record"
                        organ = decrypted.get('organ_type', 'N/A')
                        hospital = decrypted.get('hospital', 'N/A')
                    else:
                        record_type = 'unknown'
                        unique_id = 'N/A'
                        name = 'Unknown'
                        organ = 'N/A'
                        hospital = 'N/A'
                    
                    # Calculate current block hash
                    current_hash = blockchain.hash_block(block)
                    
                    record_data = {
                        'block_index': block['index'],
                        'unique_id': unique_id,
                        'type': record_type,
                        'name': name,
                        'organ': organ,
                        'timestamp': block['timestamp'],
                        'hospital': hospital,
                        'previous_hash': block['previous_hash'],
                        'current_hash': current_hash
                    }
                    
                    blockchain_records.append(record_data)
                except Exception as e:
                    # If decryption fails, skip this entry
                    continue
        
        # Insert records into database
        for record in blockchain_records:
            try:
                c.execute('''
                    INSERT INTO blockchain_records 
                    (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record['block_index'],
                    record['unique_id'],
                    record['previous_hash'],
                    record['current_hash'],
                    record['type'],
                    record['name'],
                    record['organ'],
                    record['hospital'],
                    record['timestamp']
                ))
            except sqlite3.IntegrityError:
                # Skip if record already exists
                pass
        
        conn.commit()
        conn.close()
        
        print(f"Successfully migrated {len(blockchain_records)} blockchain records to database!")
        
    except Exception as e:
        print(f"Error migrating blockchain data: {str(e)}")

if __name__ == "__main__":
    migrate_blockchain_data()