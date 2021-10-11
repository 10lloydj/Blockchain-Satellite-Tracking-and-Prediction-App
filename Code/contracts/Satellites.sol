//SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.5.0;

//pragma experimental ABIEncoderV2;
contract Satellites {
 
    // used to assert the contract has been deployed 
    string public name = "Satellites Smart Contract";

    // data storage for the satellite data
    struct SatInfo {
        uint id;
        string name;
        string longitude;
        string latitude;
        string elevation;
        string azimuth;
        string timestamp;
    }

    mapping (uint => SatInfo) public sat;

    // sets or adds a record the smart contract in memory storage
    function set( uint _address, uint id_, string memory name_ , string memory longitude_, string memory latitude_, string memory elevation_, string memory azimuth_,
    string memory timestamp_) public {
        
        sat[_address].id = id_;
        sat[_address].name = name_;
        sat[_address].longitude = longitude_;
        sat[_address].latitude = latitude_;
        sat[_address].elevation = elevation_;
        sat[_address].azimuth = azimuth_;
        sat[_address].timestamp = timestamp_;
    }
    // retrieves a struct of type SatInfo
    function get()  view public  returns (uint , string memory, string memory, 
    string memory, string memory, string memory, string memory) {
        // within python it returns an array
        return ( sat[0].id, sat[0].name, sat[0].longitude,sat[0].latitude,sat[0].elevation,sat[0].azimuth,sat[0].timestamp);
    }
}
