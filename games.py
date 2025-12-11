"""
Game models for the Flask betting simulator.
"""

import numpy as np
from typing import Dict


class DiceGame:
    def __init__(self, sides: int = 6, bet_amount: float = 1.0):
        self.sides = sides
        self.bet_amount = bet_amount

    def play(self) -> Dict[str, float]:
        player_choice = np.random.randint(1, self.sides + 1)
        dice_roll = np.random.randint(1, self.sides + 1)
        player_won = dice_roll == player_choice
        payout = self._calculate_payout(player_won)
        player_profit = payout - self.bet_amount
        house_profit = self.bet_amount - payout
        return {
            "player_bet": self.bet_amount,
            "dice_roll": dice_roll,
            "player_choice": player_choice,
            "player_won": player_won,
            "payout": payout,
            "player_profit": player_profit,
            "house_profit": house_profit,
        }

    def _calculate_payout(self, player_won: bool) -> float:
        raise NotImplementedError


class FairDiceGame(DiceGame):
    def __init__(self, sides: int = 6, bet_amount: float = 1.0):
        super().__init__(sides, bet_amount)
        self.payout_multiplier = sides

    def _calculate_payout(self, player_won: bool) -> float:
        if player_won:
            return self.bet_amount * self.payout_multiplier
        return 0.0


class TweakedDiceGame(DiceGame):
    def __init__(self, sides: int = 6, bet_amount: float = 1.0, payout_multiplier: float = 5.0):
        super().__init__(sides, bet_amount)
        self.payout_multiplier = payout_multiplier

    def _calculate_payout(self, player_won: bool) -> float:
        if player_won:
            return self.bet_amount * self.payout_multiplier
        return 0.0


def calculate_house_edge(win_probability: float, payout_multiplier: float) -> float:
    return (1 - (win_probability * payout_multiplier)) * 100


class WeightedProbabilitiesGame(DiceGame):
    def __init__(self, sides: int = 6, bet_amount: float = 1.0, player_number_weight: float = 0.12):
        super().__init__(sides, bet_amount)
        self.player_number_weight = player_number_weight
        self.payout_multiplier = sides

    def play(self) -> Dict[str, float]:
        player_choice = np.random.randint(1, self.sides + 1)
        remaining_weight = (1.0 - self.player_number_weight) / (self.sides - 1)
        probabilities = [remaining_weight] * self.sides
        probabilities[player_choice - 1] = self.player_number_weight
        probabilities = np.array(probabilities)
        probabilities = probabilities / probabilities.sum()

        outcomes = np.arange(1, self.sides + 1)
        dice_roll = np.random.choice(outcomes, p=probabilities)
        player_won = dice_roll == player_choice
        payout = self._calculate_payout(player_won)
        player_profit = payout - self.bet_amount
        house_profit = self.bet_amount - payout
        return {
            "player_bet": self.bet_amount,
            "dice_roll": dice_roll,
            "player_choice": player_choice,
            "player_won": player_won,
            "payout": payout,
            "player_profit": player_profit,
            "house_profit": house_profit,
        }

    def _calculate_payout(self, player_won: bool) -> float:
        if player_won:
            return self.bet_amount * self.payout_multiplier
        return 0.0


class ModifiedPayoutGame(DiceGame):
    def __init__(self, sides: int = 6, bet_amount: float = 1.0, payout_multiplier: float = 5.7):
        super().__init__(sides, bet_amount)
        self.payout_multiplier = payout_multiplier

    def _calculate_payout(self, player_won: bool) -> float:
        if player_won:
            return self.bet_amount * self.payout_multiplier
        return 0.0


class NormalDistributionGame(DiceGame):
    def __init__(
        self,
        sides: int = 6,
        bet_amount: float = 1.0,
        mean_multiplier: float = 5.0,
        std_multiplier: float = 1.5,
        min_multiplier: float = 0.0,
        max_multiplier: float = 10.0,
    ):
        super().__init__(sides, bet_amount)
        self.mean_multiplier = mean_multiplier
        self.std_multiplier = std_multiplier
        self.min_multiplier = min_multiplier
        self.max_multiplier = max_multiplier

    def play(self) -> Dict[str, float]:
        player_choice = np.random.randint(1, self.sides + 1)
        dice_roll = np.random.randint(1, self.sides + 1)
        player_won = dice_roll == player_choice

        if player_won:
            multiplier = np.random.normal(self.mean_multiplier, self.std_multiplier)
            multiplier = np.clip(multiplier, self.min_multiplier, self.max_multiplier)
            multiplier = max(0.0, multiplier)
            payout = self.bet_amount * multiplier
        else:
            payout = 0.0

        player_profit = payout - self.bet_amount
        house_profit = self.bet_amount - payout
        return {
            "player_bet": self.bet_amount,
            "dice_roll": dice_roll,
            "player_choice": player_choice,
            "player_won": player_won,
            "payout": payout,
            "player_profit": player_profit,
            "house_profit": house_profit,
        }

    def _calculate_payout(self, player_won: bool) -> float:
        return 0.0


