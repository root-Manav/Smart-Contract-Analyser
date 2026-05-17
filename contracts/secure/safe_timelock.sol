// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeTimelock {
    address public owner;
    uint256 public delay;
    mapping(bytes32 => uint256) public queued;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 _delay) {
        owner = msg.sender;
        delay = _delay;
    }

    function queue(bytes32 id) public onlyOwner {
        queued[id] = block.timestamp + delay;
    }

    function execute(
        bytes32 id,
        address target,
        uint256 value,
        bytes memory data
    ) public onlyOwner {
        require(queued[id] != 0, "Not queued");
        require(block.timestamp >= queued[id], "Too early");
        queued[id] = 0;
        (bool ok,) = target.call{value: value}(data);
        require(ok, "Execution failed");
    }

    receive() external payable {}
}
