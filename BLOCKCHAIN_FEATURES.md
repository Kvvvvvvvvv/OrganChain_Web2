# Blockchain Features in Organ Donation Platform

This document explains the blockchain integration features implemented in the organ donation platform.

## Overview

The platform uses Ethereum blockchain technology (via Ganache for development) to provide:
1. Immutable record of organ matches
2. Transparency in the matching process
3. Privacy through encryption of sensitive data
4. Auditability of all transactions

## Smart Contract

The platform uses a Solidity smart contract (`OrganChain.sol`) with the following features:

### Data Structures

1. **Hospital**: Stores hospital information
2. **Match**: Records donor-patient matches with full details

### Events

The contract emits detailed events for transparency:

1. **HospitalAdded**: When a hospital is registered
2. **HospitalRemoved**: When a hospital is deregistered
3. **MatchAdded**: When a donor-patient match is created

The `MatchAdded` event includes:
- Donor name, age, and hospital
- Patient name, age, and hospital
- Encrypted organ type and blood type
- Match date
- A human-readable details field

### Security Features

1. **Data Encryption**: Organ type and blood type are encrypted using SHA-256 before being stored on the blockchain
2. **Access Control**: Only authorized admins can perform certain actions
3. **Immutability**: Once recorded, data cannot be altered

## Integration with Web Application

### Backend (Flask)

The Flask application integrates with the blockchain through:

1. **blockchain_service.py**: Handles all Web3 interactions
2. **Automatic Matching**: When the matching algorithm runs, matches are automatically recorded on the blockchain
3. **API Endpoints**:
   - `/api/matches`: Get all matches from the blockchain
   - `/api/transaction/<tx_hash>`: Get detailed transaction information

### Frontend

1. **Blockchain Info Page**: Displays all matches recorded on the blockchain
2. **Dashboard Links**: Easy access to blockchain information from both admin and hospital dashboards

## How to View Blockchain Data

### In the Web Application

1. Navigate to the "Blockchain Info" page from any dashboard
2. View all matches with donor and patient details
3. See that sensitive data is encrypted

### In Ganache

1. Open Ganache and go to the "Transactions" tab
2. Find transactions related to match creation (high gas usage)
3. Click on a transaction to view details
4. In the "Event Logs" section, see the detailed match information

## Data Privacy

To protect patient privacy:
1. Organ types are encrypted before being stored on the blockchain
2. Blood types are encrypted before being stored on the blockchain
3. Only non-sensitive information (names, ages, hospitals) is stored in plain text
4. All data is immutable once recorded

## Benefits

1. **Transparency**: All stakeholders can verify that matches are recorded fairly
2. **Immutability**: Once recorded, match details cannot be altered
3. **Privacy**: Sensitive medical information is encrypted
4. **Auditability**: All transactions are traceable and verifiable
5. **User-Friendly**: Event logs provide clear, human-readable information

## Technical Details

### Encryption

Sensitive data is encrypted using SHA-256:
```python
def encrypt_sensitive_data(data):
    """Encrypt sensitive data using SHA-256"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
```

### Event Structure

The `MatchAdded` event provides comprehensive information:
```
event MatchAdded(
    uint256 indexed matchId,
    string donorName,
    uint256 donorAge,
    string donorHospital,
    string encryptedOrgan,
    string encryptedBloodType,
    string patientName,
    uint256 patientAge,
    string patientHospital,
    string date,
    string details
);
```

### Human-Readable Details

Each event includes a `details` field that summarizes the match in plain English:
```
"Organ match created: Donor John Doe (35 years) from City General Hospital matched with Patient Jane Smith (45 years) from University Medical Center for [Encrypted Organ] transplant on 2025-10-12"
```

## Troubleshooting

If blockchain features aren't working:

1. Ensure Ganache is running on the correct port (7545)
2. Verify the contract is deployed (check `truffle migrate` output)
3. Confirm the `.env` file has correct configuration
4. Check that the Flask app can connect to Ganache (look for connection errors in the console)

## Future Enhancements

Possible future improvements:
1. Integration with MetaMask for hospital authentication
2. Real-time event listening for immediate UI updates
3. More sophisticated encryption (e.g., AES instead of SHA-256)
4. Additional events for other operations (donor/patient registration, etc.)