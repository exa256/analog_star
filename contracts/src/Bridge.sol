// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract Bridge is Ownable(msg.sender) {
    IERC20 public token;
    string public name;
    uint256 public depositNonce;
    uint256 public releaseNonce;
    mapping(uint256 => bool) public depositExecuted;
    mapping(uint256 => bool) public releaseExecuted;
    mapping(uint256 => uint256) public depositAmounts; // New mapping to store deposit amounts
    mapping(uint256 => address) public depositors; // New mapping to store depositor addresses

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
        depositAmounts[depositNonce] = amount; // Store the deposit amount
        depositors[depositNonce] = msg.sender; // Store the depositor's address
        depositNonce++;
        return amount;
    }

    function release(address to, uint256 amount) external onlyOwner returns (uint256) {
        require(token.transfer(to, amount), "Transfer failed");
        console.log("releasing");
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

    function getDepositAmount(uint256 nonce) external view returns (uint256) {
        return depositAmounts[nonce]; // New function to get deposit amount by nonce
    }

    function getDepositor(uint256 nonce) external view returns (address) {
        return depositors[nonce]; // New function to get depositor address by nonce
    }
}