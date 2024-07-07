// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Dex {
    IERC20 public tokenA;
    IERC20 public tokenB;
    uint256 public feePercent; // Fee percentage in basis points (e.g., 25 for 0.25%)
    string public chainName;
    uint256 public swapNonce;
    mapping(uint256 => bool) public swapExecuted;

    constructor(address _tokenA, address _tokenB, uint256 _feePercent, string memory _chainName) {
        require(_tokenA != _tokenB, "Tokens must be different");
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
        feePercent = _feePercent;
        chainName = _chainName;
        swapNonce = 0;
    }

    function _getReserve(IERC20 token) private view returns (uint256) {
        return token.balanceOf(address(this));
    }

    function getAReserve() public view returns (uint256) {
        return _getReserve(tokenA);
    }

    function getBReserve() public view returns (uint256) {
        return _getReserve(tokenB);
    }

    function _getAmountOut(uint256 amountIn, uint256 reserveIn, uint256 reserveOut) private view returns (uint256) {
        uint256 amountInWithFee = amountIn * (10000 - feePercent) / 10000;
        return (amountInWithFee * reserveOut) / (reserveIn + amountInWithFee);
    }

    function _swap(IERC20 fromToken, IERC20 toToken, uint256 amountIn) private returns (uint256) {
        uint256 reserveIn = _getReserve(fromToken);
        uint256 reserveOut = _getReserve(toToken);
        uint256 amountOut = _getAmountOut(amountIn, reserveIn, reserveOut);

        require(fromToken.transferFrom(msg.sender, address(this), amountIn), "Transfer failed");
        require(toToken.transfer(msg.sender, amountOut), "Transfer failed");

        swapExecuted[swapNonce] = true;
        swapNonce++;

        return amountOut;
    }

    function swapAForB(uint256 amountA) external returns (uint256) {
        return _swap(tokenA, tokenB, amountA);
    }

    function swapBForA(uint256 amountB) external returns (uint256) {
        return _swap(tokenB, tokenA, amountB);
    }

    function getPairwise() external view returns (string memory, address, address) {
        return (chainName, address(tokenA), address(tokenB));
    }

    function getCurrentSwapStatus() external view returns (uint256, bool) {
        return (swapNonce, swapExecuted[swapNonce]);
    }
}