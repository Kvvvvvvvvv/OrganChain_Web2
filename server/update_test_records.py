import sqlite3
import os

# Connect to the database
DB = os.path.join(os.path.dirname(__file__), "database.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Update test donor
c.execute("UPDATE donor SET medical_document_path = 'test_medical_document.pdf', status = 'Not Matched' WHERE name = 'John Doe'")

# Update test patient
c.execute("UPDATE patient SET medical_document_path = 'test_medical_document.pdf', status = 'Not Matched' WHERE name = 'Jane Smith'")

conn.commit()
conn.close()

print("Test records updated successfully!")