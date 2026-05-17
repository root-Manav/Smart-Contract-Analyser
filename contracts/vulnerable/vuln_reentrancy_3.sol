// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy3 {
    mapping(address => uint256) private balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawAll() public {
        uint256 amt = balances[msg.sender];
        require(amt > 0, "Zero balance");
        (bool success,) = payable(msg.sender).call{value: amt}("");
        require(success);
        balances[msg.sender] = 0;
    }

    receive() external payable {}
}
