import unittest
import random
from decimal import Decimal
from a_wallet import TokenManager, Bridge, Dex, Graph, add_edges_for_lp, dijkstra, random_fee

class TestDijkstraAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token_manager = TokenManager()
        cls.token_manager.add_token("Ethereum", "USDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Ethereum", "WUSDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Polygon", "bUSDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Polygon", "USDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Polygon", "WUSDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Polygon", "aaveUSDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Arbitrum", "USDT", random.randint(1000, 10000))
        cls.token_manager.add_token("Arbitrum", "bUSDT", random.randint(1000, 10000))

        cls.uniswap_ethereum = Dex("Uniswap-Ethereum", cls.token_manager.get_token("Ethereum", "USDT"), cls.token_manager.get_token("Ethereum", "WUSDT"), fee_percent=random_fee())
        cls.quickswap_polygon = Dex("Quickswap-Polygon", cls.token_manager.get_token("Polygon", "bUSDT"), cls.token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
        cls.uniswap_polygon = Dex("Uniswap-Polygon", cls.token_manager.get_token("Polygon", "USDT"), cls.token_manager.get_token("Polygon", "WUSDT"), fee_percent=random_fee())
        cls.uniswap_polygon_aave = Dex("Uniswap-Polygon-Aave", cls.token_manager.get_token("Polygon", "aaveUSDT"), cls.token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
        cls.aave_polygon = Dex("Aave-Polygon", cls.token_manager.get_token("Polygon", "aaveUSDT"), cls.token_manager.get_token("Polygon", "USDT"), fee_percent=0)
        cls.uniswap_arbitrum = Dex("Uniswap-Arbitrum", cls.token_manager.get_token("Arbitrum", "USDT"), cls.token_manager.get_token("Arbitrum", "bUSDT"), fee_percent=random_fee())

        cls.synapse = Bridge("Synapse", cls.token_manager.get_token("Ethereum", "USDT"), cls.token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
        cls.polybridge = Bridge("Polybridge", cls.token_manager.get_token("Ethereum", "USDT"), cls.token_manager.get_token("Polygon", "bUSDT"), fee_percent=random_fee())
        cls.arbitrumbridge = Bridge("ArbitrumBridge", cls.token_manager.get_token("Arbitrum", "bUSDT"), cls.token_manager.get_token("Ethereum", "WUSDT"), fee_percent=random_fee())

    def test_dijkstra_algorithm(self):
        graph = Graph()
        large_swap_amount = Decimal(1000)

        for token in self.token_manager.get_all_keys():
            graph.add_node(token)

        add_edges_for_lp(graph, self.uniswap_ethereum, large_swap_amount)
        add_edges_for_lp(graph, self.quickswap_polygon, large_swap_amount)
        add_edges_for_lp(graph, self.uniswap_polygon, large_swap_amount)
        add_edges_for_lp(graph, self.uniswap_polygon_aave, large_swap_amount)
        add_edges_for_lp(graph, self.aave_polygon, large_swap_amount)
        add_edges_for_lp(graph, self.synapse, large_swap_amount)
        add_edges_for_lp(graph, self.polybridge, large_swap_amount)
        add_edges_for_lp(graph, self.arbitrumbridge, large_swap_amount)
        add_edges_for_lp(graph, self.uniswap_arbitrum, large_swap_amount)

        start_token = ("Arbitrum", "USDT")
        target_token = ("Polygon", "aaveUSDT")
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

    def test_unreachable_token(self):
        graph = Graph()
        large_swap_amount = Decimal(1000)

        for token in self.token_manager.get_all_keys():
            graph.add_node(token)

        # Do not add edge for uniswap_arbitrum or bridge to make it unreachable

        start_token = ("Arbitrum", "USDT")
        target_token = ("Arbitrum", "bUSDT")
        shortest_path_result = dijkstra(graph, start_token, target_token)
        shortest_path, edges_used, cost = shortest_path_result.path, shortest_path_result.edges_used, shortest_path_result.total_cost

        print(f"Attempted path for start token: {start_token[1]} on {start_token[0]} to {target_token[1]} on {target_token[0]}")
        print("Route chosen is:")
        for edge in edges_used:
            from_node, to_node, lp_name = edge
            print(f"Using {lp_name} to swap {from_node[1]} on {from_node[0]} to {to_node[1]} on {to_node[0]}")
        print("Total Cost:", cost)

        self.assertEqual(shortest_path, [])
        self.assertEqual(edges_used, [])
        self.assertEqual(cost, float('infinity'))

class TestSingleHopScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token_manager_dex1 = TokenManager()
        cls.token_manager_dex1.add_token("Chain1", "TokenA", 1000)  # Assuming this is the liquidity amount for DEX1
        cls.token_manager_dex1.add_token("Chain1", "TokenB", 1000)

        cls.token_manager_dex2 = TokenManager()
        cls.token_manager_dex2.add_token("Chain1", "TokenA", 10000)  # Assuming this is the liquidity amount for DEX2
        cls.token_manager_dex2.add_token("Chain1", "TokenB", 10000)

        # Two DEXs with different LP amounts and fees
        # DEX2 has lower fees
        cls.dex1 = Dex("DEX1", cls.token_manager_dex1.get_token("Chain1", "TokenA"), cls.token_manager_dex1.get_token("Chain1", "TokenB"), fee_percent=0.01)
        cls.dex2 = Dex("DEX2", cls.token_manager_dex2.get_token("Chain1", "TokenA"), cls.token_manager_dex2.get_token("Chain1", "TokenB"), fee_percent=0.005)

    def test_single_hop_with_two_dexes(self):
        graph = Graph()
        swap_amount = Decimal(500)

        for token in self.token_manager_dex1.get_all_keys():
            graph.add_node(token)

        add_edges_for_lp(graph, self.dex1, swap_amount)
        add_edges_for_lp(graph, self.dex2, swap_amount)

        start_token = ("Chain1", "TokenA")
        target_token = ("Chain1", "TokenB")
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
        self.assertEqual(edges_used[0][2], "DEX2")  # Ensure DEX2 is chosen due to lower fees and larger LP

if __name__ == '__main__':
    unittest.main()
