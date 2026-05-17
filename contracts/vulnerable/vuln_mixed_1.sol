// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed1 {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0);
        (bool ok,) = msg.sender.call{value: bal}("");
        require(ok);
        balances[msg.sender] = 0;
    }

    function ownerWithdraw() public {
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}
