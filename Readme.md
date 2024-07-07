## TODO

- [x] write mock smart contracts (dexs and bridges)
- [x] configure script to deploy contracts on test chain
- [x] djikstra algorithm integrated with real chain data
- [ ] exposed flask api for client to fetch contracts, get pathfinding routes
- [ ] navigator script that executes the path for user
- [ ] cleanup & setup verification scripting
- [ ] nice to have: local env orchestrations based on a JSON configuration

Analog specific:
- [ ] use Analog GMP for trustless bridging
- [ ] deploy contracts and run on testnet

Wallet specific:
- [ ] write CLI for control planes executing txs for best path
- [ ] multi input single output transaction 

Not do:
- account abstraction

## Installation
using `python 3.12.3`

1. make sure you have Foundry installed
2. install web3.py `pip install web3`

## Test contract and pathway modules

inside ./contracts, run
`forge compile`
`forge test`

in root dir, run
`python3 -m unittest`

## Running Dev Environment

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

ABIs can be found in ./contracts/out dir