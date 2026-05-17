// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked2 {
    function batchSend(address payable[] memory targets, uint256 amount) public payable {
        for (uint256 i = 0; i < targets.length; i++) {
            targets[i].call{value: amount}("");
        }
    }

    receive() external payable {}
}
