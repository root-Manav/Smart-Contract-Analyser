// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeMultiSig {
    address[] public owners;
    uint256 public required;
    mapping(address => bool) public isOwner;

    struct Tx {
        address to;
        uint256 value;
        bool    done;
        uint256 confirms;
    }

    Tx[] public txs;
    mapping(uint256 => mapping(address => bool)) public confirmed;

    modifier onlyOwner() {
        require(isOwner[msg.sender], "Not owner");
        _;
    }

    constructor(address[] memory _owners, uint256 _req) {
        require(_owners.length >= _req, "Invalid required");
        required = _req;
        for (uint256 i = 0; i < _owners.length; i++) {
            isOwner[_owners[i]] = true;
            owners.push(_owners[i]);
        }
    }

    function submit(address to, uint256 val) public onlyOwner returns (uint256) {
        txs.push(Tx(to, val, false, 0));
        return txs.length - 1;
    }

    function confirm(uint256 id) public onlyOwner {
        require(!confirmed[id][msg.sender], "Already confirmed");
        confirmed[id][msg.sender] = true;
        txs[id].confirms++;
    }

    function execute(uint256 id) public onlyOwner {
        Tx storage t = txs[id];
        require(t.confirms >= required, "Not enough confirms");
        require(!t.done, "Already executed");
        t.done = true;
        (bool ok,) = t.to.call{value: t.value}("");
        require(ok, "Execution failed");
    }

    receive() external payable {}
}
