#!/usr/bin/env python3
"""
Database Restoration Script
Restores the organ donation database with default data
"""

import sqlite3
import uuid
import datetime

DB = "database.db"

def restore_database():
    """Restore database with default data"""
    print("🔄 Starting database restoration...")
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        # Clear existing data
        print("🧹 Clearing existing data...")
        c.execute("DELETE FROM match_record")
        c.execute("DELETE FROM donor")
        c.execute("DELETE FROM patient")
        c.execute("DELETE FROM hospital")
        c.execute("DELETE FROM admin")
        
        # Reset auto-increment counters
        c.execute("DELETE FROM sqlite_sequence")
        
        # Insert default admin
        print("👤 Adding default admin...")
        c.execute("INSERT INTO admin (email, password) VALUES (?, ?)", 
                 ('admin@gmail.com', '1234'))
        
        # Insert sample hospitals
        print("🏥 Adding sample hospitals...")
        hospitals = [
            ('City General Hospital', 'citygeneral@hospital.com', 'New York, NY', 'hospital123'),
            ('Metro Medical Center', 'metro@medical.com', 'Los Angeles, CA', 'metro456'),
            ('Regional Health Center', 'regional@health.com', 'Chicago, IL', 'regional789'),
            ('University Hospital', 'university@hospital.com', 'Boston, MA', 'university101'),
            ('Community Medical', 'community@medical.com', 'Houston, TX', 'community202')
        ]
        
        for hospital in hospitals:
            c.execute("INSERT INTO hospital (name, email, location, password) VALUES (?, ?, ?, ?)", 
                     hospital)
        
        # Get hospital IDs for reference
        c.execute("SELECT id, name FROM hospital")
        hospitals_data = c.fetchall()
        print(f"✅ Added {len(hospitals_data)} hospitals")
        
        # Insert sample donors
        print("🩸 Adding sample donors...")
        donors = [
            (1, 'John Smith', 35, 'Male', 'O+', 'Heart', 'Not Matched'),
            (1, 'Sarah Johnson', 28, 'Female', 'A+', 'Kidney', 'Not Matched'),
            (2, 'Michael Brown', 42, 'Male', 'B+', 'Liver', 'Not Matched'),
            (2, 'Emily Davis', 31, 'Female', 'AB+', 'Lung', 'Not Matched'),
            (3, 'David Wilson', 45, 'Male', 'O-', 'Heart', 'Not Matched'),
            (3, 'Lisa Anderson', 29, 'Female', 'A-', 'Kidney', 'Not Matched'),
            (4, 'Robert Taylor', 38, 'Male', 'B-', 'Liver', 'Not Matched'),
            (4, 'Jennifer Martinez', 33, 'Female', 'AB-', 'Lung', 'Not Matched'),
            (5, 'Christopher Lee', 41, 'Male', 'O+', 'Heart', 'Not Matched'),
            (5, 'Amanda Garcia', 27, 'Female', 'A+', 'Kidney', 'Not Matched')
        ]
        
        for donor in donors:
            unique_id = str(uuid.uuid4())
            registration_date = datetime.datetime.now().isoformat()
            c.execute("""INSERT INTO donor (unique_id, hospital_id, name, age, gender, 
                     blood_type, organ, status, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (unique_id, donor[0], donor[1], donor[2], donor[3], donor[4], donor[5], donor[6], registration_date))
        
        print(f"✅ Added {len(donors)} donors")
        
        # Insert sample patients
        print("🏥 Adding sample patients...")
        patients = [
            (1, 'Alice Thompson', 55, 'Female', 'O+', 'Heart', 'Not Matched'),
            (1, 'Bob Rodriguez', 48, 'Male', 'A+', 'Kidney', 'Not Matched'),
            (2, 'Carol White', 62, 'Female', 'B+', 'Liver', 'Not Matched'),
            (2, 'Daniel Harris', 39, 'Male', 'AB+', 'Lung', 'Not Matched'),
            (3, 'Eva Clark', 51, 'Female', 'O-', 'Heart', 'Not Matched'),
            (3, 'Frank Lewis', 44, 'Male', 'A-', 'Kidney', 'Not Matched'),
            (4, 'Grace Walker', 58, 'Female', 'B-', 'Liver', 'Not Matched'),
            (4, 'Henry Hall', 36, 'Male', 'AB-', 'Lung', 'Not Matched'),
            (5, 'Ivy Young', 49, 'Female', 'O+', 'Heart', 'Not Matched'),
            (5, 'Jack Allen', 43, 'Male', 'A+', 'Kidney', 'Not Matched')
        ]
        
        for patient in patients:
            unique_id = str(uuid.uuid4())
            registration_date = datetime.datetime.now().isoformat()
            c.execute("""INSERT INTO patient (unique_id, hospital_id, name, age, gender, 
                     blood_type, organ, status, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (unique_id, patient[0], patient[1], patient[2], patient[3], patient[4], patient[5], patient[6], registration_date))
        
        print(f"✅ Added {len(patients)} patients")
        
        # Create some sample matches
        print("🔗 Creating sample matches...")
        matches = [
            (1, 1, 1, 1, 'Heart', 'O+'),  # John Smith (donor) -> Alice Thompson (patient)
            (2, 2, 2, 2, 'Kidney', 'A+'), # Sarah Johnson (donor) -> Bob Rodriguez (patient)
            (3, 3, 3, 3, 'Liver', 'B+'),  # Michael Brown (donor) -> Carol White (patient)
        ]
        
        for match in matches:
            match_date = datetime.datetime.now().isoformat()
            c.execute("""INSERT INTO match_record (donor_id, patient_id, donor_hospital_id, 
                     patient_hospital_id, organ, blood_type, match_date) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (match[0], match[1], match[2], match[3], match[4], match[5], match_date))
            
            # Update donor and patient status to matched
            c.execute("UPDATE donor SET status='Matched' WHERE id=?", (match[0],))
            c.execute("UPDATE patient SET status='Matched' WHERE id=?", (match[1],))
        
        print(f"✅ Created {len(matches)} matches")
        
        # Commit all changes
        conn.commit()
        print("💾 Database changes committed successfully!")
        
        # Display summary
        print("\n📊 Database Restoration Summary:")
        c.execute("SELECT COUNT(*) FROM admin")
        admin_count = c.fetchone()[0]
        print(f"👤 Admins: {admin_count}")
        
        c.execute("SELECT COUNT(*) FROM hospital")
        hospital_count = c.fetchone()[0]
        print(f"🏥 Hospitals: {hospital_count}")
        
        c.execute("SELECT COUNT(*) FROM donor")
        donor_count = c.fetchone()[0]
        print(f"🩸 Donors: {donor_count}")
        
        c.execute("SELECT COUNT(*) FROM patient")
        patient_count = c.fetchone()[0]
        print(f"🏥 Patients: {patient_count}")
        
        c.execute("SELECT COUNT(*) FROM match_record")
        match_count = c.fetchone()[0]
        print(f"🔗 Matches: {match_count}")
        
        print("\n🎉 Database restoration completed successfully!")
        print("\n🔑 Default Login Credentials:")
        print("   Admin: admin@gmail.com / 1234")
        print("   Hospital: Use any hospital email with their password")
        
    except Exception as e:
        print(f"❌ Error during restoration: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    success = restore_database()
    if success:
        print("\n✅ Database is ready to use!")
    else:
        print("\n❌ Database restoration failed!")
