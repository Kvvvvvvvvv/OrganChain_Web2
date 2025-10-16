#!/usr/bin/env python3
"""
Test script to verify blockchain integration
"""

import os
import sys
import json

# Add the server directory to the path so we can import blockchain_service
sys.path.append(os.path.join(os.path.dirname(__file__)))

from blockchain_service import (
    add_match_to_chain, 
    add_record_to_chain, 
    get_all_matches, 
    get_all_records, 
    add_hospital_to_blockchain,
    is_hospital_registered,
    is_connected
)

def test_blockchain_connection():
    """Test if we can connect to the blockchain"""
    print("Testing blockchain connection...")
    if is_connected():
        print("✓ Connected to blockchain")
        return True
    else:
        print("✗ Cannot connect to blockchain")
        return False

def test_add_hospital():
    """Test adding a hospital to the blockchain"""
    print("\nTesting hospital registration...")
    try:
        receipt = add_hospital_to_blockchain("Test Hospital", "test@hospital.com", "Test City")
        if receipt:
            print("✓ Hospital registered successfully")
            print(f"  Transaction hash: {receipt.transactionHash.hex()}")
            return True
        else:
            print("✗ Failed to register hospital")
            return False
    except Exception as e:
        print(f"✗ Error registering hospital: {e}")
        return False

def test_add_record():
    """Test adding a simple record to the blockchain"""
    print("\nTesting record addition...")
    try:
        receipt = add_record_to_chain("DONOR_001", "Kidney", "Test Hospital", "PATIENT_001")
        if receipt:
            print("✓ Record added successfully")
            print(f"  Transaction hash: {receipt.transactionHash.hex()}")
            return True
        else:
            print("✗ Failed to add record")
            return False
    except Exception as e:
        print(f"✗ Error adding record: {e}")
        return False

def test_add_match():
    """Test adding a match to the blockchain"""
    print("\nTesting match addition...")
    try:
        match_data = {
            'donorName': "John Doe",
            'donorAge': 35,
            'donorHospital': "Test Hospital",
            'organ': "Kidney",
            'bloodType': "O+",
            'patientName': "Jane Smith",
            'patientAge': 45,
            'patientHospital': "Test Hospital",
            'date': "2025-10-15"
        }
        
        receipt = add_match_to_chain(match_data)
        if receipt:
            print("✓ Match added successfully")
            print(f"  Transaction hash: {receipt.transactionHash.hex()}")
            return True
        else:
            print("✗ Failed to add match")
            return False
    except Exception as e:
        print(f"✗ Error adding match: {e}")
        return False

def test_get_records():
    """Test retrieving records from the blockchain"""
    print("\nTesting record retrieval...")
    try:
        records = get_all_records()
        print(f"✓ Retrieved {len(records)} records")
        for i, record in enumerate(records[:3]):  # Show first 3 records
            print(f"  Record {i+1}: {record}")
        return True
    except Exception as e:
        print(f"✗ Error retrieving records: {e}")
        return False

def test_get_matches():
    """Test retrieving matches from the blockchain"""
    print("\nTesting match retrieval...")
    try:
        matches = get_all_matches()
        print(f"✓ Retrieved {len(matches)} matches")
        for i, match in enumerate(matches[:3]):  # Show first 3 matches
            print(f"  Match {i+1}: {match}")
        return True
    except Exception as e:
        print(f"✗ Error retrieving matches: {e}")
        return False

def main():
    """Run all tests"""
    print("OrganChain Blockchain Integration Tests")
    print("=" * 40)
    
    # Test connection
    if not test_blockchain_connection():
        print("\nCannot proceed with tests without blockchain connection")
        return
    
    # Run all tests
    tests = [
        test_add_hospital,
        test_add_record,
        test_add_match,
        test_get_records,
        test_get_matches
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()