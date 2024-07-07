import unittest
from decimal import Decimal
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

if __name__ == '__main__':
    unittest.main()