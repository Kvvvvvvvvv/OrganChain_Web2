import sqlite3
import os
import hashlib
from datetime import datetime

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def generate_hash(data):
    """Generate a SHA-256 hash for the given data"""
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

def verify_blockchain_integrity():
    """Verify the integrity of the blockchain"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get all blockchain records ordered by block index
        c.execute("SELECT block_index, unique_id, previous_hash, current_hash, data_type, name FROM blockchain_records ORDER BY block_index ASC")
        records = c.fetchall()
        
        previous_current_hash = '0'  # Genesis block should have previous_hash = '0'
        all_correct = True
        
        for i, record in enumerate(records):
            block_index, unique_id, previous_hash, current_hash, data_type, name = record
            
            # Check if previous_hash matches the previous block's current_hash
            if i == 0:
                # First block should have previous_hash = '0'
                if previous_hash != '0':
                    print(f"ERROR: First block should have previous_hash = '0', but has '{previous_hash}'")
                    all_correct = False
            else:
                # Other blocks should have previous_hash = previous block's current_hash
                if previous_hash != previous_current_hash:
                    print(f"ERROR: Block {block_index} has previous_hash '{previous_hash[:20]}...' but should be '{previous_current_hash[:20]}...'")
                    all_correct = False
            
            # Store current_hash for next iteration
            previous_current_hash = current_hash
        
        conn.close()
        
        return all_correct
        
    except Exception as e:
        print(f"Error verifying blockchain integrity: {e}")
        return False

def rebuild_blockchain():
    """Rebuild the entire blockchain with proper hash chaining"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get all blockchain records ordered by block index
        c.execute("SELECT id, block_index, unique_id, data_type, name, organ, hospital, timestamp FROM blockchain_records ORDER BY block_index ASC")
        records = c.fetchall()
        
        print(f"Rebuilding blockchain with {len(records)} records...")
        
        # Rebuild the hash chaining
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
            
            # Set previous_hash for next iteration
            previous_hash = current_hash
        
        conn.commit()
        conn.close()
        
        print("Successfully rebuilt blockchain with proper hash chaining!")
        return True
        
    except Exception as e:
        print(f"Error rebuilding blockchain: {e}")
        return False

def maintain_blockchain():
    """Main function to maintain blockchain integrity"""
    print("Blockchain Maintenance Script")
    print("=" * 30)
    
    # Verify current integrity
    print("Verifying blockchain integrity...")
    if verify_blockchain_integrity():
        print("✓ Blockchain integrity verified - all hash chains are correct!")
    else:
        print("✗ Blockchain integrity issues found!")
        print("Rebuilding blockchain...")
        if rebuild_blockchain():
            print("✓ Blockchain successfully rebuilt!")
            # Verify again after rebuild
            if verify_blockchain_integrity():
                print("✓ Blockchain integrity verified after rebuild!")
            else:
                print("✗ Blockchain still has integrity issues after rebuild!")
        else:
            print("✗ Failed to rebuild blockchain!")
    
    # Show blockchain statistics
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM blockchain_records")
        total_records = c.fetchone()[0]
        
        c.execute("SELECT data_type, COUNT(*) FROM blockchain_records GROUP BY data_type")
        type_counts = c.fetchall()
        
        print(f"\nBlockchain Statistics:")
        print(f"Total blocks: {total_records}")
        for record_type, count in type_counts:
            print(f"  {record_type.capitalize()}: {count}")
        
        conn.close()
    except Exception as e:
        print(f"Error getting blockchain statistics: {e}")

if __name__ == "__main__":
    maintain_blockchain()