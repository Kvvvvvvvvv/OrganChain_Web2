import sqlite3
import os
import re

# Connect to the database
DB = os.path.join(os.path.dirname(__file__), "database.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Function to extract filename from full path
def extract_filename(full_path):
    if full_path is None:
        return None
    # Extract just the filename part from the full path
    filename = os.path.basename(full_path)
    return filename

# Update donor records
c.execute("SELECT id, medical_document_path FROM donor WHERE medical_document_path IS NOT NULL")
donor_records = c.fetchall()

for donor_id, full_path in donor_records:
    filename = extract_filename(full_path)
    if filename != full_path:  # Only update if we're changing something
        c.execute("UPDATE donor SET medical_document_path = ? WHERE id = ?", (filename, donor_id))
        print(f"Updated donor {donor_id}: {full_path} -> {filename}")

# Update patient records
c.execute("SELECT id, medical_document_path FROM patient WHERE medical_document_path IS NOT NULL")
patient_records = c.fetchall()

for patient_id, full_path in patient_records:
    filename = extract_filename(full_path)
    if filename != full_path:  # Only update if we're changing something
        c.execute("UPDATE patient SET medical_document_path = ? WHERE id = ?", (filename, patient_id))
        print(f"Updated patient {patient_id}: {full_path} -> {filename}")

conn.commit()
conn.close()

print("Database updated successfully!")