#!/usr/bin/env python3
"""
Script to check available accounts in Ganache
"""

import json
from web3 import Web3

def check_accounts():
    # Connect to local Ethereum node (Ganache)
    ganache_url = "http://127.0.0.1:7545"
    web3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not web3.is_connected():
        print("Error: Could not connect to Ethereum node at", ganache_url)
        return
    
    print("Connected to Ethereum node")
    
    # Get accounts
    accounts = web3.eth.accounts
    print(f"Available accounts ({len(accounts)}):")
    for i, account in enumerate(accounts):
        balance = web3.eth.get_balance(account)
        balance_eth = web3.from_wei(balance, 'ether')
        print(f"  {i}: {account} ({balance_eth} ETH)")
    
    # Check the deployed contract
    try:
        with open('server/deployed_contract.json', 'r') as f:
            contract_info = json.load(f)
        
        contract_address = contract_info['address']
        print(f"\nDeployed contract address: {contract_address}")
        
        # Check if contract exists by getting its code
        code = web3.eth.get_code(contract_address)
        if code != b'':
            print("Contract is deployed and accessible")
        else:
            print("Contract is not deployed or not accessible")
    except FileNotFoundError:
        print("\nNo deployed contract found")

if __name__ == "__main__":
    check_accounts()