// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeEscrow {
    address public buyer;
    address public seller;
    address public arbiter;
    uint256 public amount;
    bool public released;
    bool public refunded;

    modifier onlyArbiter() {
        require(msg.sender == arbiter, "Not arbiter");
        _;
    }

    constructor(address _seller, address _arbiter) payable {
        buyer   = msg.sender;
        seller  = _seller;
        arbiter = _arbiter;
        amount  = msg.value;
    }

    function release() public onlyArbiter {
        require(!released && !refunded, "Already settled");
        released = true;
        (bool ok,) = seller.call{value: amount}("");
        require(ok, "Transfer failed");
    }

    function refund() public onlyArbiter {
        require(!released && !refunded, "Already settled");
        refunded = true;
        (bool ok,) = buyer.call{value: amount}("");
        require(ok, "Transfer failed");
    }
}
