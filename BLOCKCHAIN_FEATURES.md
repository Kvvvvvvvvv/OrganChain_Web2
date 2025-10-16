# Blockchain Features in OrganChain

This document describes the blockchain integration features implemented in the OrganChain platform.

## Overview

OrganChain leverages blockchain technology to provide transparency, immutability, and security for organ donation records and matching processes. All critical operations are recorded on the Ethereum blockchain using a custom smart contract.

## Smart Contract

The core of the blockchain integration is the `OrganChain.sol` smart contract, which provides the following functionality:

### Data Structures

1. **Hospital** - Stores hospital registration information
2. **Match** - Records detailed organ match information
3. **Record** - Simple organ donation records (as per the example)

### Key Functions

- `addHospital()` - Register a hospital on the blockchain
- `addMatch()` - Record a donor-patient match with full details
- `addRecord()` - Add a simple organ record (as per the example)
- `getAllMatches()` - Retrieve all recorded matches
- `getAllRecords()` - Retrieve all simple records

### Events

- `HospitalAdded` - Emitted when a hospital is registered
- `MatchAdded` - Emitted when a match is recorded with detailed information
- `OrganRegistered` - Emitted when a simple record is added

## Backend Integration

The Flask backend integrates with the blockchain through the `blockchain_service.py` module:

### Key Functions

- `add_match_to_chain()` - Records matches on the blockchain
- `add_record_to_chain()` - Adds simple records to the blockchain
- `add_hospital_to_blockchain()` - Registers hospitals on the blockchain
- `get_all_matches()` - Retrieves all matches from the blockchain
- `get_all_records()` - Retrieves all simple records from the blockchain

### Automatic Recording

When matches are created through the platform's matching algorithm, they are automatically recorded on the blockchain. Similarly, when donors or patients are added, simple records are created on the blockchain.

## Frontend Integration

### MetaMask Authentication

The platform supports MetaMask wallet authentication for hospitals. When logging in as a hospital, users can connect their MetaMask wallet to verify their identity on the blockchain.

### Web3 Example

A dedicated Web3 integration example (`web3_example.html`) demonstrates how to:

1. Connect to MetaMask
2. Add records directly to the blockchain
3. View blockchain records

This example shows how the platform could be extended to allow direct blockchain interactions from the frontend.

## API Endpoints

The platform provides REST API endpoints to access blockchain data:

- `GET /api/matches` - Retrieve all matches from the blockchain
- `GET /api/records` - Retrieve all simple records from the blockchain
- `GET /api/transaction/<tx_hash>` - Get detailed information about a specific transaction

## Security and Privacy

### Data Encryption

Sensitive information such as organ types and blood types are encrypted before being stored on the blockchain using SHA-256 hashing.

### Access Control

The smart contract implements role-based access control:
- Only the contract owner can add/remove administrators
- Only administrators can perform critical operations
- Hospitals can only perform operations after registration

## Deployment

The smart contract is deployed using Truffle to a local Ganache network. The deployment process:

1. Compiles the Solidity contract
2. Migrates the contract to the blockchain
3. Generates ABI and contract address information

## Viewing Blockchain Data

Blockchain data can be viewed in several ways:

1. **Platform Interface** - Through the "Blockchain Info" section
2. **API Endpoints** - Using the REST API
3. **Ganache UI** - Directly in the Ganache transaction logs
4. **Web3 Example** - Through the dedicated Web3 integration page

## Benefits

1. **Transparency** - All operations are publicly verifiable
2. **Immutability** - Records cannot be altered or deleted
3. **Security** - Sensitive data is encrypted
4. **Auditability** - All transactions can be traced and verified
5. **Decentralization** - No single point of failure