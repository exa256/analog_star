#!/bin/bash

echo "Both anvil instances are running. Logs are being written to chain_1447.log and chain_1559.log."
# Start the first anvil instance and log its output
anvil --chain-id 1447 --port 8545 2>&1 | tee chain_1447.log &

# Start the second anvil instance and log its output
anvil --chain-id 1559 --port 8546 2>&1 | tee chain_1559.log &

# Wait for both processes to finish
wait
