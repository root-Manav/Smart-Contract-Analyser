// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked1 {
    function sendReward(address payable to, uint256 amount) public payable {
        to.call{value: amount}("");
    }

    receive() external payable {}
}