class Lucky9Game:
    base_deck = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9] * 4 + [0] * 16, dtype=float)

    def __init__(self, bet_amount: float = 1.0, payout_multiplier: float = 2.0):
        self.bet_amount = bet_amount
        self.payout_multiplier = payout_multiplier

    @classmethod
    def build_deck(cls) -> np.ndarray:
        deck = np.random.permutation(cls.base_deck)
        return deck

    @staticmethod
    def draw_from_deck(deck: np.ndarray, count: int = 1) -> (np.ndarray, np.ndarray):
        drawn = deck[:count]
        remainder = deck[count:]
        return drawn, remainder

    @staticmethod
    def hand_total(cards: np.ndarray) -> int:
        return int(cards.sum() % 10)

    def resolve(self, player_cards: np.ndarray, dealer_cards: np.ndarray) -> Dict[str, float]:
        player_total = self.hand_total(player_cards)
        dealer_total = self.hand_total(dealer_cards)
        player_won = player_total > dealer_total
        tie = player_total == dealer_total

        if tie:
            payout = self.bet_amount
        elif player_won:
            payout = self.bet_amount * self.payout_multiplier
        else:
            payout = 0.0

        player_profit = payout - self.bet_amount
        house_profit = self.bet_amount - payout

        return {
            "player_bet": self.bet_amount,
            "player_cards": player_cards.tolist(),
            "dealer_cards": dealer_cards.tolist(),
            "player_total": player_total,
            "dealer_total": dealer_total,
            "player_won": player_won,
            "tie": tie,
            "payout": payout,
            "player_profit": player_profit,
            "house_profit": house_profit,
        }

    def play(self) -> Dict[str, float]:
        deck = self.build_deck()
        player_draw, deck = self.draw_from_deck(deck, 2)
        dealer_draw, deck = self.draw_from_deck(deck, 2)
        return self.resolve(player_draw, dealer_draw)


class SlotMachineGame:
    """
    Simple 3-reel slot:
    - Weighted symbols per reel (rarer symbols pay more)
    - Pays on triples only; no double/any-7 wins
    Designed with a small house edge; a small forced-win chance keeps occasional wins.
    """

    def __init__(self, bet_amount: float = 1.0):
        self.bet_amount = bet_amount
        self.symbols = np.array(["A", "B", "C", "D", "7", "BAR"], dtype=str)
        # Distinct appearance rates (sum to 1 after normalization)
        self.weights = np.array([0.30, 0.24, 0.18, 0.12, 0.10, 0.06], dtype=float)
        self.weights = self.weights / self.weights.sum()
        self.triple_multipliers = {"A": 2.0, "B": 3.0, "C": 5.0, "D": 8.0, "7": 15.0, "BAR": 25.0}
        self.force_win_chance = 0.08

    def play(self) -> Dict[str, float]:
        if np.random.rand() < self.force_win_chance:
            symbol = np.random.choice(list(self.triple_multipliers.keys()))
            spin = np.array([symbol, symbol, symbol])
        else:
            spin = np.random.choice(self.symbols, size=3, p=self.weights)
        unique, counts = np.unique(spin, return_counts=True)
        max_idx = counts.argmax()
        symbol = unique[max_idx]
        count = counts[max_idx]

        multiplier = 0.0
        if count == 3:
            multiplier = self.triple_multipliers.get(symbol, 2.0)

        payout = self.bet_amount * multiplier
        player_profit = payout - self.bet_amount
        house_profit = self.bet_amount - payout

        return {
            "player_bet": self.bet_amount,
            "player_won": payout > 0,
            "spin_result": spin.tolist(),
            "multiplier": multiplier,
            "payout": payout,
            "player_profit": player_profit,
            "house_profit": house_profit,
        }

