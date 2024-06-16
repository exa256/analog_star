import random
from decimal import Decimal, getcontext
from pydantic import BaseModel
from typing import Optional
import heapq
from collections import defaultdict, deque
from typing import NamedTuple


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

# Helper function to generate random fee
def random_fee(base_fee=0.0025, variation=0.15):
    return base_fee * (1 + random.uniform(-variation, variation))

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

class ShortestPathResult(NamedTuple):
    path: list[TokenNode]
    edges_used: list[tuple[TokenNode, TokenNode, str]]
    total_cost: float

def dijkstra(graph: Graph, initial: TokenNode, target: TokenNode) -> ShortestPathResult:
    # Initialize a dictionary to store the shortest paths from the initial node to all other nodes.
    # Each entry in the dictionary maps a node (TokenNode) to a tuple containing the previous node in the path
    # and the total weight (cost) from the initial node to the current node.
    shortest_paths: dict[TokenNode, tuple[Optional[TokenNode], float]] = {initial: (None, 0)}
    # Start with the initial node as the current node.
    current_node: Optional[TokenNode] = initial
    # Create a set to keep track of visited nodes to avoid revisiting them.
    visited: set[TokenNode] = set()
    
    # Continue the algorithm until there are no more nodes to visit.
    while current_node is not None:
        # If the current node is the target, the shortest path has been found.
        if current_node == target:
            break
        
        # Mark the current node as visited.
        visited.add(current_node)
        # Retrieve all possible next nodes (destinations) from the current node.
        destinations: list[TokenNode] = graph.edges[current_node]
        # Get the current total weight to the current node.
        weight_to_current_node: float = shortest_paths[current_node][1]

        # Iterate over each neighboring node and calculate the weight of the path through the current node.
        for next_node in destinations:
            weight: float = graph.weights[(current_node, next_node)] + weight_to_current_node
            # If the next node is not in the shortest_paths dictionary, or if the new weight is less than
            # the previously recorded weight, update the shortest path to the next node.
            if next_node not in shortest_paths or shortest_paths[next_node][1] > weight:
                shortest_paths[next_node] = (current_node, weight)
        
        # Prepare the next set of destinations by excluding already visited nodes and selecting the node
        # with the lowest total weight.
        next_destinations: dict[TokenNode, tuple[Optional[TokenNode], float]] = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        # If there are no more nodes to visit, exit the loop.
        if not next_destinations:
            break
        # Select the next node with the smallest total weight.
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # Reconstruct the shortest path and the edges used from the shortest_paths dictionary.
    path: list[TokenNode] = []
    edges_used: list[tuple[TokenNode, TokenNode, str]] = []
    # Start from the target node and work backwards to the initial node.
    current_node = target
    while current_node is not None:
        # Add the current node to the path.
        path.append(current_node)
        # Get the previous node in the path.
        next_node = shortest_paths.get(current_node, [None])[0]
        # If there is a previous node, add the edge to the list of edges used.
        if next_node is not None:
            edges_used.append((next_node, current_node, graph.lp_names[(next_node, current_node)]))
        # Move to the previous node.
        current_node = next_node
    # Reverse the path and edges used to get them in the correct order from initial to target.
    path.reverse()
    edges_used.reverse()
    
    # If the target node is in the shortest_paths dictionary, return the shortest path result.
    # Otherwise, return an empty path with infinite cost, indicating that the target is unreachable.
    if target in shortest_paths:
        return ShortestPathResult(path, edges_used, shortest_paths[target][1])
    else:
        return ShortestPathResult([], [], float('infinity'))


def add_edges_for_lp(graph: Graph, lp: LPExchange, large_swap_amount: Decimal) -> None:
    """
    we make assumption that asset A and B is like-kinded asset, ie. stable coins
    therefore weight is calculated as differences between the input/output aka. slippage

    in reality we need price oracle and ways to determine dollar value of each asset, considering 
    not only slippage but considering factors like relative volume, price impact on the pool
    this would allow the algorithm to handle larger swap sizes and non homongenous trading pair like ETH-Stable
    """
    a_to_b_output = lp.get_b_from_a(large_swap_amount)
    b_to_a_output = lp.get_a_from_b(large_swap_amount)
    
    a_to_b_slippage = (large_swap_amount - a_to_b_output) / large_swap_amount
    b_to_a_slippage = (large_swap_amount - b_to_a_output) / large_swap_amount
    
    a_to_b_weight = max(a_to_b_slippage, 0)
    b_to_a_weight = max(b_to_a_slippage, 0)
    
    token_a_node = (lp.get_token_a().chain, lp.get_token_a().name)
    token_b_node = (lp.get_token_b().chain, lp.get_token_b().name)
    
    graph.add_edge(token_a_node, token_b_node, a_to_b_weight, lp.name)
    graph.add_edge(token_b_node, token_a_node, b_to_a_weight, lp.name)