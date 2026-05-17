// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess4 {
    address payable public owner;
    uint256 public fee;

    constructor() {
        owner = payable(msg.sender);
        fee = 100;
    }

    function setFee(uint256 f) public {
        fee = f;
    }

    function setOwner(address payable o) public {
        owner = o;
    }

    function collectFees() public {
        require(msg.sender == owner);
        owner.transfer(address(this).balance);
    }

    receive() external payable {}
}
