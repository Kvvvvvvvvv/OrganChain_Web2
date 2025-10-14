#!/usr/bin/env python3
"""
Script to sync existing database matches to the blockchain
"""

import sqlite3
import os
import sys

# Add the server directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from blockchain_service import add_match_to_chain

DB = os.path.join(os.path.dirname(__file__), "database.db")

def sync_matches_to_blockchain():
    """Sync existing database matches to blockchain"""
    print("🔄 Starting sync of database matches to blockchain...")
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    try:
        # Get all match records with hospital names
        c.execute('''
            SELECT 
                d.name as donor_name,
                d.organ as donor_organ,
                d.blood_type as donor_blood_type,
                hd.name as donor_hospital_name,
                p.name as patient_name,
                p.organ as patient_organ,
                p.blood_type as patient_blood_type,
                hp.name as patient_hospital_name,
                mr.match_date
            FROM match_record mr
            JOIN donor d ON mr.donor_id = d.id
            JOIN patient p ON mr.patient_id = p.id
            JOIN hospital hd ON mr.donor_hospital_id = hd.id
            JOIN hospital hp ON mr.patient_hospital_id = hp.id
            ORDER BY mr.match_date
        ''')
        
        matches = c.fetchall()
        print(f"Found {len(matches)} matches in database")
        
        success_count = 0
        error_count = 0
        
        for match in matches:
            donor_name, donor_organ, donor_blood_type, donor_hospital, \
            patient_name, patient_organ, patient_blood_type, patient_hospital, \
            match_date = match
            
            # Create match object for blockchain
            match_data = {
                'donorName': donor_name,
                'donorOrgan': donor_organ,
                'donorBloodType': donor_blood_type,
                'donorHospital': donor_hospital,
                'patientName': patient_name,
                'patientOrgan': patient_organ,
                'patientBloodType': patient_blood_type,
                'patientHospital': patient_hospital,
                'date': match_date.split(' ')[0]  # Get just the date part
            }
            
            try:
                # Add to blockchain
                receipt = add_match_to_chain(match_data)
                print(f"✅ Added match {donor_name} -> {patient_name} to blockchain. TX: {receipt.transactionHash.hex()}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to add match {donor_name} -> {patient_name} to blockchain: {e}")
                error_count += 1
        
        print(f"\n📊 Sync Summary:")
        print(f"   Successful: {success_count}")
        print(f"   Errors: {error_count}")
        print(f"   Total: {len(matches)}")
        
        if error_count == 0:
            print("\n🎉 All matches synced to blockchain successfully!")
        else:
            print(f"\n⚠️  Sync completed with {error_count} errors.")
            
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    success = sync_matches_to_blockchain()
    if success:
        print("\n✅ Blockchain sync completed!")
    else:
        print("\n❌ Blockchain sync failed!")
        sys.exit(1)