// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy4 {
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    function buy() public payable {
        shares[msg.sender] += msg.value;
        totalShares += msg.value;
    }

    function sell(uint256 amount) public {
        require(shares[msg.sender] >= amount, "Not enough shares");
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok);
        shares[msg.sender] -= amount;
        totalShares -= amount;
    }

    receive() external payable {}
}
