// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OrganChain {
    struct Hospital {
        string name;
        string email;
        string location;
        bool isRegistered;
    }
    
    struct Match {
        string donorName;
        uint256 donorAge;
        string donorHospital;
        string encryptedOrgan;
        string encryptedBloodType;
        string patientName;
        uint256 patientAge;
        string patientHospital;
        string date;
    }
    
    struct Record {
        string donorId;
        string organType;
        string hospital;
        string receiverId;
        uint256 timestamp;
    }
    
    mapping(address => Hospital) public hospitals;
    mapping(address => bool) public authorizedAdmins;
    Match[] public matches;
    Record[] public records;
    
    address public owner;
    
    event HospitalAdded(address indexed hospital, string name, string email, string location);
    event HospitalRemoved(address indexed hospital, string name);
    event AdminAdded(address indexed admin);
    event AdminRemoved(address indexed admin);
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
    event OrganRegistered(string donorId, string organType, string hospital, string receiverId);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }
    
    modifier onlyAdmin() {
        require(authorizedAdmins[msg.sender] || msg.sender == owner, "Only admins can perform this action");
        _;
    }
    
    modifier onlyRegisteredHospital() {
        require(hospitals[msg.sender].isRegistered, "Only registered hospitals can perform this action");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedAdmins[msg.sender] = true;
    }
    
    function addAdmin(address admin) public onlyOwner {
        authorizedAdmins[admin] = true;
        emit AdminAdded(admin);
    }
    
    function removeAdmin(address admin) public onlyOwner {
        authorizedAdmins[admin] = false;
        emit AdminRemoved(admin);
    }
    
    function addHospital(string memory name, string memory email, string memory location) public {
        hospitals[msg.sender] = Hospital(name, email, location, true);
        emit HospitalAdded(msg.sender, name, email, location);
    }
    
    function removeHospital() public onlyRegisteredHospital {
        Hospital memory h = hospitals[msg.sender];
        delete hospitals[msg.sender];
        emit HospitalRemoved(msg.sender, h.name);
    }
    
    function getHospital(address hospitalAddr) public view returns (string memory, string memory, string memory, bool) {
        Hospital memory h = hospitals[hospitalAddr];
        return (h.name, h.email, h.location, h.isRegistered);
    }
    
    function isHospitalRegistered(address hospitalAddr) public view returns (bool) {
        return hospitals[hospitalAddr].isRegistered;
    }
    
    function isAdmin(address addr) public view returns (bool) {
        return authorizedAdmins[addr] || addr == owner;
    }
    
    // Add match functions with full donor/patient details
    function addMatch(
        string memory donorName,
        uint256 donorAge,
        string memory donorHospital,
        string memory encryptedOrgan,
        string memory encryptedBloodType,
        string memory patientName,
        uint256 patientAge,
        string memory patientHospital,
        string memory date
    ) public {
        matches.push(Match(
            donorName,
            donorAge,
            donorHospital,
            encryptedOrgan,
            encryptedBloodType,
            patientName,
            patientAge,
            patientHospital,
            date
        ));
        
        // Create a detailed description for the event
        string memory details = string(abi.encodePacked(
            "Organ match created: Donor ", donorName, " (", toString(donorAge), " years) from ", donorHospital,
            " matched with Patient ", patientName, " (", toString(patientAge), " years) from ", patientHospital,
            " for ", getOrganName(encryptedOrgan), " transplant on ", date
        ));
        
        emit MatchAdded(
            matches.length - 1,
            donorName,
            donorAge,
            donorHospital,
            encryptedOrgan,
            encryptedBloodType,
            patientName,
            patientAge,
            patientHospital,
            date,
            details
        );
    }
    
    function getAllMatches() public view returns (Match[] memory) {
        return matches;
    }
    
    function getMatchesCount() public view returns (uint256) {
        return matches.length;
    }
    
    // Simple record function as per the example
    function addRecord(string memory donorId, string memory organType, string memory hospital, string memory receiverId) public {
        records.push(Record(donorId, organType, hospital, receiverId, block.timestamp));
        emit OrganRegistered(donorId, organType, hospital, receiverId);
    }

    function getAllRecords() public view returns (Record[] memory) {
        return records;
    }
    
    // Helper function to convert uint to string
    function toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
    
    // Helper function to get organ name (this would normally decrypt, but we'll just return a placeholder)
    function getOrganName(string memory encryptedOrgan) internal pure returns (string memory) {
        // In a real implementation, this would decrypt the organ name
        // For now, we'll just return a placeholder
        return "[Encrypted Organ]";
    }
}