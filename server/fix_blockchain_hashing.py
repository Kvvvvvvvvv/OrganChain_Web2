import sqlite3
import os
import hashlib
from datetime import datetime

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def generate_hash(data):
    """Generate a SHA-256 hash for the given data"""
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

def fix_blockchain_hashing():
    """Fix the blockchain hashing to ensure proper chaining"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get all blockchain records ordered by block index
        c.execute("SELECT id, block_index, unique_id, data_type, name, organ, hospital, timestamp FROM blockchain_records ORDER BY block_index ASC")
        records = c.fetchall()
        
        print(f"Fixing hash chaining for {len(records)} blockchain records...")
        
        # Fix the hash chaining
        previous_hash = '0'  # Genesis block previous hash
        
        for i, record in enumerate(records):
            record_id, block_index, unique_id, data_type, name, organ, hospital, timestamp = record
            
            # Generate current hash based on record data
            data_to_hash = f"{unique_id}{data_type}{name}{organ}{hospital}{timestamp}"
            current_hash = generate_hash(data_to_hash)
            
            # Update the record with proper previous and current hashes
            c.execute('''
                UPDATE blockchain_records 
                SET previous_hash = ?, current_hash = ?
                WHERE id = ?
            ''', (previous_hash, current_hash, record_id))
            
            print(f"Fixed block {block_index}: prev_hash={previous_hash[:10]}..., curr_hash={current_hash[:10]}...")
            
            # Set previous_hash for next iteration
            previous_hash = current_hash
        
        conn.commit()
        conn.close()
        
        print("Successfully fixed blockchain hash chaining!")
        return True
        
    except Exception as e:
        print(f"Error fixing blockchain hashing: {e}")
        return False

if __name__ == "__main__":
    fix_blockchain_hashing()