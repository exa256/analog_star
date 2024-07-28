// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/console.sol";
import {Test, console} from "forge-std/Test.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Bridge} from "../src/Bridge.sol";

contract MintableERC20 is ERC20 {
    address private _owner;

    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
        _owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == _owner, "MintableERC20: caller is not the owner");
        _;
    }

    function mint(address account, uint256 amount) public onlyOwner {
        _mint(account, amount);
    }
}

contract BridgeTest is Test {
    Bridge public bridge;
    MintableERC20 public token;
    address public user = address(0x123);

    function setUp() public {
        token = new MintableERC20("Token", "TKN");

        // Mint tokens for the user and the Bridge contract
        token.mint(user, 1000 ether);
        token.mint(address(this), 1000 ether);

        // Deploy the Bridge contract
        bridge = new Bridge(address(token), "TestBridge");

        // Transfer some tokens to the Bridge contract to provide liquidity
        token.transfer(address(bridge), 500 ether);
    }

    function testDeposit() public {
        uint256 amount = 100 ether;

        // Approve the Bridge contract to spend tokens on behalf of the user
        vm.startPrank(user);
        console.log("User %s approves Bridge to spend %s tokens", user, amount);
        token.approve(address(bridge), amount);

        // Log balances before the deposit
        console.log("User Token balance before deposit: %s", token.balanceOf(user));
        console.log("Bridge Token balance before deposit: %s", token.balanceOf(address(bridge)));

        // Perform the deposit
        console.log("User %s performs deposit with %s tokens", user, amount);
        uint256 depositedAmount = bridge.deposit(amount);
        vm.stopPrank();

        // Check balances
        console.log("Checking balances after deposit");
        console.log("User Token balance: %s", token.balanceOf(user));
        console.log("Bridge Token balance: %s", token.balanceOf(address(bridge)));

        assertEq(token.balanceOf(user), 900 ether);
        assertEq(token.balanceOf(address(bridge)), 600 ether);
        assertEq(depositedAmount, amount);

        // Check depositNonce and depositExecuted
        console.log("Checking depositNonce and depositExecuted");
        console.log("Bridge depositNonce: %s", bridge.depositNonce());
        console.log("Bridge depositExecuted(0): %s", bridge.depositExecuted(0));
        assertEq(bridge.depositNonce(), 1);
        assertTrue(bridge.depositExecuted(0));
    }

    function testRelease() public {
        uint256 amount = 100 ether;

        // Log balances before the release
        console.log("User Token balance before release: %s", token.balanceOf(user));
        console.log("Bridge Token balance before release: %s", token.balanceOf(address(bridge)));

        // Perform the release
        console.log("Owner performs release to user %s with %s tokens", user, amount);
        uint256 releasedAmount = bridge.release(user, amount);

        // Check balances
        console.log("Checking balances after release");
        console.log("User Token balance: %s", token.balanceOf(user));
        console.log("Bridge Token balance: %s", token.balanceOf(address(bridge)));

        assertEq(token.balanceOf(user), 1100 ether);
        assertEq(token.balanceOf(address(bridge)), 400 ether);
        assertEq(releasedAmount, amount);

        // Check releaseNonce and releaseExecuted
        console.log("Checking releaseNonce and releaseExecuted");
        console.log("Bridge releaseNonce: %s", bridge.releaseNonce());
        console.log("Bridge releaseExecuted(0): %s", bridge.releaseExecuted(0));
        assertEq(bridge.releaseNonce(), 1);
        assertTrue(bridge.releaseExecuted(0));
    }

    function testGetReserve() public {
        uint256 reserve = bridge.getReserve();
        console.log("Bridge Token reserve: %s", reserve);
        assertEq(reserve, 500 ether);
    }

    function testGetCurrentDepositStatus() public {
        (uint256 nonce, bool executed) = bridge.getCurrentDepositStatus();
        console.log("Bridge current deposit nonce: %s", nonce);
        console.log("Bridge current deposit executed: %s", executed);
        assertEq(nonce, 0);
        assertFalse(executed);
    }

    function testGetCurrentReleaseStatus() public {
        (uint256 nonce, bool executed) = bridge.getCurrentReleaseStatus();
        console.log("Bridge current release nonce: %s", nonce);
        console.log("Bridge current release executed: %s", executed);
        assertEq(nonce, 0);
        assertFalse(executed);
    }
}