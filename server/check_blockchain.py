import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from blockchain_service import is_connected, contract, web3

print("Blockchain Connection Status:")
print("Connected:", is_connected())
print("Web3 Provider:", web3.provider.endpoint_uri if web3.provider else "None")
print("Contract:", contract)

if contract:
    print("Contract Address:", contract.address)
    print("Contract ABI Length:", len(contract.abi))