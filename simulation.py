"""
Monte Carlo simulation helpers for the Flask project.
"""

import pandas as pd
from typing import Dict

from games import (
    FairDiceGame,
    TweakedDiceGame,
    WeightedProbabilitiesGame,
    ModifiedPayoutGame,
    NormalDistributionGame,
    Lucky9Game,
    SlotMachineGame,
)


def run_simulation(game, num_simulations: int = 10000) -> pd.DataFrame:
    results = []
    for _ in range(num_simulations):
        results.append(game.play())
    df = pd.DataFrame(results)
    df["cumulative_player_profit"] = df["player_profit"].cumsum()
    df["cumulative_house_profit"] = df["house_profit"].cumsum()
    df["game_number"] = range(1, len(df) + 1)
    return df


def run_games(num_simulations: int, bet_amount: float, params: dict) -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}

    if params.get("fair"):
        out["Fair Game"] = run_simulation(FairDiceGame(bet_amount=bet_amount), num_simulations)
    if params.get("tweaked"):
        out["Reduced Payout"] = run_simulation(
            TweakedDiceGame(bet_amount=bet_amount, payout_multiplier=params.get("tweaked_payout", 5.0)),
            num_simulations,
        )
    if params.get("weighted"):
        out["Weighted Probabilities"] = run_simulation(
            WeightedProbabilitiesGame(bet_amount=bet_amount, player_number_weight=params.get("weighted_prob", 0.12)),
            num_simulations,
        )
    if params.get("modified_payout"):
        out["Modified Payout"] = run_simulation(
            ModifiedPayoutGame(bet_amount=bet_amount, payout_multiplier=params.get("modified_payout", 5.7)),
            num_simulations,
        )
    if params.get("normal_dist"):
        out["Normal Distribution"] = run_simulation(
            NormalDistributionGame(
                bet_amount=bet_amount,
                mean_multiplier=params.get("normal_mean", 5.0),
                std_multiplier=params.get("normal_std", 1.5),
            ),
            num_simulations,
        )
    if params.get("lucky9"):
        out["Lucky 9"] = run_simulation(
            Lucky9Game(bet_amount=bet_amount, payout_multiplier=params.get("lucky9_payout", 2.0)),
            num_simulations,
        )
    if params.get("slot_machine"):
        out["Slot Machine"] = run_simulation(SlotMachineGame(bet_amount=bet_amount), num_simulations)
    return out


def calculate_statistics(df: pd.DataFrame) -> Dict[str, float]:
    stats = {
        "total_games": len(df),
        "total_bet": df["player_bet"].sum(),
        "wins": df["player_won"].sum(),
        "losses": (df["player_won"] == False).sum(),
        "win_rate": df["player_won"].mean(),
        "total_player_profit": df["player_profit"].sum(),
        "total_house_profit": df["house_profit"].sum(),
        "avg_player_profit_per_game": df["player_profit"].mean(),
        "avg_house_profit_per_game": df["house_profit"].mean(),
        "final_player_balance": df["cumulative_player_profit"].iloc[-1],
        "final_house_balance": df["cumulative_house_profit"].iloc[-1],
        "max_player_profit": df["cumulative_player_profit"].max(),
        "min_player_profit": df["cumulative_player_profit"].min(),
        "max_house_profit": df["cumulative_house_profit"].max(),
        "min_house_profit": df["cumulative_house_profit"].min(),
    }
    stats["std_player_profit"] = df["player_profit"].std()
    stats["std_house_profit"] = df["house_profit"].std()
    stats["player_roi"] = (stats["total_player_profit"] / stats["total_bet"]) * 100
    stats["house_roi"] = (stats["total_house_profit"] / stats["total_bet"]) * 100
    return stats

