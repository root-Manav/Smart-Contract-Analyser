// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeVoting {
    address public owner;
    mapping(address => bool) public hasVoted;
    mapping(uint256 => uint256) public votes;
    bool public active;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier isActive() {
        require(active, "Voting closed");
        _;
    }

    constructor() {
        owner = msg.sender;
        active = true;
    }

    function vote(uint256 id) public isActive {
        require(!hasVoted[msg.sender], "Already voted");
        hasVoted[msg.sender] = true;
        votes[id]++;
    }

    function close() public onlyOwner {
        active = false;
    }
}
