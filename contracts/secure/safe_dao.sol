// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeDAO {
    struct Proposal {
        string   desc;
        uint256  yes;
        uint256  no;
        bool     executed;
        uint256  deadline;
    }

    Proposal[] public proposals;
    mapping(address => uint256) public tokens;
    address public admin;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function giveTokens(address a, uint256 amt) public onlyAdmin {
        tokens[a] = amt;
    }

    function propose(string memory desc, uint256 duration) public returns (uint256) {
        proposals.push(Proposal(desc, 0, 0, false, block.timestamp + duration));
        return proposals.length - 1;
    }

    function vote(uint256 id, bool support) public {
        Proposal storage p = proposals[id];
        require(block.timestamp < p.deadline, "Voting ended");
        require(tokens[msg.sender] > 0, "No tokens");
        if (support) p.yes += tokens[msg.sender];
        else         p.no  += tokens[msg.sender];
    }
}
