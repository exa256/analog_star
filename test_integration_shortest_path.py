import unittest
import time
from decimal import Decimal
from web3 import Web3
from pathway import TokenManager, RealToken, RealDex, RealBridge, Graph, add_edges_for_lp, dijkstra

class TestIntegrationShortestPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token_manager = TokenManager()

        # Add real tokens
        cls.token_manager.add_token("SourceChain", "sUSDC-A", 10000)
        cls.token_manager.add_token("SourceChain", "sUSDC-B", 10000)
        cls.token_manager.add_token("DestinationChain", "dUSDC-A", 10000)
        cls.token_manager.add_token("DestinationChain", "dUSDC-B", 10000)

        # Create real token instances
        cls.susdc_a = RealToken("SourceChain", "sUSDC-A", "0x5FbDB2315678afecb367f032d93F642f64180aa3", "http://localhost:8545")
        cls.susdc_b = RealToken("SourceChain", "sUSDC-B", "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", "http://localhost:8545")
        cls.dusdc_a = RealToken("DestinationChain", "dUSDC-A", "0x5FbDB2315678afecb367f032d93F642f64180aa3", "http://localhost:8546")
        cls.dusdc_b = RealToken("DestinationChain", "dUSDC-B", "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", "http://localhost:8546")

        # Create real DEX instances
        cls.dex_a = RealDex("DEX-A", cls.susdc_a.to_token("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"), cls.susdc_b.to_token("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"), 0.0025, "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0", "http://localhost:8545")
        cls.dex_b = RealDex("DEX-B", cls.dusdc_a.to_token("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"), cls.dusdc_b.to_token("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"), 0.0025, "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0", "http://localhost:8546")

        # Create real Bridge instances
        cls.bridge_b = RealBridge("Bridge-B", cls.susdc_b.to_token("0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"), cls.dusdc_b.to_token("0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"), 0.0025, "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9", "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9", "http://localhost:8545", "http://localhost:8546")

        # Mint tokens to DEX and Bridge addresses to ensure liquidity
        cls.susdc_a.token_contract.functions.mint("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0", 10000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})
        cls.susdc_b.token_contract.functions.mint("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0", 10000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})
        cls.dusdc_a.token_contract.functions.mint("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0", 10000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})
        cls.dusdc_b.token_contract.functions.mint("0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0", 10000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})
        cls.susdc_b.token_contract.functions.mint("0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9", 10000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})
        cls.dusdc_b.token_contract.functions.mint("0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9", 10000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})

    def test_shortest_path(self):
        graph = Graph()
        large_swap_amount = Decimal(1000)

        for token in self.token_manager.get_all_keys():
            graph.add_node(token)

        add_edges_for_lp(graph, self.dex_a, large_swap_amount)
        add_edges_for_lp(graph, self.dex_b, large_swap_amount)
        add_edges_for_lp(graph, self.bridge_b, large_swap_amount)

        start_token = ("SourceChain", "sUSDC-A")
        target_token = ("DestinationChain", "dUSDC-A")
        shortest_path_result = dijkstra(graph, start_token, target_token)
        shortest_path, edges_used, cost = shortest_path_result.path, shortest_path_result.edges_used, shortest_path_result.total_cost

        print(f"Found path for start token: {start_token[1]} on {start_token[0]} to {target_token[1]} on {target_token[0]}")
        print("Route chosen is:")
        for edge in edges_used:
            from_node, to_node, lp_name = edge
            print(f"Using {lp_name} to swap {from_node[1]} on {from_node[0]} to {to_node[1]} on {to_node[0]}")
        print("Total Estimate Slippage Incurred:", cost)
        print("\n")

        self.assertIsNotNone(shortest_path)
        self.assertIsNotNone(edges_used)
        self.assertIsNotNone(cost)
    
    def swap_on_dex(self, dex, from_token, to_token, amount, web3, account, private_key):
        _, tokenA_address, _ = dex.dex_contract.functions.getPairwise().call()

        # Determine the correct swap function based on the from_token address
        if from_token.token_address == tokenA_address:
            swap_function = dex.dex_contract.functions.swapAForB
        else:
            swap_function = dex.dex_contract.functions.swapBForA
        tx = swap_function(amount).build_transaction({
            'nonce': web3.eth.get_transaction_count(account),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei')
        })
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash

    def swap_on_bridge(self, bridge, from_token, to_token, amount, web3, account, private_key):
        initial_reserve = bridge.get_b_reserve() if from_token.token_contract.functions.name().call().endswith("A") else bridge.get_a_reserve()

        # technically bridge can be from A to B
        tx = bridge.bridge_contract_src.functions.deposit(amount).build_transaction({
            'nonce': web3.eth.get_transaction_count(account),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei')
        })
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)

        # # Polling for reserve change on the destination chain
        # while True:
        #     new_reserve = bridge.get_b_reserve() if from_token.name.endswith("A") else bridge.get_a_reserve()
        #     if new_reserve < initial_reserve:
        #         break
        time.sleep(2)

        return tx_hash

    def approve_tokens(self, token, web3, spender, amount, private_key, account):
        tx = token.token_contract.functions.approve(spender, amount).build_transaction({
            'nonce': web3.eth.get_transaction_count(account),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei')
        })
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)

    def test_navigate_shortest(self):
        "NOTE: we hardcode swap and bridge amount on each step"
        graph = Graph()
        large_swap_amount = Decimal(1000)

        for token in self.token_manager.get_all_keys():
            graph.add_node(token)

        add_edges_for_lp(graph, self.dex_a, large_swap_amount)
        add_edges_for_lp(graph, self.dex_b, large_swap_amount)
        add_edges_for_lp(graph, self.bridge_b, large_swap_amount)

        start_token = ("SourceChain", "sUSDC-A")
        target_token = ("DestinationChain", "dUSDC-A")
        shortest_path_result = dijkstra(graph, start_token, target_token)
        shortest_path, edges_used, cost = shortest_path_result.path, shortest_path_result.edges_used, shortest_path_result.total_cost

        # Mint starting token to Alice
        alice_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        self.susdc_a.token_contract.functions.mint(alice_address, 1000).transact({'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'})

        # Create dictionaries for LP names and addresses
        lp_dict = {
            "DEX-A": (self.dex_a, "SourceChain"),
            "DEX-B": (self.dex_b, "DestinationChain"),
            "Bridge-B": (self.bridge_b, "SourceChain") # FIXME technically bridge can be on either src or dest
        }

        address_dict = {
            "sUSDC-A": self.susdc_a,
            "sUSDC-B": self.susdc_b,
            "dUSDC-A": self.dusdc_a,
            "dUSDC-B": self.dusdc_b
        }

        chain_rpc_dict = {
            "SourceChain": "http://localhost:8545",
            "DestinationChain": "http://localhost:8546"
        }

        # Approve all tokens for all contracts to spend
        self.approve_tokens(self.susdc_a, Web3(Web3.HTTPProvider(chain_rpc_dict["SourceChain"])), self.dex_a.dex_contract.address, 1000, PRIVATE_KEY, alice_address)
        self.approve_tokens(self.susdc_a, Web3(Web3.HTTPProvider(chain_rpc_dict["SourceChain"])), self.bridge_b.bridge_contract_src.address, 1000, PRIVATE_KEY, alice_address)
        self.approve_tokens(self.susdc_b, Web3(Web3.HTTPProvider(chain_rpc_dict["SourceChain"])), self.bridge_b.bridge_contract_src.address, 1000, PRIVATE_KEY, alice_address)
        self.approve_tokens(self.dusdc_b, Web3(Web3.HTTPProvider(chain_rpc_dict["DestinationChain"])), self.dex_b.dex_contract.address, 1000, PRIVATE_KEY, alice_address)

        alice_balance_before = self.dusdc_a.token_contract.functions.balanceOf(alice_address).call()

        # Iterate through the path and execute swaps/bridges
        for edge in edges_used:
            from_node, to_node, lp_name = edge
            lp, chain_name = lp_dict[lp_name]
            from_token = address_dict[from_node[1]]
            to_token = address_dict[to_node[1]]
            web3 = Web3(Web3.HTTPProvider(chain_rpc_dict[chain_name]))

            print(f"Using {lp_name} to swap {from_node[1]} on {from_node[0]} to {to_node[1]} on {to_node[0]}")

            if "DEX" in lp_name:
                tx_hash = self.swap_on_dex(lp, from_token, to_token, 1000, web3, alice_address, PRIVATE_KEY)
            elif "Bridge" in lp_name:
                tx_hash = self.swap_on_bridge(lp, from_token, to_token, 1000, web3, alice_address, PRIVATE_KEY)

            tx_hash = web3.to_hex(tx_hash)
            print(f"Transaction hash: {tx_hash}")

        # Check Alice's balance on the destination chain
        alice_balance_after = self.dusdc_a.token_contract.functions.balanceOf(alice_address).call()
        self.assertGreater(alice_balance_after, alice_balance_before)


if __name__ == '__main__':
    unittest.main()