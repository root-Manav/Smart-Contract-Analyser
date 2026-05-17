// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeRegistry {
    address public owner;
    mapping(string => address) private reg;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function register(string memory name, address addr) public onlyOwner {
        require(addr != address(0), "Zero address");
        require(reg[name] == address(0), "Name taken");
        reg[name] = addr;
    }

    function resolve(string memory name) public view returns (address) {
        return reg[name];
    }
}
