// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked3 {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function withdraw(address payable to, uint256 amt) public {
        require(msg.sender == owner);
        to.call{value: amt}("");
    }

    receive() external payable {}
}
