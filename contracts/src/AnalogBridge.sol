// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import {IGmpReceiver} from "@analog-gmp/interfaces/IGmpReceiver.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IGateway} from "@analog-gmp/interfaces/IGateway.sol";
import {GmpSender, PrimitiveUtils} from "@analog-gmp/Primitives.sol";

contract AnalogLPBridge is IGmpReceiver {
    using PrimitiveUtils for GmpSender;

    IGateway private immutable _trustedGateway;
    AnalogLPBridge public immutable analogLPBridge; // lp recipient bridge on the other networks
    uint16 private immutable _recipientNetwork; // analog specific recipient network identifier
    IERC20 private immutable _token;
    uint256 public feePercent; // Fee percentage in basis points (e.g., 25 for 0.25%)

    string public name;
    uint256 public depositNonce;
    uint256 public releaseNonce;
    mapping(uint256 => bool) public depositExecuted;
    mapping(uint256 => bool) public releaseExecuted;
    mapping(uint256 => uint256) public depositAmounts; // New mapping to store deposit amounts
    mapping(uint256 => address) public depositors; // New mapping to store depositor addresses

    // deposit to the bridge on the source chain
    event DepositBridge(bytes32 indexed id, address indexed from, uint256 amount);

    // release the bridge on the destination chain
    event ReleaseBridge(bytes32 indexed id, address indexed from, uint256 amount);

    uint256 private constant MSG_GAS_LIMIT = 1_000_000;

    /**
     * @dev Bridge command that will be encoded in the `data` field on the `onGmpReceived` method.
     */
    struct BridgeTxCommand {
        address depositor; // depositor address
        uint256 reserveIn; // total reserve prior to the deposit
        uint256 amountIn; // amount deposited by user
    }

    constructor(
        IGateway gatewayAddress,
        address _erc20Token,
        AnalogLPBridge _analogLPBridge,
        uint16 recipientNetwork,
        string memory name
    ) {
        _trustedGateway = gatewayAddress;
        _token = IERC20(_erc20Token);
        analogLPBridge = _analogLPBridge;
        _recipientNetwork = recipientNetwork;
        name = name;
        depositNonce = 0;
        releaseNonce = 0;
        feePercent = 25;
    }

    function _getReserve() private view returns (uint256) {
        return _token.balanceOf(address(this));
    }

    function _getAmountOut(uint256 amountIn, uint256 reserveIn, uint256 reserveOut) private view returns (uint256) {
        uint256 amountInWithFee = amountIn * (10000 - feePercent) / 10000;
        return (amountInWithFee * reserveOut) / (reserveIn + amountInWithFee);
    }

    // TODO implement transaction queue to enforce temporal order based on FIFO
    function _release(address to, uint256 amountIn, uint256 reserveIn) internal returns (uint256) {
        uint256 reserveOut = _getReserve(); // Assuming the reserve out is the same token in this context
        uint256 amountOut = _getAmountOut(amountIn, reserveIn, reserveOut);

        require(_token.transfer(to, amountOut), "Transfer failed");
        releaseExecuted[releaseNonce] = true;
        releaseNonce++;
        return amountOut;
    }
    function deposit(uint256 amount) external returns (bytes32 messageID) {
        // _burn(msg.sender, amount);
        require(_token.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        depositExecuted[depositNonce] = true;
        depositAmounts[depositNonce] = amount; // Store the deposit amount
        depositors[depositNonce] = msg.sender; // Store the depositor's address
        depositNonce++;
        bytes memory message = abi.encode(BridgeTxCommand({depositor: msg.sender, reserveIn: _getReserve(), amountIn: amount}));
        messageID = _trustedGateway.submitMessage(address(analogLPBridge), _recipientNetwork, MSG_GAS_LIMIT, message);
        emit DepositBridge(messageID, msg.sender, amount);
    }

    // handle release on incoming message from GMP
    function onGmpReceived(bytes32 id, uint128 network, bytes32 sender, bytes calldata data)
        external
        payable
        returns (bytes32)
    {
        // Convert bytes32 to address
        address senderAddr = GmpSender.wrap(sender).toAddress();

        // Validate the message
        require(msg.sender == address(_trustedGateway), "Unauthorized: only the gateway can call this method");
        require(network == _recipientNetwork, "Unauthorized network");
        require(senderAddr == address(analogLPBridge), "Unauthorized sender");

        // Decode the command
        BridgeTxCommand memory command = abi.decode(data, (BridgeTxCommand));

        // Mint the tokens to the destination account
        _release(command.depositor, command.amountIn, command.reserveIn);
        emit ReleaseBridge(id, command.depositor, command.amountIn);

        return id;
    }
}