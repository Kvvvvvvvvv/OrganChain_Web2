import sqlite3
import os
import sys
from datetime import datetime

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def add_test_blockchain_records():
    """Add test blockchain records to demonstrate the correct structure"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Clear existing blockchain records
        c.execute("DELETE FROM blockchain_records")
        print("Cleared existing blockchain records")
        
        # Add test records with proper blockchain structure
        test_records = [
            {
                'block_index': 1,
                'unique_id': 'hospital_1',
                'previous_hash': '0',  # Genesis block
                'current_hash': '7105d6d0969019e13946...',  # Example hash
                'data_type': 'hospital',
                'name': 'City Hospital',
                'organ': 'hospital_registration',
                'hospital': 'City Hospital',
                'timestamp': datetime.now().isoformat()
            },
            {
                'block_index': 2,
                'unique_id': 'patient_19',
                'previous_hash': '7105d6d0969019e13946...',  # Previous block hash
                'current_hash': 'f4434c1ee5d1c8067dfe...',  # Current block hash
                'data_type': 'patient',
                'name': 'John Doe',
                'organ': 'Kidney',
                'hospital': 'City Hospital',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        for record in test_records:
            c.execute('''
                INSERT INTO blockchain_records 
                (block_index, unique_id, previous_hash, current_hash, data_type, name, organ, hospital, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['block_index'],
                record['unique_id'],
                record['previous_hash'],
                record['current_hash'],
                record['data_type'],
                record['name'],
                record['organ'],
                record['hospital'],
                record['timestamp']
            ))
            
            print(f"Added test record: {record['unique_id']} (block {record['block_index']})")
        
        conn.commit()
        conn.close()
        
        print("Successfully added test blockchain records!")
        return True
        
    except Exception as e:
        print(f"Error adding test blockchain records: {e}")
        return False

if __name__ == "__main__":
    add_test_blockchain_records()