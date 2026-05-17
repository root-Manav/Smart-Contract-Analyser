// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeAuction {
    address public owner;
    address public topBidder;
    uint256 public topBid;
    bool public ended;
    mapping(address => uint256) public pending;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function bid() public payable {
        require(!ended, "Auction ended");
        require(msg.value > topBid, "Bid too low");
        if (topBidder != address(0)) {
            pending[topBidder] += topBid;
        }
        topBidder = msg.sender;
        topBid    = msg.value;
    }

    function withdraw() public {
        uint256 amt = pending[msg.sender];
        require(amt > 0, "Nothing to withdraw");
        pending[msg.sender] = 0;
        (bool ok,) = payable(msg.sender).call{value: amt}("");
        require(ok, "Transfer failed");
    }

    function endAuction() public onlyOwner {
        require(!ended, "Already ended");
        ended = true;
        (bool ok,) = owner.call{value: topBid}("");
        require(ok, "Transfer failed");
    }
}
