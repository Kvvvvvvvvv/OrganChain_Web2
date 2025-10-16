# How to View Blockchain Transaction Details in Ganache

This guide explains how to view detailed information about organ matches stored on the blockchain using Ganache.

## Prerequisites

1. Make sure Ganache is running on http://127.0.0.1:7545
2. Ensure the Flask application is running on http://127.0.0.1:5000
3. Have at least one match recorded in the system

## Steps to View Transaction Details

### 1. Access the Blockchain Information Page

1. Open your web browser and navigate to http://127.0.0.1:5000/blockchain_info
2. You will see a list of matches stored on the blockchain with details such as:
   - Donor name and age
   - Patient name and age
   - Hospital information
   - Match date
   - Encrypted organ and blood type information

### 2. Find the Transaction in Ganache

1. Open Ganache
2. Click on the "Transactions" tab
3. Look for transactions with high gas usage (typically > 300,000 gas) as these are likely to be the match creation transactions
4. Alternatively, you can check the transaction hash from the API response:
   - Visit http://127.0.0.1:5000/api/matches
   - Note the transaction details

### 3. View Transaction Details

1. Click on a transaction to view its details
2. In the transaction details panel, scroll down to the "Logs" or "Event Logs" section
3. You will see the `MatchAdded` event with the following information:
   - Donor name and age
   - Patient name and age
   - Hospital names
   - Match date
   - A detailed description field that summarizes the match

### 4. Understanding the Event Data

The `MatchAdded` event now includes:
- Indexed fields for efficient searching (matchId)
- Human-readable details in the `details` field
- All relevant information about the donor and patient
- Encrypted sensitive data (organ type and blood type)

## Example Event Log

When you view a transaction's event logs, you'll see something like:

```
MatchAdded(
  matchId: 0
  donorName: "John Doe"
  donorAge: 35
  donorHospital: "City General Hospital"
  encryptedOrgan: "574e763ee3834061a25debb72992d76cf9e40af868dcbea8d5f6c2adf166c0ac"
  encryptedBloodType: "4aa8d4a10f941836b0c764d54421edf48c76cafb4b17ffe338b0340194515d89"
  patientName: "Jane Smith"
  patientAge: 45
  patientHospital: "University Medical Center"
  date: "2025-10-12"
  details: "Organ match created: Donor John Doe (35 years) from City General Hospital matched with Patient Jane Smith (45 years) from University Medical Center for [Encrypted Organ] transplant on 2025-10-12"
)
```

## Web3 Frontend Integration

The platform also includes a Web3 frontend integration example that allows direct interaction with the blockchain:

1. Navigate to http://127.0.0.1:5000/web3_example
2. Connect your MetaMask wallet
3. Add records directly to the blockchain
4. View blockchain records in real-time

This demonstrates how the platform could be extended to allow hospitals to interact directly with the blockchain without going through the backend.

## API Access

You can also access blockchain data programmatically through the REST API:

- `GET /api/matches` - Retrieve all matches from the blockchain
- `GET /api/records` - Retrieve all simple records from the blockchain
- `GET /api/transaction/<tx_hash>` - Get detailed information about a specific transaction

## Benefits of This Approach

1. **Transparency**: All stakeholders can verify that matches are recorded fairly
2. **Immutability**: Once recorded, match details cannot be altered
3. **Privacy**: Sensitive medical information is encrypted
4. **Auditability**: All transactions are traceable and verifiable
5. **User-Friendly**: Event logs provide clear, human-readable information
6. **Flexibility**: Multiple ways to interact with blockchain data

## Troubleshooting

If you don't see any transactions:
1. Make sure you've created at least one match through the web interface
2. Run the matching algorithm by visiting http://127.0.0.1:5000/matches
3. Check that the blockchain service is properly connected to Ganache
4. Verify that the smart contract is deployed correctly

If you encounter connection issues:
1. Ensure Ganache is running on the correct port (7545)
2. Check that the RPC endpoint in the configuration matches Ganache's endpoint
3. Verify that the contract address is correctly set in the backend