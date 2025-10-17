import sqlite3
import os

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def verify_hash_chaining():
    """Verify that the blockchain hash chaining is correct"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get all blockchain records ordered by block index
        c.execute("SELECT block_index, unique_id, previous_hash, current_hash, data_type, name FROM blockchain_records ORDER BY block_index ASC")
        records = c.fetchall()
        
        print(f"Verifying hash chaining for {len(records)} blockchain records...")
        print("Block # | Unique ID | Previous Hash | Current Hash | Match")
        print("-" * 85)
        
        previous_current_hash = '0'  # Genesis block should have previous_hash = '0'
        all_correct = True
        
        for i, record in enumerate(records):
            block_index, unique_id, previous_hash, current_hash, data_type, name = record
            
            # Check if previous_hash matches the previous block's current_hash
            if i == 0:
                # First block should have previous_hash = '0'
                match = previous_hash == '0'
                if not match:
                    print(f"ERROR: First block should have previous_hash = '0', but has '{previous_hash}'")
                    all_correct = False
            else:
                # Other blocks should have previous_hash = previous block's current_hash
                match = previous_hash == previous_current_hash
                if not match:
                    print(f"ERROR: Block {block_index} has previous_hash '{previous_hash[:20]}...' but should be '{previous_current_hash[:20]}...'")
                    all_correct = False
            
            # Display record info
            print(f"{block_index:7} | {unique_id[:12]:12} | {previous_hash[:15]:15} | {current_hash[:15]:15} | {'✓' if match else '✗'}")
            
            # Store current_hash for next iteration
            previous_current_hash = current_hash
        
        conn.close()
        
        if all_correct:
            print("\n✓ All hash chaining is correct!")
        else:
            print("\n✗ Hash chaining errors found!")
            
        return all_correct
        
    except Exception as e:
        print(f"Error verifying hash chaining: {e}")
        return False

if __name__ == "__main__":
    verify_hash_chaining()