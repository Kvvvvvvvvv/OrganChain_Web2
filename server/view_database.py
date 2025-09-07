import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('database.db')

print("=== ORGAN DONOR DATABASE VIEWER ===\n")

# Function to display table data
def show_table(table_name, title):
    print(f"--- {title} ---")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        if df.empty:
            print("No data found.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print(f"Error reading {table_name}: {e}")
    print("\n")

# Show all tables
try:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Available tables:", [table[0] for table in tables])
    print("\n")
except Exception as e:
    print(f"Error getting tables: {e}")

# Display each table
show_table('hospital', 'HOSPITALS')
show_table('donor', 'DONORS')
show_table('patient', 'PATIENTS')
show_table('match_record', 'MATCH RECORDS')
show_table('admin', 'ADMINS')

# Close connection
conn.close()

print("Database viewing complete!")
