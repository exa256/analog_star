// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract Bridge is Ownable(msg.sender) {
    IERC20 public token;
    string public name;
    uint256 public depositNonce;
    uint256 public releaseNonce;
    mapping(uint256 => bool) public depositExecuted;
    mapping(uint256 => bool) public releaseExecuted;

    constructor(address _token, string memory _name) {
        token = IERC20(_token);
        name = _name;
        transferOwnership(msg.sender); // Set the deployer as the owner
        depositNonce = 0;
        releaseNonce = 0;
    }

    function deposit(uint256 amount) external returns (uint256) {
        require(token.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        depositExecuted[depositNonce] = true;
        depositNonce++;
        return amount;
    }

    function release(address to, uint256 amount) external onlyOwner returns (uint256) {
        require(token.transfer(to, amount), "Transfer failed");
        releaseExecuted[releaseNonce] = true;
        releaseNonce++;
        return amount;
    }

    function getReserve() external view returns (uint256) {
        return token.balanceOf(address(this));
    }

    function getCurrentDepositStatus() external view returns (uint256, bool) {
        return (depositNonce, depositExecuted[depositNonce]);
    }

    function getCurrentReleaseStatus() external view returns (uint256, bool) {
        return (releaseNonce, releaseExecuted[releaseNonce]);
    }
}