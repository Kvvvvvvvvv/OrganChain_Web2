# OrganChain - Blockchain-Integrated Organ Donation Platform

A full-stack platform to manage organ donation chains across hospitals, with automatic donor–patient matching, transplant scheduling, and role-based access (Super Admin, Admin, Hospital).

This version includes **blockchain integration** for enhanced security and verification using Ethereum smart contracts.

## Features

- **Role-based access control**: Super Admin, Admin, and Hospital roles
- **Organ matching**: Automatic donor-patient matching based on organ compatibility, blood type, and location
- **Database management**: SQLite database for storing donors, patients, hospitals, and matches
- **Blockchain integration**: Ethereum smart contracts for hospital verification and authentication
- **MetaMask authentication**: Secure login using MetaMask wallet
- **Web3 frontend integration**: Direct blockchain interaction from the browser
- **Comprehensive blockchain API**: REST endpoints for blockchain data access
- **Dual data storage**: Both traditional database and blockchain storage for redundancy

## Tech Stack

- **Backend**: Python (Flask), SQLite via SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Blockchain**: Ethereum smart contracts (Solidity), Web3.js, Web3.py
- **Authentication**: MetaMask wallet integration
- **Deployment**: Docker, Vercel

## Project Structure

```
.
├── server/                 # Backend Flask application
│   ├── app.py             # Main application file
│   ├── blockchain_service.py # Blockchain integration service
│   ├── OrganChain.sol     # Solidity smart contract
│   ├── OrganChain_abi.json # Contract ABI
│   └── requirements.txt   # Python dependencies
├── client/                # Frontend templates and static files
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JavaScript, images
├── contracts/             # Solidity smart contracts
│   └── OrganChain.sol     # Main contract
├── migrations/            # Truffle migrations
│   └── 2_deploy_organchain.js # Deployment script
├── truffle-config.js      # Truffle configuration
├── deploy_contract.py     # Script to deploy smart contract
└── requirements.txt       # Project dependencies
```

## Blockchain Integration

This platform uses Ethereum smart contracts to verify hospital registrations and provide an additional layer of security.

### Smart Contract Features

- Hospital registration and verification
- Admin authorization management
- Event logging for all critical operations
- Immutable record of hospital information
- Organ match recording with detailed information
- Simple record storage for basic organ donation information
- Data encryption for sensitive information

### MetaMask Authentication

Hospitals can connect their MetaMask wallet for blockchain verification:
1. Click "Connect MetaMask" on the login page
2. Approve the connection in MetaMask
3. The wallet address will be used to verify hospital registration on the blockchain

### Web3 Frontend Integration

The platform includes a dedicated Web3 integration example that allows direct interaction with the blockchain:
1. Navigate to the "Web3 Example" page from the dashboard
2. Connect your MetaMask wallet
3. Add records directly to the blockchain
4. View blockchain records in real-time

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r server/requirements.txt
   npm install -g truffle
   ```

2. **Initialize the database**:
   ```bash
   python server/app.py
   ```

3. **Start a local Ethereum node** (for development):
   ```bash
   # Using Ganache CLI
   ganache-cli
   
   # Or using Hardhat
   npx hardhat node
   ```

4. **Compile and deploy the smart contract using Truffle**:
   ```bash
   # Compile the contract
   truffle compile
   
   # Deploy the contract
   truffle migrate --network development
   ```

5. **Or deploy using the custom deployment script**:
   ```bash
   python deploy_contract.py
   ```

6. **Configure environment variables**:
   Create a `.env` file in the project root with:
   ```env
   GANACHE_RPC=http://127.0.0.1:7545
   PRIVATE_KEY=0xb7704b524c611ae9888dcf3331e7bd334be5c0e084203cdbacf55bc6ac61cf79
   CONTRACT_JSON_PATH=./build/contracts/OrganChain.json
   ```

7. **Sync existing matches to blockchain** (optional):
   ```bash
   python server/sync_matches_to_blockchain.py
   ```

8. **Run the application**:
   ```bash
   python server/app.py
   ```

## API Endpoints

- `GET /api/matches` - Get all matches from blockchain
- `GET /api/records` - Get all simple records from blockchain
- `GET /api/transaction/<tx_hash>` - Get detailed information about a specific transaction
- `POST /api/matches` - Add a new match to blockchain

## Viewing Blockchain Data

To view detailed blockchain transaction information:
1. Access the "Blockchain Info" page from the dashboard
2. Or visit the API endpoints directly
3. Or check transactions directly in Ganache

See [HOW_TO_VIEW_BLOCKCHAIN_DATA.md](HOW_TO_VIEW_BLOCKCHAIN_DATA.md) for detailed instructions.

## Default Accounts

- **Admin**: admin@gmail.com / 1234

## Security

- Passwords are stored securely
- MetaMask integration provides wallet-based authentication
- Blockchain verification ensures hospital authenticity
- Role-based access control limits system access
- Sensitive data is encrypted before storing on the blockchain

## Deployment

The application can be deployed using Docker or traditional hosting services. For blockchain features, you'll need to connect to an Ethereum network (mainnet, testnet, or local node).