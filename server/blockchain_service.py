import json
import os
import hashlib
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

GANACHE_RPC = os.getenv("GANACHE_RPC", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# Fix the path to the contract JSON file
CONTRACT_JSON_PATH = os.getenv("CONTRACT_JSON_PATH", "./deployed_contract.json")

def is_connected():
    """Check if we can connect to the blockchain"""
    try:
        web3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
        return web3.is_connected()
    except:
        return False

# Initialize web3 connection
web3 = Web3(Web3.HTTPProvider(GANACHE_RPC))

# Check connection and warn if not connected
if not web3.is_connected():
    print("Warning: Cannot connect to Ganache at " + GANACHE_RPC)
    print("Blockchain features will be disabled")

acct = None
FROM_ADDRESS = None

# Only set up accounts if we're connected
if web3.is_connected():
    if PRIVATE_KEY:
        try:
            acct = web3.eth.account.from_key(PRIVATE_KEY)
            FROM_ADDRESS = acct.address
        except Exception as e:
            print(f"Warning: Could not create account from private key: {e}")
            # Fall back to using unlocked accounts
            if web3.eth.accounts:
                FROM_ADDRESS = web3.eth.accounts[0]
    else:
        # Use unlocked accounts if available
        if web3.eth.accounts:
            FROM_ADDRESS = web3.eth.accounts[0]

# Load contract ABI + address only if connected
contract = None
abi = None
contract_address = None

if web3.is_connected():
    try:
        with open(CONTRACT_JSON_PATH) as f:
            contract_json = json.load(f)
        abi = contract_json['abi']

        # try to find deployed address for current network id
        network_id = list(contract_json.get('networks', {}).keys())
        if len(network_id) > 0:
            # pick the first network entry deployed by truffle
            net = contract_json['networks'][network_id[0]]
            contract_address = net.get('address')
        else:
            # fallback: you can manually set address in .env or below
            contract_address = os.getenv("CONTRACT_ADDRESS", None)

        if not contract_address:
            print("Warning: Contract address not found in build file. Set CONTRACT_ADDRESS in .env or redeploy contract.")
        else:
            contract = web3.eth.contract(address=contract_address, abi=abi)
    except Exception as e:
        print(f"Warning: Could not load contract: {e}")
        contract = None

def encrypt_sensitive_data(data):
    """Encrypt sensitive data using SHA-256"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def add_match_to_chain(match):
    """
    match: dict with keys:
      donorName, donorAge, donorHospital, organ, bloodType,
      patientName, patientAge, patientHospital, date
    """
    # Return early if blockchain is not available
    if not web3.is_connected() or not contract or not FROM_ADDRESS:
        print("Blockchain not available, skipping match recording")
        return None
        
    try:
        # Encrypt sensitive fields
        encrypted_organ = encrypt_sensitive_data(match['organ'])
        encrypted_blood_type = encrypt_sensitive_data(match['bloodType'])
        
        tx = contract.functions.addMatch(
            match['donorName'],
            match['donorAge'],
            match['donorHospital'],
            encrypted_organ,
            encrypted_blood_type,
            match['patientName'],
            match['patientAge'],
            match['patientHospital'],
            match['date']
        ).build_transaction({
            'from': FROM_ADDRESS,
            'nonce': web3.eth.get_transaction_count(FROM_ADDRESS),
            'gas': 400000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })

        if PRIVATE_KEY and acct:
            signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        else:
            # If using unlocked accounts on Ganache, can send directly
            tx_hash = web3.eth.send_transaction(tx)

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    except Exception as e:
        print(f"Error adding match to blockchain: {e}")
        return None

def add_record_to_chain(donor_id, organ_type, hospital, receiver_id):
    """
    Add a simple record to the blockchain (as per the example)
    """
    # Return early if blockchain is not available
    if not web3.is_connected() or not contract or not FROM_ADDRESS:
        print("Blockchain not available, skipping record recording")
        return None
        
    try:
        tx = contract.functions.addRecord(
            donor_id, organ_type, hospital, receiver_id
        ).build_transaction({
            'from': FROM_ADDRESS,
            'nonce': web3.eth.get_transaction_count(FROM_ADDRESS),
            'gas': 200000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })

        if PRIVATE_KEY and acct:
            signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        else:
            # If using unlocked accounts on Ganache, can send directly
            tx_hash = web3.eth.send_transaction(tx)

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    except Exception as e:
        print(f"Error adding record to blockchain: {e}")
        return None

def get_all_matches():
    if not web3.is_connected() or not contract:
        return []
        
    try:
        matches = contract.functions.getAllMatches().call()
        # returns list of tuples corresponding to struct fields
        # convert to list of dicts
        fields = ['donorName', 'donorAge', 'donorHospital', 'encryptedOrgan', 'encryptedBloodType',
                  'patientName', 'patientAge', 'patientHospital', 'date']
        out = []
        for m in matches:
            out.append({fields[i]: m[i] for i in range(len(fields))})
        return out
    except Exception as e:
        print(f"Error getting matches from blockchain: {e}")
        return []

def get_all_records():
    if not web3.is_connected() or not contract:
        return []
        
    try:
        records = contract.functions.getAllRecords().call()
        # returns list of tuples corresponding to struct fields
        # convert to list of dicts
        fields = ['donorId', 'organType', 'hospital', 'receiverId', 'timestamp']
        out = []
        for r in records:
            out.append({fields[i]: r[i] for i in range(len(fields))})
        return out
    except Exception as e:
        print(f"Error getting records from blockchain: {e}")
        return []

def add_hospital_to_blockchain(name, email, location):
    """
    Add a hospital to the blockchain
    """
    # Return early if blockchain is not available
    if not web3.is_connected() or not contract or not FROM_ADDRESS:
        print("Blockchain not available, skipping hospital registration")
        return None
        
    try:
        tx = contract.functions.addHospital(name, email, location).build_transaction({
            'from': FROM_ADDRESS,
            'nonce': web3.eth.get_transaction_count(FROM_ADDRESS),
            'gas': 200000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })

        if PRIVATE_KEY and acct:
            signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        else:
            # If using unlocked accounts on Ganache, can send directly
            tx_hash = web3.eth.send_transaction(tx)

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    except Exception as e:
        print(f"Error adding hospital to blockchain: {e}")
        return None

def is_hospital_registered(hospital_address):
    """
    Check if a hospital is registered on the blockchain
    """
    if not web3.is_connected() or not contract:
        return False
        
    try:
        result = contract.functions.hospitals(hospital_address).call()
        # result is a tuple: (name, email, location, isRegistered)
        return result[3]  # isRegistered field
    except Exception as e:
        print(f"Error checking hospital registration: {e}")
        return False

def get_transaction_details(tx_hash):
    """
    Get detailed information about a transaction
    """
    if not web3.is_connected():
        return None
        
    try:
        tx = web3.eth.get_transaction(tx_hash)
        receipt = web3.eth.get_transaction_receipt(tx_hash)
        
        # Get block information
        block = web3.eth.get_block(receipt['blockNumber'])
        
        return {
            'transaction_hash': tx_hash,
            'from': tx['from'],
            'to': tx['to'],
            'gas': tx['gas'],
            'gas_price': tx['gasPrice'],
            'value': tx['value'],
            'block_number': receipt['blockNumber'],
            'block_timestamp': block['timestamp'],
            'gas_used': receipt['gasUsed'],
            'status': receipt['status'],
            'logs': receipt['logs']
        }
    except Exception as e:
        print(f"Error getting transaction details: {e}")
        return None