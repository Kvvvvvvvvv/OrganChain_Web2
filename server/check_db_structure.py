import sqlite3
import os

# Use the database file in the same directory as this script
DB = os.path.join(os.path.dirname(__file__), "database.db")

def check_db_structure():
    """Check the structure of the database tables"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        # Get table names
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        print("Database Tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check blockchain_records table structure
        print("\nBlockchain Records Table Structure:")
        c.execute("PRAGMA table_info(blockchain_records)")
        columns = c.fetchall()
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        # Check number of records in blockchain_records
        c.execute("SELECT COUNT(*) FROM blockchain_records")
        count = c.fetchone()[0]
        print(f"\nTotal blockchain records: {count}")
        
        # Check donor table structure
        print("\nDonor Table Structure:")
        c.execute("PRAGMA table_info(donor)")
        columns = c.fetchall()
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        # Check patient table structure
        print("\nPatient Table Structure:")
        c.execute("PRAGMA table_info(patient)")
        columns = c.fetchall()
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database structure: {e}")

if __name__ == "__main__":
    check_db_structure()