// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy1 {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "Nothing to withdraw");
        (bool sent,) = msg.sender.call{value: bal}("");
        require(sent, "Failed");
        balances[msg.sender] = 0;
    }

    receive() external payable {}
}
