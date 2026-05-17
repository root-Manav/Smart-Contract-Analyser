// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeToken {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 supply) {
        owner = msg.sender;
        totalSupply = supply;
        balanceOf[msg.sender] = supply;
    }

    function transfer(address to, uint256 amt) public returns (bool) {
        require(to != address(0), "Zero address");
        require(balanceOf[msg.sender] >= amt, "Insufficient");
        balanceOf[msg.sender] -= amt;
        balanceOf[to] += amt;
        return true;
    }

    function mint(uint256 amt) public onlyOwner {
        totalSupply += amt;
        balanceOf[owner] += amt;
    }
}
