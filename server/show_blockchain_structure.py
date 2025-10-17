import sqlite3
import os

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def show_blockchain_structure():
    """Show the complete blockchain structure with proper hash chaining"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get all blockchain records ordered by block index
        c.execute("""
            SELECT block_index, unique_id, data_type, name, organ, hospital, timestamp, previous_hash, current_hash 
            FROM blockchain_records 
            ORDER BY block_index ASC
        """)
        records = c.fetchall()
        
        print("BLOCKCHAIN STRUCTURE")
        print("=" * 100)
        print(f"{'Block':<6} | {'Type':<10} | {'Name/Hospital':<20} | {'Previous Hash':<15} | {'Current Hash':<15}")
        print("-" * 100)
        
        for record in records:
            block_index, unique_id, data_type, name, organ, hospital, timestamp, previous_hash, current_hash = record
            
            # Display record info
            display_name = name if data_type != 'hospital' else hospital
            print(f"{block_index:<6} | {data_type:<10} | {display_name[:20]:<20} | {previous_hash[:15]:<15} | {current_hash[:15]:<15}")
            
            # Show hash chaining for first few blocks
            if block_index <= 5 or block_index == len(records):
                print(f"       Hash chain: {previous_hash[:30]}... -> {current_hash[:30]}...")
                print()
        
        print(f"Total blocks in blockchain: {len(records)}")
        
        # Show statistics
        c.execute("SELECT data_type, COUNT(*) FROM blockchain_records GROUP BY data_type")
        stats = c.fetchall()
        print("\nRecord Types:")
        for record_type, count in stats:
            print(f"  {record_type.capitalize()}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error showing blockchain structure: {e}")

if __name__ == "__main__":
    show_blockchain_structure()