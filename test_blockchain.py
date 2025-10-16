import requests
import json

# Test data to add to the blockchain
data = {
    "donor": "D101",
    "organ": "Kidney",
    "hospital": "Apollo",
    "receiver": "R305"
}

# Make a POST request to add the record to the blockchain
response = requests.post('http://127.0.0.1:5000/add_to_chain', 
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps(data))

print("Response from server:")
print(response.json())

# Check the blockchain
response = requests.get('http://127.0.0.1:5000/chain')
print("\nCurrent blockchain:")
print(json.dumps(response.json(), indent=2))