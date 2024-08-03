// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Dex} from "../src/Dex.sol";

contract Token is ERC20 {
    address private _owner;

    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
        _owner = msg.sender;
        _mint(msg.sender, 1000 ether);
    }

    modifier onlyOwner() {
        require(msg.sender == _owner, "MintableERC20: caller is not the owner");
        _;
    }

    function mint(address account, uint256 amount) public onlyOwner {
        _mint(account, amount);
    }
}