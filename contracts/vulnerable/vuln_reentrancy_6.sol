// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy6 {
    mapping(address => uint256) public stakes;

    function stake() public payable {
        stakes[msg.sender] += msg.value;
    }

    function unstake() public {
        uint256 s = stakes[msg.sender];
        require(s > 0);
        (bool ok,) = payable(msg.sender).call{value: s}("");
        require(ok, "Transfer failed");
        stakes[msg.sender] = 0;
    }

    receive() external payable {}
}
