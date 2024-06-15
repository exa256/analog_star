from decimal import Decimal, getcontext
from pydantic import BaseModel
from typing import Optional
import heapq
from collections import defaultdict, deque

class Token(BaseModel):
    chain: str
    name: str
    amount: Optional[int] = None

# Set precision for Decimal calculations
getcontext().prec = 50

TokenNode = tuple[str, str]

class Pairwise(BaseModel):
    """
    Pairwise is a tuple of two tokens, by chain and name
    """
    token_a: TokenNode
    token_b: TokenNode

class TokenManager:
    def __init__(self):
        self.tokens = {}

    def add_token(self, chain: str, name: str, amount: Optional[int] = None):
        key = (chain, name)
        if key in self.tokens:
            raise ValueError(f"Token with chain '{chain}' and name '{name}' already exists.")
        self.tokens[key] = Token(chain=chain, name=name, amount=amount)

    def get_token(self, chain: str, name: str) -> Token:
        key = (chain, name)
        return self.tokens.get(key, None)

    def get_all_keys(self) -> set[TokenNode]:
        return set(self.tokens.keys())


# constant function market making in python
class LiquidityPool:
    def __init__(self, token_a: Token, token_b: Token):
        self.token_a = token_a
        self.token_b = token_b
    
    def get_b_reserve(self):
        return Decimal(self.token_b.amount)

    def get_a_reserve(self):
        return Decimal(self.token_a.amount)

    def set_a_reserve(self, amount):
        self.token_a.amount = int(amount)
        return Decimal(self.token_a.amount)

    def set_b_reserve(self, amount):
        self.token_b.amount = int(amount)
        return Decimal(self.token_b.amount)

class LPExchange(LiquidityPool):
    """
    Internal Library for simulating AMM in python
    """
    def __init__(self, token_a: Token, token_b: Token, fee_percent=0.0025) -> None:
        super().__init__(token_a, token_b)
        self.fee_percent = Decimal(fee_percent)

    def get_a_from_b(self, b_amount: Decimal) -> Decimal:
        b_amount = Decimal(b_amount)
        fee = b_amount * self.fee_percent
        invarient = self.get_a_reserve() * self.get_b_reserve()
        new_a_reserve = invarient / (self.get_b_reserve() + b_amount - fee)
        return self.get_a_reserve() - new_a_reserve

    def get_b_from_a(self, a_amount: Decimal) -> Decimal:
        a_amount = Decimal(a_amount)
        fee = a_amount * self.fee_percent
        invarient = self.get_a_reserve() * self.get_b_reserve()
        new_b_reserve = invarient / (self.get_a_reserve() + a_amount - fee)
        return self.get_b_reserve() - new_b_reserve

    def swap_a_from_b(self, b_amount: Decimal) -> Decimal:
        a_output = self.get_a_from_b(b_amount)
        self.set_b_reserve(self.get_b_reserve() + Decimal(b_amount))
        self.set_a_reserve(self.get_a_reserve() - a_output)
        return a_output

    def swap_b_from_a(self, a_amount: Decimal) -> Decimal:
        b_output = self.get_b_from_a(a_amount)
        self.set_a_reserve(self.get_a_reserve() + Decimal(a_amount))
        self.set_b_reserve(self.get_b_reserve() - b_output)
        return b_output

    def get_token_a(self) -> Token:
        return self.token_a

    def get_token_b(self) -> Token:
        return self.token_b


class Dex(LPExchange):
    def __init__(self, name: str, token_a: Token, token_b: Token, fee_percent=0.0025) -> None:
        if token_a.chain != token_b.chain:
            raise ValueError("Dex can only have tokens from the same chain.")
        super().__init__(token_a, token_b, fee_percent)
        self.name = name

    def get_pairwise(self) -> Pairwise:
        return Pairwise(token_a=TokenNode(self.token_a.name, self.token_a.chain), token_b=TokenNode(self.token_b.name, self.token_b.chain))

class Bridge(LPExchange):
    def __init__(self, name: str, token_a: Token, token_b: Token, fee_percent=0.0025) -> None:
        if token_a.chain == token_b.chain:
            raise ValueError("Bridge must have tokens from different chains.")
        super().__init__(token_a, token_b, fee_percent)
        self.name = name

    def get_pairwise(self) -> Pairwise:
        return Pairwise(token_a=TokenNode(self.token_a.name, self.token_a.chain), token_b=TokenNode(self.token_b.name, self.token_b.chain))

