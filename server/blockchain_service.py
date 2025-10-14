import json
import os
import hashlib
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

GANACHE_RPC = os.getenv("GANACHE_RPC", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# Fix the path to the contract JSON file
CONTRACT_JSON_PATH = os.getenv("CONTRACT_JSON_PATH", "../build/contracts/OrganChain.json")

web3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
if not web3.is_connected():
    raise Exception("Cannot connect to Ganache at " + GANACHE_RPC)

acct = None
if PRIVATE_KEY:
    acct = web3.eth.account.from_key(PRIVATE_KEY)
    FROM_ADDRESS = acct.address
else:
    FROM_ADDRESS = web3.eth.accounts[0] if web3.eth.accounts else None

# load contract ABI + address
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
    raise Exception("Contract address not found in build file. Set CONTRACT_ADDRESS in .env or redeploy contract.")

contract = web3.eth.contract(address=contract_address, abi=abi)

def encrypt_sensitive_data(data):
    """Encrypt sensitive data using SHA-256"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def add_match_to_chain(match):
    """
    match: dict with keys:
      donorName, donorAge, donorHospital, organ, bloodType,
      patientName, patientAge, patientHospital, date
    """
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

    if PRIVATE_KEY:
        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    else:
        # If using unlocked accounts on Ganache, can send directly
        tx_hash = web3.eth.send_transaction(tx)

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def get_all_matches():
    matches = contract.functions.getAllMatches().call()
    # returns list of tuples corresponding to struct fields
    # convert to list of dicts
    fields = ['donorName', 'donorAge', 'donorHospital', 'encryptedOrgan', 'encryptedBloodType',
              'patientName', 'patientAge', 'patientHospital', 'date']
    out = []
    for m in matches:
        out.append({fields[i]: m[i] for i in range(len(fields))})
    return out

def add_hospital_to_blockchain(name, email, location):
    """
    Add a hospital to the blockchain
    """
    tx = contract.functions.addHospital(name, email, location).build_transaction({
        'from': FROM_ADDRESS,
        'nonce': web3.eth.get_transaction_count(FROM_ADDRESS),
        'gas': 200000,
        'gasPrice': web3.to_wei('20', 'gwei')
    })

    if PRIVATE_KEY:
        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    else:
        # If using unlocked accounts on Ganache, can send directly
        tx_hash = web3.eth.send_transaction(tx)

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def is_hospital_registered(hospital_address):
    """
    Check if a hospital is registered on the blockchain
    """
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