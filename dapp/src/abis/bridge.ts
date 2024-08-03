export const bridgeAbi = [
	{
	  inputs: [
		{
		  internalType: "uint256",
		  name: "amount",
		  type: "uint256"
		}
	  ],
	  name: "deposit",
	  outputs: [
		{
		  internalType: "bytes32",
		  name: "messageID",
		  type: "bytes32"
		}
	  ],
	  stateMutability: "nonpayable",
	  type: "function"
	},
	{
	  inputs: [
		{
		  internalType: "contract IGateway",
		  name: "gatewayAddress",
		  type: "address"
		},
		{
		  internalType: "address",
		  name: "_erc20Token",
		  type: "address"
		},
		{
		  internalType: "contract AnalogLPBridge",
		  name: "_analogLPBridge",
		  type: "address"
		},
		{
		  internalType: "uint16",
		  name: "recipientNetwork",
		  type: "uint16"
		},
		{
		  internalType: "string",
		  name: "name",
		  type: "string"
		}
	  ],
	  stateMutability: "nonpayable",
	  type: "constructor"
	},
	{
	  anonymous: false,
	  inputs: [
		{
		  indexed: true,
		  internalType: "bytes32",
		  name: "id",
		  type: "bytes32"
		},
		{
		  indexed: true,
		  internalType: "address",
		  name: "from",
		  type: "address"
		},
		{
		  indexed: false,
		  internalType: "uint256",
		  name: "amount",
		  type: "uint256"
		}
	  ],
	  name: "DepositBridge",
	  type: "event"
	},
	{
	  inputs: [
		{
		  internalType: "bytes32",
		  name: "id",
		  type: "bytes32"
		},
		{
		  internalType: "uint128",
		  name: "network",
		  type: "uint128"
		},
		{
		  internalType: "bytes32",
		  name: "sender",
		  type: "bytes32"
		},
		{
		  internalType: "bytes",
		  name: "data",
		  type: "bytes"
		}
	  ],
	  name: "onGmpReceived",
	  outputs: [
		{
		  internalType: "bytes32",
		  name: "",
		  type: "bytes32"
		}
	  ],
	  stateMutability: "payable",
	  type: "function"
	}
  ];