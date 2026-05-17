// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed3 {
    mapping(address => uint256) public stakes;
    address public governance;

    constructor() {
        governance = msg.sender;
    }

    function stake() public payable {
        stakes[msg.sender] += msg.value;
    }

    function unstake() public {
        uint256 s = stakes[msg.sender];
        require(s > 0);
        (bool ok,) = msg.sender.call{value: s}("");
        require(ok);
        stakes[msg.sender] = 0;
    }

    function setGovernance(address g) public {
        governance = g;
    }

    function govWithdraw(address payable to) public {
        require(msg.sender == governance);
        to.call{value: address(this).balance}("");
    }

    receive() external payable {}
}
