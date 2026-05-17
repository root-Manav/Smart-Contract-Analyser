// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked5 {
    function multiTransfer(
        address payable a,
        address payable b,
        address payable c,
        uint256 amt
    ) public payable {
        a.call{value: amt}("");
        b.call{value: amt}("");
        c.call{value: amt}("");
    }

    receive() external payable {}
}
