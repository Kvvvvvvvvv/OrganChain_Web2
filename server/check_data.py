import sqlite3
import os

# Connect to the database
DB = os.path.join(os.path.dirname(__file__), "database.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Check donor data
print("=== DONOR DATA ===")
c.execute("SELECT * FROM donor LIMIT 5")
donors = c.fetchall()
for donor in donors:
    print(donor)

print("\n=== PATIENT DATA ===")
c.execute("SELECT * FROM patient LIMIT 5")
patients = c.fetchall()
for patient in patients:
    print(patient)

conn.close()