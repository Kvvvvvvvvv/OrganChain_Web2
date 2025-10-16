import sqlite3
import os

# Connect to the database
DB = os.path.join(os.path.dirname(__file__), "database.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Check for test donor
print("=== TEST DONOR ===")
c.execute("SELECT * FROM donor WHERE name = 'John Doe'")
donor = c.fetchone()
if donor:
    print(donor)
else:
    print("No test donor found")

# Check for test patient
print("\n=== TEST PATIENT ===")
c.execute("SELECT * FROM patient WHERE name = 'Jane Smith'")
patient = c.fetchone()
if patient:
    print(patient)
else:
    print("No test patient found")

conn.close()