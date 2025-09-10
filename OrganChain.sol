// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OrganChain {
    struct Hospital {
        string name;
        string email;
        string location;
    }
    mapping(address => Hospital) public hospitals;

    event HospitalAdded(address indexed hospital, string name);

    function addHospital(string memory name, string memory email, string memory location) public {
        hospitals[msg.sender] = Hospital(name, email, location);
        emit HospitalAdded(msg.sender, name);
    }

    function getHospital(address hospitalAddr) public view returns (string memory, string memory, string memory) {
        Hospital memory h = hospitals[hospitalAddr];
        return (h.name, h.email, h.location);
    }
}
