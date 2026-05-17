// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy5 {
    mapping(address => uint256) public pool;

    function addLiquidity() public payable {
        pool[msg.sender] += msg.value;
    }

    function removeLiquidity(uint256 amount) public {
        require(pool[msg.sender] >= amount);
        (bool sent,) = msg.sender.call{value: amount}("");
        require(sent);
        pool[msg.sender] -= amount;
    }

    receive() external payable {}
}
