import subprocess
import json

# Constants
SRC_CHAIN_RPC = "http://localhost:8545"
DEST_CHAIN_RPC = "http://localhost:8546"
ACCOUNT = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        exit(1)
    return result.stdout.strip()

def deploy_token(name, symbol, rpc_url):
    command = f'forge create contracts/src/Token.sol:Token --constructor-args "{name}" "{symbol}" --rpc-url {rpc_url} --unlocked --from {ACCOUNT}'
    result = run_command(command)
    return f"Token {name} ({symbol}) deployed at {result} on {rpc_url} \n"

def deploy_dex(token1, token2, fee, chain_name, rpc_url):
    command = f'forge create contracts/src/Dex.sol:Dex --constructor-args "{token1}" "{token2}" {fee} "{chain_name}" --rpc-url {rpc_url} --unlocked --from {ACCOUNT}'
    result = run_command(command)
    return f"DEX with tokens {token1} and {token2} and fee {fee} deployed at {result} on {rpc_url} \n"

def deploy_bridge(token, name, rpc_url):
    command = f'forge create contracts/src/Bridge.sol:Bridge --constructor-args "{token}" "{name}" --rpc-url {rpc_url} --unlocked --from {ACCOUNT}'
    result = run_command(command)
    return f"Bridge {name} with token {token} deployed at {result} on {rpc_url}"

def main():
    log = []

    # Deploy tokens on source chain
    log.append(deploy_token("sUSDC-A", "sUSDC-A", SRC_CHAIN_RPC))
    log.append(deploy_token("sUSDC-B", "sUSDC-B", SRC_CHAIN_RPC))

    # Deploy tokens on destination chain
    log.append(deploy_token("dUSDC-A", "dUSDC-A", DEST_CHAIN_RPC))
    log.append(deploy_token("dUSDC-B", "dUSDC-B", DEST_CHAIN_RPC))

    # Deploy DEXs
    log.append(deploy_dex("0x5FbDB2315678afecb367f032d93F642f64180aa3", "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", 25, "src chain", SRC_CHAIN_RPC)) # hardcoded tokens addr are deterministic
    log.append(deploy_dex("0x5FbDB2315678afecb367f032d93F642f64180aa3", "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", 25, "dst chain", DEST_CHAIN_RPC)) # hardcoded tokens addr are deterministic

    # Deploy bridges
    log.append(deploy_bridge("0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", "bridge-a", SRC_CHAIN_RPC))
    log.append(deploy_bridge("0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", "bridge-b", DEST_CHAIN_RPC))

    # Log all outputs
    with open('deployment_log.txt', 'w') as f:
        for entry in log:
            f.write(entry + '\n')

    print("Deployment complete. Log:")
    for entry in log:
        print(entry)

if __name__ == "__main__":
    main()