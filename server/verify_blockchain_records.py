import sqlite3
import os

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def verify_blockchain_records():
    """Verify that the blockchain_records table has been properly populated"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get total count of blockchain records
        c.execute("SELECT COUNT(*) FROM blockchain_records")
        total_records = c.fetchone()[0]
        
        # Get count by data type
        c.execute("SELECT data_type, COUNT(*) FROM blockchain_records GROUP BY data_type")
        type_counts = c.fetchall()
        
        # Get first few records to verify structure
        c.execute("SELECT block_index, unique_id, data_type, name, hospital, timestamp FROM blockchain_records ORDER BY block_index LIMIT 10")
        sample_records = c.fetchall()
        
        print(f"Total blockchain records: {total_records}")
        print("\nRecords by type:")
        for record_type, count in type_counts:
            print(f"  {record_type}: {count}")
        
        print("\nFirst 10 records:")
        print("Block # | Unique ID | Type | Name | Hospital | Timestamp")
        print("-" * 80)
        for record in sample_records:
            print(f"{record[0]:7} | {record[1][:12]:12} | {record[2]:8} | {record[3][:15]:15} | {record[4][:20]:20} | {record[5][:19]}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error verifying blockchain records: {e}")
        return False

if __name__ == "__main__":
    verify_blockchain_records()