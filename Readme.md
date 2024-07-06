## TODO

- [x] write mock smart contracts (dexs and bridges)
- [ ] configure script to deploy contracts on test chain
- [ ] djikstra algorithm integrated with real chain data
- [ ] trustless multichain smart contracts 

Analog specific:
- [ ] use Analog Watch for fetching contract data
- [ ] use Analog GMP for trustless routing

Wallet specific:
- [ ] write CLI for control planes executing txs for best path
- [ ] multi input single output transaction 

Not do:
- account abstraction

## Installation
using `python 3.12.3`

1. make sure you have Foundry installed
2. install web3.py `pip install web3`

## Running Dev Environment

1. Spinning up local testnets environments

source chain: 
`anvil --chain-id 1447 --port 8545`

destination chain
`anvil --chain-id 1559 --port 8546`

2. Deploy contracts

2.1 Deploy all tokens on each chain
Deploy sUSDC-A
`forge create src/Token.sol:Token --constructor-args "sUSDC-A" "sUSDC-A" --rpc-url http:localhost:8545 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

Deploy sUSDC-B
`forge create src/Token.sol:Token --constructor-args "sUSDC-B" "sUSDC-B" --rpc-url http:localhost:8545 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

Deploy dUSDC-A
`forge create src/Token.sol:Token --constructor-args "dUSDC-A" "dUSDC-A" --rpc-url http:localhost:8546 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

Deploy dUSDC-B
`forge create src/Token.sol:Token --constructor-args "dUSDC-B" "dUSDC-B" --rpc-url http:localhost:8546 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

Following will be the addresses for tokens deployed:
```
sUSDC-A: 0x5FbDB2315678afecb367f032d93F642f64180aa3
sUSDC-B: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
dUSDC-A: 0x5FbDB2315678afecb367f032d93F642f64180aa3
dUSDC-B: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
```

2.2 Deploy all the dexes

`forge create src/Dex.sol:Dex --constructor-args "0x5FbDB2315678afecb367f032d93F642f64180aa3" "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512" 25 "src chain" --rpc-url http:localhost:8545 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

`forge create src/Dex.sol:Dex --constructor-args "0x5FbDB2315678afecb367f032d93F642f64180aa3" "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512" 25 "dst chain" --rpc-url http:localhost:8546 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

DEXs

```
dex-a: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
dex-b: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
```

2.3 Deploy all the bridges contract and bridge service

`forge create src/Bridge.sol:Bridge --constructor-args "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512" "bridge-a"  --rpc-url http:localhost:8545 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

`forge create src/Bridge.sol:Bridge --constructor-args "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512" "bridge-b"  --rpc-url http:localhost:8546 --unlocked --from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

`python3 -m bridge`

2.4 Provide Liquidity for dexes and bridges, mint token to self

1. mint 100 USDCs to the bridge on both chains
cast send 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512 "mint(address, uint256)" 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9 10000 --private-key "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" --rpc-url "http://localhost:8545"

cast send 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512 "mint(address, uint256)" 0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9 10000 --private-key "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" --rpc-url "http://localhost:8546"

2. test call the function to deposit on source chain
cast send 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512 "approve(address, uint256)" 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9 10000 --private-key "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" --rpc-url "http://localhost:8545"

cast send 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9 "deposit(uint256)" 100 --private-key "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" --rpc-url "http://localhost:8545"


2.5 mint token to self.