# Initialize TokenManager and add tokens
import random

token_manager = TokenManager()
token_manager.add_token("Ethereum", "USDT", random.randint(1000, 10000))
token_manager.add_token("Ethereum", "WUSDT", random.randint(1000, 10000))
token_manager.add_token("Polygon", "bUSDT", random.randint(1000, 10000))
token_manager.add_token("Polygon", "USDT", random.randint(1000, 10000))
token_manager.add_token("Polygon", "WUSDT", random.randint(1000, 10000))
token_manager.add_token("Polygon", "aaveUSDT", random.randint(1000, 10000))

# Helper function to generate random fee
def random_fee(base_fee=0.0025, variation=0.15):
    return base_fee * (1 + random.uniform(-variation, variation))

# Initialize Dexs with random fees
uniswap_ethereum = Dex("Uniswap-Ethereum", token_manager.get_token("Ethereum", "USDT"), token_manager.get_token("Ethereum", "WUSDT"), fee_percent=random_fee())
quickswap_polygon = Dex("Quickswap-Polygon", token_manager.get_token("Polygon", "bUSDT"), token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
uniswap_polygon = Dex("Uniswap-Polygon", token_manager.get_token("Polygon", "USDT"), token_manager.get_token("Polygon", "WUSDT"), fee_percent=random_fee())
uniswap_polygon_aave = Dex("Uniswap-Polygon-Aave", token_manager.get_token("Polygon", "aaveUSDT"), token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
aave_polygon = Dex("Aave-Polygon", token_manager.get_token("Polygon", "aaveUSDT"), token_manager.get_token("Polygon", "USDT"), fee_percent=0)

# Initialize Bridges with random fees
synapse = Bridge("Synapse", token_manager.get_token("Ethereum", "USDT"), token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
polybridge = Bridge("Polybridge", token_manager.get_token("Ethereum", "USDT"), token_manager.get_token("Polygon", "bUSDT"), fee_percent=random_fee())

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.weights = {}
        self.lp_names = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, weight, lp_name):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight
        self.lp_names[(from_node, to_node)] = lp_name
        self.lp_names[(to_node, from_node)] = lp_name

def dijkstra(graph: Graph, initial: TokenNode, target: TokenNode):
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    
    while current_node is not None:
        if current_node == target:
            break
        
        visited.add(current_node)
        destinations = graph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + weight_to_current_node
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            break
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # Reconstruct the shortest path to the target node
    path = []
    edges_used = []
    current_node = target
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        if next_node is not None:
            edges_used.append((next_node, current_node, graph.lp_names[(next_node, current_node)]))
        current_node = next_node
    path = path[::-1]
    edges_used = edges_used[::-1]
    
    return path, edges_used, shortest_paths[target][1] if target in shortest_paths else ([], [], float('infinity'))

# Create graph and add nodes and edges
graph = Graph()

# Add nodes
for token in token_manager.get_all_keys():
    graph.add_node(token)

# Add edges with weights
def add_edges_for_lp(graph, lp: LPExchange):
    token_a_node = (lp.get_token_a().chain, lp.get_token_a().name)
    token_b_node = (lp.get_token_b().chain, lp.get_token_b().name)
    a_to_b_weight = lp.fee_percent + abs(lp.get_a_reserve() - lp.get_b_reserve())
    b_to_a_weight = lp.fee_percent + abs(lp.get_b_reserve() - lp.get_a_reserve())
    graph.add_edge(token_a_node, token_b_node, a_to_b_weight, lp.name)
    graph.add_edge(token_b_node, token_a_node, b_to_a_weight, lp.name)

# Adding edges for each LP
add_edges_for_lp(graph, uniswap_ethereum)
add_edges_for_lp(graph, quickswap_polygon)
add_edges_for_lp(graph, uniswap_polygon)
add_edges_for_lp(graph, uniswap_polygon_aave)
add_edges_for_lp(graph, aave_polygon)
add_edges_for_lp(graph, synapse)
add_edges_for_lp(graph, polybridge)

# Run Dijkstra's algorithm from a starting node to a target node
start_token = ("Ethereum", "WUSDT")
target_token = ("Polygon", "aaveUSDT")
shortest_path, edges_used, cost = dijkstra(graph, start_token, target_token)
print("Shortest path:", shortest_path)
print("Edges used:", edges_used)
print("Cost:", cost)
