import time
import json
from web3 import Web3

# Constants
SRC_CHAIN_RPC = "http://localhost:8545"
DEST_CHAIN_RPC = "http://localhost:8546"
BRIDGE_CONTRACT_ADDRESS_SRC = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
BRIDGE_CONTRACT_ADDRESS_DST = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
TOKEN_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
ACCOUNT = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# Initialize web3 instances
web3_src = Web3(Web3.HTTPProvider(SRC_CHAIN_RPC))
web3_dest = Web3(Web3.HTTPProvider(DEST_CHAIN_RPC))

# Load token and bridge contracts
with open('./contracts/out/Bridge.sol/Bridge.json') as f:
    bridge_json = json.load(f)
    BRIDGE_ABI = bridge_json['abi']

with open('./contracts/out/Token.sol/Token.json') as f:
    token_json = json.load(f)
    TOKEN_ABI = token_json['abi']

bridge_src = web3_src.eth.contract(address=BRIDGE_CONTRACT_ADDRESS_SRC, abi=BRIDGE_ABI)
bridge_dest = web3_dest.eth.contract(address=BRIDGE_CONTRACT_ADDRESS_DST, abi=BRIDGE_ABI)
token_src = web3_src.eth.contract(address=TOKEN_ADDRESS, abi=TOKEN_ABI)
token_dest = web3_dest.eth.contract(address=TOKEN_ADDRESS, abi=TOKEN_ABI)

def mint_tokens(token, web3, to, amount, private_key):
    tx = token.functions.mint(to, amount).build_transaction({
        'nonce': web3.eth.get_transaction_count(ACCOUNT),
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei')
    })
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)

def approve_tokens(token, web3, spender, amount, private_key):
    tx = token.functions.approve(spender, amount).build_transaction({
        'nonce': web3.eth.get_transaction_count(ACCOUNT),
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei')
    })
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)

def deposit_tokens(bridge, web3, amount, private_key):
    tx = bridge.functions.deposit(amount).build_transaction({
        'nonce': web3.eth.get_transaction_count(ACCOUNT),
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei')
    })
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)

def get_balance(token, address):
    return token.functions.balanceOf(address).call()

def main():
    # Mint tokens to the bridge on both chains
    print('seeding tokens to bridge contracts')
    mint_tokens(token_src, web3_src, BRIDGE_CONTRACT_ADDRESS_SRC, 10000, PRIVATE_KEY)
    mint_tokens(token_dest, web3_dest, BRIDGE_CONTRACT_ADDRESS_DST, 10000, PRIVATE_KEY)

    # Check balances before deposit
    balance_src_before = get_balance(token_src, ACCOUNT)
    balance_dest_before = get_balance(token_dest, ACCOUNT)

    # Approve and deposit tokens on the source chain
    print('approving and depositing token to bridge')
    approve_tokens(token_src, web3_src, BRIDGE_CONTRACT_ADDRESS_SRC, 10000, PRIVATE_KEY)
    deposit_tokens(bridge_src, web3_src, 100, PRIVATE_KEY)

    # Wait for the bridge service to process the deposit
    time.sleep(2)

    # Check balances after deposit
    balance_src_after = get_balance(token_src, ACCOUNT)
    balance_dest_after = get_balance(token_dest, ACCOUNT)

    print(f"Source wallet balance before bridge: {balance_src_before}, after: {balance_src_after}")
    print(f"Destination wallet balance before bridge: {balance_dest_before}, after: {balance_dest_after}")

    assert balance_src_after < balance_src_before, "Source balance did not decrease"
    assert balance_dest_after > balance_dest_before, "Destination balance did not increase"

if __name__ == "__main__":
    main()