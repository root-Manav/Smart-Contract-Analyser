// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess3 {
    mapping(address => bool) public admins;

    function addAdmin(address a) public {
        admins[a] = true;
    }

    function removeAdmin(address a) public {
        admins[a] = false;
    }

    function adminAction(address payable to, uint256 amt) public {
        require(admins[msg.sender], "Not admin");
        to.transfer(amt);
    }

    receive() external payable {}
}
