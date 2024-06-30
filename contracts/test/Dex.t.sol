// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/console.sol";
import {Test, console} from "forge-std/Test.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Dex} from "../src/Dex.sol";

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

contract DexTest is Test {
    Dex public dex;
    MintableERC20 public tokenA;
    MintableERC20 public tokenB;
    address public user = address(0x123);

    function setUp() public {
        tokenA = new MintableERC20("Token A", "TKA");
        tokenB = new MintableERC20("Token B", "TKB");

        // Mint tokens for the user and the Dex contract
        tokenA.mint(user, 1000 ether);
        tokenA.mint(address(this), 1000 ether);
        tokenB.mint(address(this), 1000 ether);

        // Deploy the Dex contract
        dex = new Dex(address(tokenA), address(tokenB), 25, "TestChain");

        // Transfer some tokens to the Dex contract to provide liquidity
        tokenA.transfer(address(dex), 500 ether);
        tokenB.transfer(address(dex), 500 ether);
    }

    function testSwapAForB() public {
        uint256 amountA = 100 ether;

        // Approve the Dex contract to spend tokens on behalf of the user
        vm.startPrank(user);
        console.log("User %s approves Dex to spend %s tokens of Token A", user, amountA);
        tokenA.approve(address(dex), amountA);

        // Log balances before the swap
        console.log("User Token A balance before swap: %s", tokenA.balanceOf(user));
        console.log("User Token B balance before swap: %s", tokenB.balanceOf(user));
        console.log("Dex Token A balance before swap: %s", tokenA.balanceOf(address(dex)));
        console.log("Dex Token B balance before swap: %s", tokenB.balanceOf(address(dex)));

        // Perform the swap
        console.log("User %s performs swapAForB with %s tokens of Token A", user, amountA);
        uint256 amountBOut = dex.swapAForB(amountA);
        vm.stopPrank();

        // Check balances
        console.log("Checking balances after swapAForB");
        console.log("User Token A balance: %s", tokenA.balanceOf(user));
        console.log("User Token B balance: %s", tokenB.balanceOf(user));
        console.log("Dex Token A balance: %s", tokenA.balanceOf(address(dex)));
        console.log("Dex Token B balance: %s", tokenB.balanceOf(address(dex)));

        assertEq(tokenA.balanceOf(user), 900 ether);
        assertTrue(tokenB.balanceOf(user) >= amountBOut);
        assertEq(tokenA.balanceOf(address(dex)), 600 ether);
        assertTrue(tokenB.balanceOf(address(dex)) <= 500 ether - amountBOut);

        // Check swapNonce and swapExecuted
        console.log("Checking swapNonce and swapExecuted");
        console.log("Dex swapNonce: %s", dex.swapNonce());
        console.log("Dex swapExecuted(0): %s", dex.swapExecuted(0));
        assertEq(dex.swapNonce(), 1);
        assertTrue(dex.swapExecuted(0));
    }

    function testSwapBForA() public {
        tokenB.mint(user, 1000 ether);
        uint256 amountB = 100 ether;

        // Log balances before the swap
        console.log("User Token A balance before swap: %s", tokenA.balanceOf(user));
        console.log("User Token B balance before swap: %s", tokenB.balanceOf(user));
        console.log("Dex Token A balance before swap: %s", tokenA.balanceOf(address(dex)));
        console.log("Dex Token B balance before swap: %s", tokenB.balanceOf(address(dex)));

        // Perform the swap
        vm.startPrank(user);
        console.log("User %s approves Dex to spend %s tokens of Token B", user, amountB);
        tokenB.approve(address(dex), amountB);

        console.log("User %s performs swapBForA with %s tokens of Token B", user, amountB);
        uint256 amountAOut = dex.swapBForA(amountB);
        vm.stopPrank();

        // Check balances
        console.log("Checking balances after swapBForA");
        console.log("User Token A balance: %s", tokenA.balanceOf(user));
        console.log("User Token B balance: %s", tokenB.balanceOf(user));
        console.log("Dex Token A balance: %s", tokenA.balanceOf(address(dex)));
        console.log("Dex Token B balance: %s", tokenB.balanceOf(address(dex)));

        assertEq(tokenB.balanceOf(user), 900 ether);
        assertTrue(tokenA.balanceOf(user) >= amountAOut);
        assertEq(tokenB.balanceOf(address(dex)), 600 ether);
        assertTrue(tokenA.balanceOf(address(dex)) <= 500 ether - amountAOut);

        // Check swapNonce and swapExecuted
        console.log("Checking swapNonce and swapExecuted");
        console.log("Dex swapNonce: %s", dex.swapNonce());
        console.log("Dex swapExecuted(0): %s", dex.swapExecuted(0));
        assertEq(dex.swapNonce(), 1);
        assertTrue(dex.swapExecuted(0));
    }
}