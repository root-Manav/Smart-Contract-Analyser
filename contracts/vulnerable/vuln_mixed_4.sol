// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed4 {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawHalf() public {
        uint256 half = balances[msg.sender] / 2;
        require(half > 0);
        (bool ok,) = msg.sender.call{value: half}("");
        require(ok);
        balances[msg.sender] -= half;
    }

    function sendTo(address payable to, uint256 amt) public {
        to.call{value: amt}("");
    }

    receive() external payable {}
}
