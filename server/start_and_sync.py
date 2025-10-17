import os
import sys
import subprocess
import time

def start_ganache_and_sync():
    """Start Ganache and sync blockchain records"""
    
    print("Starting Ganache blockchain...")
    
    # Try to start Ganache
    try:
        # Check if Ganache is already running
        import requests
        try:
            response = requests.get("http://127.0.0.1:7545")
            print("Ganache is already running!")
        except:
            print("Ganache is not running. Please start Ganache on port 7545")
            print("You can download Ganache from: https://www.trufflesuite.com/ganache")
            return
    
        # Wait a moment for Ganache to fully start
        time.sleep(2)
        
        # Run the blockchain sync script
        print("Running blockchain sync...")
        sync_result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), "sync_blockchain_records.py")
        ], capture_output=True, text=True)
        
        if sync_result.returncode == 0:
            print("Blockchain sync completed successfully!")
            print(sync_result.stdout)
        else:
            print("Blockchain sync failed!")
            print(sync_result.stderr)
            
        # Update database with blockchain records
        print("Updating database with blockchain records...")
        update_result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), "update_blockchain_database.py")
        ], capture_output=True, text=True)
        
        if update_result.returncode == 0:
            print("Database update completed successfully!")
            print(update_result.stdout)
        else:
            print("Database update failed!")
            print(update_result.stderr)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_ganache_and_sync()