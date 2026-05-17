// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess1 {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function changeOwner(address newOwner) public {
        owner = newOwner;
    }

    function withdraw() public {
        require(msg.sender == owner);
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}
