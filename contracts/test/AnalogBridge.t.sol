// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import {Test, console} from "forge-std/Test.sol";
import {AnalogLPBridge} from "../src/AnalogBridge.sol";
import {GmpTestTools} from "@analog-gmp-testing/GmpTestTools.sol";
import {Gateway} from "@analog-gmp/Gateway.sol";
import {IGateway} from "@analog-gmp/interfaces/IGateway.sol";
import {GmpMessage, GmpStatus, GmpSender, PrimitiveUtils} from "@analog-gmp/Primitives.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

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

contract GmpTestToolsTest is Test {
    using PrimitiveUtils for GmpSender;
    using PrimitiveUtils for address;

    address private constant ALICE = address(bytes20(keccak256("Alice")));
    address private constant BOB = address(bytes20(keccak256("Bob")));

    Gateway private constant SEPOLIA_GATEWAY = Gateway(GmpTestTools.SEPOLIA_GATEWAY);
    uint16 private constant SEPOLIA_NETWORK = GmpTestTools.SEPOLIA_NETWORK_ID;

    Gateway private constant SHIBUYA_GATEWAY = Gateway(GmpTestTools.SHIBUYA_GATEWAY);
    uint16 private constant SHIBUYA_NETWORK = GmpTestTools.SHIBUYA_NETWORK_ID;

    AnalogLPBridge private shibuyaBridge;
    AnalogLPBridge private sepoliaBridge;

    MintableERC20 private shibuyaErc20;
    MintableERC20 private sepoliaErc20;

    function test_bridge_tokens() external {
        // Step 1: Setup test environment //

        // Deploy the gateway contracts at pre-defined addresses
        // Also creates one fork for each supported network
        GmpTestTools.setup();

        // Add funds to Alice and Bob in all networks
        GmpTestTools.deal(ALICE, 100 ether);
        GmpTestTools.deal(BOB, 100 ether);

        // Step 2: Deploy the ERC20 tokens                   //

        // Switch to Shibuya network and deploy the ERC20 using Alice account
        GmpTestTools.switchNetwork(SHIBUYA_NETWORK, ALICE);
        shibuyaErc20 = new MintableERC20("ShibuyaToken", "SHT");
        shibuyaErc20.mint(ALICE, 1000);
        assertEq(shibuyaErc20.balanceOf(ALICE), 1000, "unexpected alice balance in shibuya");
        assertEq(shibuyaErc20.balanceOf(BOB), 0, "unexpected bob balance in shibuya");

        // Switch to Sepolia network and deploy the ERC20 using Bob account
        GmpTestTools.switchNetwork(SEPOLIA_NETWORK, BOB);
        sepoliaErc20 = new MintableERC20("SepoliaToken", "SPT");
        sepoliaErc20.mint(BOB, 0);
        assertEq(sepoliaErc20.balanceOf(ALICE), 0, "unexpected alice balance in sepolia");
        assertEq(sepoliaErc20.balanceOf(BOB), 0, "unexpected bob balance in sepolia");

        // Step 3: Precompute bridge addresses               //

        AnalogLPBridge shibuyaBridge = AnalogLPBridge(vm.computeCreateAddress(ALICE, vm.getNonce(ALICE)));
        AnalogLPBridge sepoliaBridge = AnalogLPBridge(vm.computeCreateAddress(BOB, vm.getNonce(BOB)));

        // Step 4: Deploy the bridges                        //

        // Switch to Shibuya network and deploy the bridge using Alice account
        GmpTestTools.switchNetwork(SHIBUYA_NETWORK, ALICE);
        shibuyaBridge = new AnalogLPBridge(SHIBUYA_GATEWAY, address(shibuyaErc20), sepoliaBridge, SEPOLIA_NETWORK, "ShibuyaBridge"); // 5 is sepolia?

        // Switch to Sepolia network and deploy the bridge using Bob account
        GmpTestTools.switchNetwork(SEPOLIA_NETWORK, BOB);
        sepoliaBridge = new AnalogLPBridge(SEPOLIA_GATEWAY, address(sepoliaErc20), shibuyaBridge, SHIBUYA_NETWORK, "SepoliaBridge");

        // Step 5: Mint tokens to bridge addresses           //

        // Mint tokens to Shibuya bridge address
        GmpTestTools.switchNetwork(SHIBUYA_NETWORK, ALICE);
        shibuyaErc20.mint(address(shibuyaBridge), 10000);
        assertEq(shibuyaErc20.balanceOf(address(shibuyaBridge)), 10000, "unexpected shibuya bridge balance");

        // Mint tokens to Sepolia bridge address
        GmpTestTools.switchNetwork(SEPOLIA_NETWORK, BOB);
        sepoliaErc20.mint(address(sepoliaBridge), 10000);
        assertEq(sepoliaErc20.balanceOf(address(sepoliaBridge)), 10000, "unexpected sepolia bridge balance");

        // Step 6: Approve tokens for bridge contract            //

        // Switch to Shibuya network and Alice account
        GmpTestTools.switchNetwork(SHIBUYA_NETWORK, ALICE);
        shibuyaErc20.approve(address(shibuyaBridge), 100);

        // Step 7: Deposit funds to destination Gateway Contract //

        // Switch to Sepolia network and Alice account
        GmpTestTools.switchNetwork(SEPOLIA_NETWORK, ALICE);
        // If the sender is a contract, its address must be converted
        GmpSender sender = address(shibuyaErc20).toSender(true);
        // Alice deposits 1 ether to Sepolia gateway contract
        SEPOLIA_GATEWAY.deposit{value: 1 ether}(sender, SHIBUYA_NETWORK);

        // Step 8: Send GMP message //

        // Switch to Shibuya network and Alice account
        GmpTestTools.switchNetwork(SHIBUYA_NETWORK, ALICE);

        // Teleport 100 tokens from Alice to Bob's account in Sepolia
        vm.expectEmit(false, true, false, true, address(shibuyaBridge));
        emit AnalogLPBridge.DepositBridge(bytes32(0), ALICE, 100);
        bytes32 messageID = shibuyaBridge.deposit(100);

        // Now with the `messageID`, Alice can check the message status in the destination gateway contract
        GmpTestTools.switchNetwork(SEPOLIA_NETWORK, ALICE);
        assertTrue(
            SEPOLIA_GATEWAY.gmpInfo(messageID).status == GmpStatus.NOT_FOUND,
            "unexpected message status, expect 'pending'"
        );

        // Step 9: Wait Chronicles Relay the GMP message //

        // The GMP hasn't been executed yet...
        assertEq(sepoliaErc20.balanceOf(ALICE), 0, "unexpected alice balance in sepolia");

        // Simulate relaying the message
        vm.expectEmit(true, true, false, true, address(sepoliaBridge));
        emit AnalogLPBridge.ReleaseBridge(messageID, ALICE, 100);
        GmpTestTools.relayMessages();

        // Success! The GMP message was executed!!!
        assertTrue(SEPOLIA_GATEWAY.gmpInfo(messageID).status == GmpStatus.SUCCESS, "failed to execute GMP");

        // Check ALICE and BOB balance in Shibuya
        GmpTestTools.switchNetwork(SHIBUYA_NETWORK);
        assertEq(shibuyaErc20.balanceOf(ALICE), 900, "unexpected alice's balance in shibuya");

        // Check ALICE and BOB balance in Sepolia
        GmpTestTools.switchNetwork(SEPOLIA_NETWORK);
        assertGt(sepoliaErc20.balanceOf(ALICE), 0, "unexpected alice's balance in sepolia");
    }
}