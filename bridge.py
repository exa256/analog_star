# TODO accept configurations as arguments and not hardcoded constants
import time
import math
import json
from web3 import Web3

with open('./contracts/out/Bridge.sol/Bridge.json') as f:
    bridge_json = json.load(f)
    BRIDGE_ABI = bridge_json['abi']

# Constants
SRC_CHAIN_RPC = "http://localhost:8545"
DEST_CHAIN_RPC = "http://localhost:8546"
BRIDGE_CONTRACT_ADDRESS_SRC = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
BRIDGE_CONTRACT_ADDRESS_DST = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
ACCOUNT_SRC = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
ACCOUNT_DEST = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
PRIVATE_KEY_SRC = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
PRIVATE_KEY_DEST = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# Initialize web3 instances
web3_src = Web3(Web3.HTTPProvider(SRC_CHAIN_RPC))
web3_dest = Web3(Web3.HTTPProvider(DEST_CHAIN_RPC))

# Load bridge contract
bridge_src = web3_src.eth.contract(address=BRIDGE_CONTRACT_ADDRESS_SRC, abi=BRIDGE_ABI)
bridge_dest = web3_dest.eth.contract(address=BRIDGE_CONTRACT_ADDRESS_DST, abi=BRIDGE_ABI)

TOKEN_ADDRESS_SRC = bridge_src.functions.token().call()
TOKEN_ADDRESS_DEST = bridge_dest.functions.token().call()

def get_nonce_and_balance(bridge, web3):
    nonce = bridge.functions.depositNonce().call()
    balance = bridge.functions.getReserve().call()
    return nonce, balance

def get_deposit_amount(bridge, nonce):
    return bridge.functions.getDepositAmount(nonce).call()

def get_depositor(bridge, nonce):
    return bridge.functions.getDepositor(nonce).call()

def calculate_output_amount(amount_in, reserve_in, reserve_out, fee_percent):
    amount_in_with_fee = amount_in * (1 - fee_percent)
    return (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)


def release_tokens(bridge, web3, to, amount, private_key):
    tx = bridge.functions.release(to, amount).build_transaction({
        'nonce': web3.eth.get_transaction_count(ACCOUNT_SRC), # assume same as account_dst FIXME
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei')
    })
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash_str = web3.to_hex(tx_hash)
    print('released token on opposite bridge')
    print(tx_hash_str)
    return tx_hash_str

def main():
    fee_percent = 0
    last_nonce_src, _ = get_nonce_and_balance(bridge_src, web3_src)
    last_nonce_dest, _ = get_nonce_and_balance(bridge_dest, web3_dest)


    while True:

        current_nonce_src, reserve_src = get_nonce_and_balance(bridge_src, web3_src)
        current_nonce_dest, reserve_dest = get_nonce_and_balance(bridge_dest, web3_dest)


        if current_nonce_src > last_nonce_src:
            amount_to_release = get_deposit_amount(bridge_src, last_nonce_src)
            depositor_address = get_depositor(bridge_src, last_nonce_src)
            reserve_out = bridge_dest.functions.getReserve().call()
            amount_to_release_cfmm = calculate_output_amount(amount_to_release, reserve_src, reserve_out, fee_percent)
            amount_to_release_cfmm = math.floor(amount_to_release_cfmm)  # Convert to nearest integer
            print(f"amount to release: {amount_to_release_cfmm}")
            release_tokens(bridge_dest, web3_dest, depositor_address, amount_to_release_cfmm, PRIVATE_KEY_DEST)
            last_nonce_src = current_nonce_src

        if current_nonce_dest > last_nonce_dest:
            amount_to_release = get_deposit_amount(bridge_dest, last_nonce_dest)
            depositor_address = get_depositor(bridge_dest, last_nonce_dest)
            reserve_out = bridge_src.functions.getReserve().call()
            amount_to_release_cfmm = calculate_output_amount(amount_to_release, reserve_dest, reserve_out, fee_percent)
            amount_to_release_cfmm = math.floor(amount_to_release_cfmm)  # Convert to nearest integer
            print(f"amount to release: {amount_to_release_cfmm}")
            release_tokens(bridge_src, web3_src, depositor_address, amount_to_release_cfmm, PRIVATE_KEY_SRC)
            last_nonce_dest = current_nonce_dest

        time.sleep(1)

if __name__ == "__main__":
    print("Bridge service is running")
    print(f"Listening to Source Chain RPC: {SRC_CHAIN_RPC}")
    print(f"Listening to Destination Chain RPC: {DEST_CHAIN_RPC}")
    print(f"Source Bridge Contract Address: {BRIDGE_CONTRACT_ADDRESS_SRC}")
    print(f"Destination Bridge Contract Address: {BRIDGE_CONTRACT_ADDRESS_DST}")
    print(f"Source Token Address: {TOKEN_ADDRESS_SRC}")
    print(f"Destination Token Address: {TOKEN_ADDRESS_DEST}")

    main()