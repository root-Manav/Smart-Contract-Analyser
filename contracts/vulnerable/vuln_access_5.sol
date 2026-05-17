// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess5 {
    address public governance;
    uint256 public rewardRate;

    constructor() {
        governance = msg.sender;
        rewardRate = 10;
    }

    function setGovernance(address g) public {
        governance = g;
    }

    function setRewardRate(uint256 r) public {
        rewardRate = r;
    }

    function govWithdraw(address payable to) public {
        require(msg.sender == governance);
        (bool ok,) = to.call{value: address(this).balance}("");
        require(ok);
    }

    receive() external payable {}
}
