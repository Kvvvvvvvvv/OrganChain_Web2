import requests
import json

print("=== OrganChain Blockchain Sync Demo ===\n")

# 1. Sync all existing database records to blockchain
print("1. Syncing all database records to blockchain...")
response = requests.get('http://127.0.0.1:5000/sync_to_blockchain')
if response.status_code == 200:
    print("✓ Sync completed successfully!")
    print(response.json())
else:
    print("✗ Sync failed!")
    print(response.json())

print("\n" + "="*50 + "\n")

# 2. View the blockchain
print("2. Viewing blockchain data...")
response = requests.get('http://127.0.0.1:5000/chain')
if response.status_code == 200:
    chain_data = response.json()
    print(f"✓ Retrieved blockchain with {len(chain_data)} blocks")
    
    # Show a sample of the data
    for i, block in enumerate(chain_data):
        print(f"\nBlock #{block['index']} (Timestamp: {block['timestamp']})")
        if block['data']:
            for entry in block['data']:
                if 'data_decrypted' in entry:
                    print(f"  Data: {entry['data_decrypted']}")
        else:
            print("  Data: Empty block")
        
        # Limit output for readability
        if i >= 2:
            print("  ... (showing first 3 blocks)")
            break
else:
    print("✗ Failed to retrieve blockchain data!")

print("\n" + "="*50 + "\n")

# 3. Test the blockchain viewer
print("3. Testing blockchain viewer API...")
response = requests.get('http://127.0.0.1:5001/api/chain')
if response.status_code == 200:
    viewer_data = response.json()
    print(f"✓ Blockchain viewer API working! Chain contains {len(viewer_data)} blocks")
else:
    print("✗ Blockchain viewer API not working!")

print("\n" + "="*50 + "\n")
print("Demo completed! All SQLite table values are now synchronized with the blockchain.")