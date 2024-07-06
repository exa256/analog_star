import unittest
from pathway import Token, LPExchange
from decimal import Decimal

class TestLPExchange(unittest.TestCase):
    def setUp(self):
        # Initialize the AMM with initial reserves
        self.token_a = Token(chain="Ethereum", name="ETH", amount=10)
        self.token_b = Token(chain="Ethereum", name="USDT", amount=500)
        self.amm = LPExchange(self.token_a, self.token_b, fee_percent=0.0025)

    def test_swap_b_from_a(self):
        # Buyer sends 1 ETH
        a_amount = Decimal(1)
        buyer_receives = self.amm.swap_b_from_a(a_amount)

        # Expected new reserves after the swap
        expected_a_reserve = Decimal(11)  # 10 + 1 ETH
        # Calculate the fee
        fee = a_amount * self.amm.fee_percent

        # Calculate the expected B reserve considering the fee
        expected_b_reserve = Decimal(454)

        # Get actual reserves after the swap
        actual_a_reserve = self.amm.get_a_reserve()
        actual_b_reserve = self.amm.get_b_reserve()

        # Assertions to check if the actual reserves match the expected reserves
        self.assertEqual(actual_a_reserve, expected_a_reserve, f"Expected A reserve: {expected_a_reserve}, but got: {actual_a_reserve}")
        self.assertEqual(actual_b_reserve, expected_b_reserve, f"Expected B reserve: {expected_b_reserve}, but got: {actual_b_reserve}")

        # Print the results for verification
        print(f"Buyer receives: {buyer_receives} {self.token_b.name} (amount: {buyer_receives})")
        print(f"A reserve after swap: {actual_a_reserve} {self.token_a.name} (amount: {actual_a_reserve})")
        print(f"B reserve after swap: {actual_b_reserve} {self.token_b.name} (amount: {actual_b_reserve})")

if __name__ == '__main__':
    unittest.main()