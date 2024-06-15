from decimal import Decimal, getcontext
from pydantic import BaseModel
from typing import Optional

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

# Helper function to generate random fee
def random_fee(base_fee=0.0025, variation=0.15):
    return base_fee * (1 + random.uniform(-variation, variation))

# Initialize Dexs with random fees
uniswap_ethereum = Dex("Uniswap-Ethereum", token_manager.get_token("Ethereum", "USDT"), token_manager.get_token("Ethereum", "WUSDT"), fee_percent=random_fee())
quickswap_polygon = Dex("Quickswap-Polygon", token_manager.get_token("Polygon", "bUSDT"), token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
uniswap_polygon = Dex("Uniswap-Polygon", token_manager.get_token("Polygon", "USDT"), token_manager.get_token("Polygon", "WUSDT"), fee_percent=random_fee())

# Initialize Bridges with random fees
synapse = Bridge("Synapse", token_manager.get_token("Ethereum", "USDT"), token_manager.get_token("Polygon", "USDT"), fee_percent=random_fee())
polybridge = Bridge("Polybridge", token_manager.get_token("Ethereum", "USDT"), token_manager.get_token("Polygon", "bUSDT"), fee_percent=random_fee())
