// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeStaking {
    mapping(address => uint256) public staked;
    mapping(address => uint256) public since;
    uint256 public rate = 5;

    function stake() public payable {
        require(msg.value > 0, "Must stake ETH");
        staked[msg.sender] += msg.value;
        since[msg.sender]   = block.timestamp;
    }

    function unstake() public {
        uint256 s = staked[msg.sender];
        require(s > 0, "Nothing staked");
        uint256 dur    = block.timestamp - since[msg.sender];
        uint256 reward = (s * rate * dur) / (365 days * 100);
        staked[msg.sender] = 0;
        since[msg.sender]  = 0;
        (bool ok,) = payable(msg.sender).call{value: s + reward}("");
        require(ok, "Transfer failed");
    }
}
