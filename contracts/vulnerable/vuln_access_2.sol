// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess2 {
    address public admin;
    mapping(address => uint256) public balances;

    constructor() {
        admin = msg.sender;
    }

    function setAdmin(address a) public {
        admin = a;
    }

    function adminDrain(address payable to) public {
        require(msg.sender == admin);
        to.transfer(address(this).balance);
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    receive() external payable {}
}
