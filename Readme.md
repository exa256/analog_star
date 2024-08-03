
# Analog * Liquidity Aggregator
> Omni chain liquidity aggregator

```
Found path for start token: sUSDC-A on SourceChain to dUSDC-A on DestinationChain
Route chosen is:
Using DEX-A to swap sUSDC-A on SourceChain to sUSDC-B on SourceChain
Using Bridge-B to swap sUSDC-B on SourceChain to dUSDC-B on DestinationChain
Using DEX-B to swap dUSDC-B on DestinationChain to dUSDC-A on DestinationChain
Total Estimate Slippage Incurred: 0.243 USDC
```

## Installation
using `python 3.12.3`

1. make sure you have Foundry installed
2. install web3.py `pip install web3`

## Test contract and pathway modules
install all forge dependencies, inside ./contracts:
`forge install`
libs we will use for this Analog are:
1. Analog-Labs/analog-gmp
2. OpenZeppelin/openzeppelin-contracts

`forge compile`
### Smart contract tests
Run all smart contract tests:
`forge test -vvvv`

### Pathway unit tests
in root dir, run
`python3 -m unittest test_shortest_path test_lp_exchange`

## Dev Environment and Integration Tests

compile smart contracts
`cd ./contracts && forge compile`

deploy 2 Anvil local rpc chains
from root dir:
`chmod +x ./scripts/chains.sh`
`./scripts/chains.sh`

deploy all the contracts, double check to make sure addresses are correct
`python3 ./scripts/deploy.py`

run the bridge listeniner
`python3 -m bridge`

try running test bridge deposit to ensure tokens are properly released via bridge
`python3 -m test_bridge`
you should see token released, logs from local rpcs and log on bridge listener

running a test shortest path algorithm on real deployed contracts
`python3 -m unittest test_integration_shortest_path`

## Code
### What's implemented 
- working Djikstra's Algorithm for most cost efficient omni chain pathfinding with no limit to number of chains, assets and edges
- Djikstra's algorithm in pure Python unit test as well as with real Solidity CFMM DEX and Bridge
- implementation of standard CFMM Bridge and DEX contracts
- Bridge service implemented as a python listener as well as `AnalogBridge` which utilizes GMP message passing to perform cross chain swap over double sided liquidity pool. 

### Integration:
Following will be the static addresses for contracts deployed, given a fresh chain script is ran successfully
```
sUSDC-A: 0x5FbDB2315678afecb367f032d93F642f64180aa3
sUSDC-B: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
dUSDC-A: 0x5FbDB2315678afecb367f032d93F642f64180aa3
dUSDC-B: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
dex-a: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
dex-b: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
bridge-b-src: 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
bridge-b-dst: 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
```

contracts are found in the ./contracts/src directory.

contracts are mocked Solidity implementation of real smart contracts for testing purpose, consists of:

The `Token` contract is an ERC20 token implementation with minting capabilities. The contract owner can mint new tokens to any address. It initializes with a specified name and symbol, and mints an initial supply to the deployer.

The `Dex` contract is a decentralized exchange that allows swapping between two different ERC20 tokens. It calculates the output amount based on the input amount and reserves, applying a fee. The contract tracks swap operations using a nonce and provides functions to query the reserves and swap status.

The `Bridge` contract facilitates token transfers between different blockchain networks. It allows users to deposit tokens into the contract and the owner to release tokens to specified addresses. The contract keeps track of deposit and release nonces, ensuring each operation is executed only once. It also provides functions to query the status and details of deposits and releases.

The `AnalogBridge` contract utilize Analog GMP to facilitate trustless cross chain transfer between network. Currently limited to Shibuya and Sepolia testnet and cannot be used in local dev environment given Anvil and GMP tooling limitations.

ABIs can be found in ./contracts/out dir

`pathway.py` contains reference working implementation of djikstra algorithm for finding shortest path for wallet swap across multiple networks and chains. Refer to unit test and integration tests for reference.

## Dapp and Testnet

Testnet utilizes bridge and erc20 contracts deployed on Shibuya and Sepolia which are supported Analog GMP testnets multichain environments

Link to demo app for the bridge can be found here: https://analog-bridge-app.vercel.app
note that the front end bridge dapp is supported in a standalone mode and not integrated with path finder algorithm

Testnet contracts are deployed with configurations below:
```
// Shibuya
// lp contract on shibuya is 0x6f978Fc5909CaCCA93fABe3BaC75C12a1856f8F7
// lp bridge on both should be 0x6f978Fc5909CaCCA93fABe3BaC75C12a1856f8F7
// erc20 is 0xC6BfD304d993aBc9A00Af873465a05234cd79acD
// gateway shib is 0x000000007f56768de3133034fa730a909003a165
// sepolia network is 5
// name shibuya-usdc-sepolia
// real lp bridge contract in bytes32: 0x0000000000000000000000016f978fc5909cacca93fabe3bac75c12a1856f8f7
```
```
// Sepolia
// lp contract on sepolia is 0x6f978Fc5909CaCCA93fABe3BaC75C12a1856f8F7
// lp bridge on both should be 0x6f978Fc5909CaCCA93fABe3BaC75C12a1856f8F7
// erc20 is 0xa3DD50f2481d655d9E6e1cB14F0BE417338BB6bb
// gateway sep is 0x000000007f56768de3133034fa730a909003a165
// shibuya network ID is 7
// name sepolia-usdc-shibuya
// real lp bridge contract in bytes32: 0x0000000000000000000000016f978fc5909cacca93fabe3bac75c12a1856f8f7
```


