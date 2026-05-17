// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy2 {
    mapping(address => uint256) public credits;

    function donate(address to) public payable {
        credits[to] += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(credits[msg.sender] >= amount, "Insufficient");
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok);
        credits[msg.sender] -= amount;
    }

    receive() external payable {}
}
