// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed2 {
    address public admin;
    mapping(address => uint256) public deposits;

    constructor() {
        admin = msg.sender;
    }

    function deposit() public payable {
        deposits[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 amt = deposits[msg.sender];
        require(amt > 0);
        (bool ok,) = payable(msg.sender).call{value: amt}("");
        require(ok);
        deposits[msg.sender] = 0;
    }

    function changeAdmin(address a) public {
        admin = a;
    }

    function adminDrain(address payable to) public {
        require(msg.sender == admin);
        to.call{value: address(this).balance}("");
    }

    receive() external payable {}
}
