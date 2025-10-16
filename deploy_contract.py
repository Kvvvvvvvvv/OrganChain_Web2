#!/usr/bin/env python3
"""
Script to deploy the OrganChain smart contract to a local Ethereum network
"""

import json
import os
from web3 import Web3

def deploy_contract():
    # Connect to local Ethereum node (Ganache)
    ganache_url = "http://127.0.0.1:7545"
    web3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not web3.is_connected():
        print("Error: Could not connect to Ethereum node at", ganache_url)
        return
    
    print("Connected to Ethereum node")
    
    # Get the first account as deployer
    deployer_account = web3.eth.accounts[0]
    print("Deployer account:", deployer_account)
    
    # Read the compiled contract
    build_path = os.path.join(os.path.dirname(__file__), "build", "contracts", "OrganChain.json")
    
    if not os.path.exists(build_path):
        print("Error: Contract build file not found at", build_path)
        print("Please compile the contract first using 'truffle compile'")
        return
    
    with open(build_path) as f:
        contract_json = json.load(f)
    
    abi = contract_json['abi']
    bytecode = contract_json['bytecode']
    
    # Create contract instance
    OrganChain = web3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Deploy the contract
    print("Deploying contract...")
    tx_hash = OrganChain.constructor().transact({'from': deployer_account, 'gas': 4000000})
    
    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    
    print("Contract deployed successfully!")
    print("Contract address:", contract_address)
    print("Transaction hash:", tx_hash.hex())
    print("Gas used:", tx_receipt.gasUsed)
    
    # Save contract address to a file for the backend
    contract_info = {
        "address": contract_address,
        "abi": abi,
        "transaction_hash": tx_hash.hex(),
        "block_number": tx_receipt.blockNumber
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "server", "deployed_contract.json")
    with open(output_path, 'w') as f:
        json.dump(contract_info, f, indent=2)
    
    print("Contract information saved to", output_path)
    
    # Test the contract by adding a simple record
    print("Testing contract by adding a simple record...")
    
    # Create contract instance with deployed address
    contract = web3.eth.contract(address=contract_address, abi=abi)
    
    # Add a test record
    test_tx_hash = contract.functions.addRecord(
        "TEST_DONOR_001",
        "Kidney",
        "Test Hospital",
        "TEST_PATIENT_001"
    ).transact({'from': deployer_account, 'gas': 200000})
    
    test_tx_receipt = web3.eth.wait_for_transaction_receipt(test_tx_hash)
    print("Test record added successfully!")
    print("Test transaction hash:", test_tx_hash.hex())
    
    # Retrieve the record
    records = contract.functions.getAllRecords().call()
    print("Retrieved records:", len(records))
    if records:
        print("First record:", records[0])
        
        # Also test getting all matches
        matches = contract.functions.getAllMatches().call()
        print("Retrieved matches:", len(matches))

if __name__ == "__main__":
    deploy_contract()