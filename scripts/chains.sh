#!/bin/bash

# Create the logs directory if it doesn't exist
mkdir -p ./logs

echo "Both anvil instances are running. Logs are being written to ./logs/chain_1447.log and ./logs/chain_1559.log."
# Start the first anvil instance and log its output
anvil --chain-id 1447 --port 8545 2>&1 | tee ./logs/chain_1447.log &

# Start the second anvil instance and log its output
anvil --chain-id 1559 --port 8546 2>&1 | tee ./logs/chain_1559.log &

# Wait for both processes to finish
wait
