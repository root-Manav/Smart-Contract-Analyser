// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed5 {
    address public owner;
    mapping(address => uint256) public credits;

    constructor() {
        owner = msg.sender;
    }

    function addCredit(address a, uint256 v) public {
        credits[a] = v;
    }

    function redeemCredit() public {
        uint256 val = credits[msg.sender];
        require(val > 0);
        (bool ok,) = msg.sender.call{value: val}("");
        require(ok);
        credits[msg.sender] = 0;
    }

    function transferOwnership(address o) public {
        owner = o;
    }

    receive() external payable {}
}
