// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked4 {
    mapping(address => uint256) public rewards;

    function setReward(address user, uint256 amt) public {
        rewards[user] = amt;
    }

    function claimReward() public {
        uint256 amt = rewards[msg.sender];
        rewards[msg.sender] = 0;
        payable(msg.sender).call{value: amt}("");
    }

    receive() external payable {}
}
