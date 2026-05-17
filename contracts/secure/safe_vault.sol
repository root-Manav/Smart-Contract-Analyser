// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeVault {
    mapping(address => uint256) private balances;
    bool private locked;

    modifier noReentrant() {
        require(!locked, "No reentrancy");
        locked = true;
        _;
        locked = false;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amt) public noReentrant {
        require(balances[msg.sender] >= amt, "Insufficient");
        balances[msg.sender] -= amt;
        (bool ok,) = payable(msg.sender).call{value: amt}("");
        require(ok, "Transfer failed");
    }

    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }

    receive() external payable {}
}
