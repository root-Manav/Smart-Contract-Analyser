// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy7 {
    mapping(address => uint256) public pending;

    function deposit() public payable {
        pending[msg.sender] += msg.value;
    }

    function claim() public {
        uint256 amount = pending[msg.sender];
        require(amount > 0, "Nothing pending");
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        pending[msg.sender] = 0;
    }

    receive() external payable {}
}
