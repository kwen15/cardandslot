from flask import Flask, render_template, request, jsonify
from pathlib import Path
import numpy as np

# Running as a module-less script, so use absolute imports within the folder
from simulation import run_games, calculate_statistics
from games import calculate_house_edge, Lucky9Game, SlotMachineGame


def create_app():
    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

    GAME_CHOICES = [
        ("fair", "Fair Game"),
        ("tweaked", "Reduced Payout"),
        ("weighted", "Weighted Probabilities"),
        ("modified_payout", "Modified Payout"),
        ("normal_dist", "Normal Distribution"),
        ("lucky9", "Lucky 9 (cards)"),
        ("slot_machine", "Slot Machine"),
    ]

    @app.route("/", methods=["GET"])
    def home():
        return render_template("home.html")

    @app.route("/about", methods=["GET"])
    def about():
        return render_template("about.html")

    @app.route("/play", methods=["GET"])
    def play():
        return render_template("play.html")

    @app.route("/run-simulation", methods=["GET"])
    def run_simulation_page():
        return render_template("simulate.html", game_choices=GAME_CHOICES)

    @app.route("/api/roll", methods=["POST"])
    def api_roll():
        data = request.get_json() or {}
        bet_color = (data.get("bet_color") or "red").lower()
        bet_amount = float(data.get("bet_amount") or 1.0)
        mode = (data.get("mode") or "fair").lower()
        chosen_prob = float(data.get("chosen_prob") or 0.18)

        colors = ["red", "blue", "green", "yellow", "pink", "white"]
        if bet_color not in colors:
            return jsonify({"error": "invalid bet color"}), 400

        if mode == "tweaked":
            chosen_p = max(0.05, min(chosen_prob, 0.3))
            remaining = (1.0 - chosen_p) / (len(colors) - 1)
            probs = [remaining] * len(colors)
            probs[colors.index(bet_color)] = chosen_p
            multipliers = {0: 0.0, 1: 0.9, 2: 1.8, 3: 2.7}
        elif mode == "weighted":
            chosen_p = max(0.05, min(chosen_prob, 0.3))
            remaining = (1.0 - chosen_p) / (len(colors) - 1)
            probs = [remaining] * len(colors)
            probs[colors.index(bet_color)] = chosen_p
            multipliers = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
        else:
            probs = [1 / len(colors)] * len(colors)
            multipliers = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}

        dice = np.random.choice(colors, size=3, p=probs)
        matches = int(sum(c == bet_color for c in dice))
        payout = bet_amount * multipliers.get(matches, 0.0)
        player_profit = payout - bet_amount
        house_profit = bet_amount - payout

        return jsonify(
            {
                "dice": dice.tolist(),
                "matches": matches,
                "payout": round(payout, 2),
                "player_profit": round(player_profit, 2),
                "house_profit": round(house_profit, 2),
                "mode": mode,
                "bet_color": bet_color,
                "probabilities": probs,
            }
        )

    @app.route("/api/lucky9", methods=["POST"])
    def api_lucky9():
        data = request.get_json() or {}
        bet_amount = float(data.get("bet_amount") or 10.0)
        payout_multiplier = float(data.get("payout_multiplier") or 2.0)

        game = Lucky9Game(bet_amount=bet_amount, payout_multiplier=payout_multiplier)
        result = game.play()

        return jsonify(
            {
                "player_cards": result["player_cards"],
                "dealer_cards": result["dealer_cards"],
                "player_total": result["player_total"],
                "dealer_total": result["dealer_total"],
                "player_won": result["player_won"],
                "tie": result["tie"],
                "payout": round(result["payout"], 2),
                "player_profit": round(result["player_profit"], 2),
                "house_profit": round(result["house_profit"], 2),
                "payout_multiplier": payout_multiplier,
                "bet_amount": bet_amount,
            }
        )

    @app.route("/api/lucky9/peek", methods=["POST"])
    def api_lucky9_peek():
        data = request.get_json() or {}
        bet_amount = float(data.get("bet_amount") or 10.0)
        payout_multiplier = float(data.get("payout_multiplier") or 2.0)

        game = Lucky9Game(bet_amount=bet_amount, payout_multiplier=payout_multiplier)
        deck = game.build_deck()
        player_cards, deck = game.draw_from_deck(deck, 2)

        return jsonify(
            {
                "player_cards": player_cards.tolist(),
                "player_total": int(game.hand_total(player_cards)),
                "deck": deck.tolist(),
            }
        )

    @app.route("/api/lucky9/draw", methods=["POST"])
    def api_lucky9_draw():
        data = request.get_json() or {}
        deck = np.array(data.get("deck") or [], dtype=float)
        player_cards = np.array(data.get("player_cards") or [], dtype=float)

        if len(deck) == 0:
            return jsonify({"error": "deck empty"}), 400

        drawn, deck = Lucky9Game.draw_from_deck(deck, 1)
        player_cards = np.concatenate([player_cards, drawn])
        return jsonify(
            {
                "player_cards": player_cards.tolist(),
                "player_total": int(Lucky9Game.hand_total(player_cards)),
                "deck": deck.tolist(),
                "drawn": drawn.tolist(),
            }
        )

    @app.route("/api/lucky9/resolve", methods=["POST"])
    def api_lucky9_resolve():
        data = request.get_json() or {}
        bet_amount = float(data.get("bet_amount") or 10.0)
        payout_multiplier = float(data.get("payout_multiplier") or 2.0)
        player_cards = np.array(data.get("player_cards") or [], dtype=float)
        dealer_cards = np.array(data.get("dealer_cards") or [], dtype=float)
        deck = np.array(data.get("deck") or [], dtype=float)

        if len(player_cards) < 2:
            return jsonify({"error": "need at least two player cards"}), 400

        # If dealer cards not provided, draw two fresh from remaining deck
        if len(dealer_cards) < 2:
            drawn, remaining = Lucky9Game.draw_from_deck(deck, 2)
            dealer_cards = drawn
            deck = remaining

        game = Lucky9Game(bet_amount=bet_amount, payout_multiplier=payout_multiplier)
        result = game.resolve(player_cards, dealer_cards)

        return jsonify(
            {
                "player_cards": result["player_cards"],
                "dealer_cards": result["dealer_cards"],
                "player_total": result["player_total"],
                "dealer_total": result["dealer_total"],
                "player_won": result["player_won"],
                "tie": result["tie"],
                "payout": round(result["payout"], 2),
                "player_profit": round(result["player_profit"], 2),
                "house_profit": round(result["house_profit"], 2),
                "payout_multiplier": payout_multiplier,
                "bet_amount": bet_amount,
            }
        )

    @app.route("/api/slot/spin", methods=["POST"])
    def api_slot_spin():
        data = request.get_json() or {}
        bet_amount = float(data.get("bet_amount") or 1.0)
        game = SlotMachineGame(bet_amount=bet_amount)
        result = game.play()
        return jsonify(
            {
                "spin": result["spin_result"],
                "multiplier": result["multiplier"],
                "payout": round(result["payout"], 2),
                "player_profit": round(result["player_profit"], 2),
                "house_profit": round(result["house_profit"], 2),
            }
        )

    @app.route("/simulate", methods=["POST"])
    def simulate():
        form = request.form
        selected = form.getlist("games")
        num_simulations = int(float(form.get("num_simulations", 5000)))
        bet_amount = float(form.get("bet_amount", 1.0))

        params = {
            "fair": "fair" in selected,
            "tweaked": "tweaked" in selected,
            "weighted": "weighted" in selected,
            "modified_payout": "modified_payout" in selected,
            "normal_dist": "normal_dist" in selected,
            "lucky9": "lucky9" in selected,
            "slot_machine": "slot_machine" in selected,
            "tweaked_payout": float(form.get("tweaked_payout", 5.0)),
            "weighted_prob": float(form.get("weighted_prob", 0.12)),
            "modified_payout": float(form.get("modified_payout", 5.7)),
            "normal_mean": float(form.get("normal_mean", 5.0)),
            "normal_std": float(form.get("normal_std", 1.5)),
            "lucky9_payout": float(form.get("lucky9_payout", 2.0)),
        }

        results = run_games(num_simulations, bet_amount, params)
        stats_rows = []
        chart_series = []
        metrics_series = []
        for label, df in results.items():
            stats = calculate_statistics(df)
            theoretical_edge = ""
            if label == "Reduced Payout":
                theoretical_edge = f"{calculate_house_edge(1/6, params['tweaked_payout']):.2f}%"
            chart_series.append(
                {
                    "label": label,
                    "data": [
                        {"x": int(row.game_number), "y": float(row.cumulative_player_profit)}
                        for row in df[["game_number", "cumulative_player_profit"]].itertuples()
                    ],
                }
            )
            stats_rows.append(
                {
                    "game": label,
                    "win_rate": f"{stats['win_rate']*100:.2f}%",
                    "player_roi": f"{stats['player_roi']:.2f}%",
                    "house_roi": f"{stats['house_roi']:.2f}%",
                    "final_player_balance": f"{stats['final_player_balance']:.2f}",
                    "final_house_balance": f"{stats['final_house_balance']:.2f}",
                    "theoretical_edge": theoretical_edge or "N/A",
                }
            )
            metrics_series.append(
                {
                    "label": label,
                    "win_rate": float(f"{stats['win_rate']*100:.2f}"),
                    "player_roi": float(f"{stats['player_roi']:.2f}"),
                    "house_roi": float(f"{stats['house_roi']:.2f}"),
                }
            )

        return render_template(
            "results.html",
            stats_rows=stats_rows,
            num_simulations=num_simulations,
            bet_amount=bet_amount,
            chart_series=chart_series,
            metrics_series=metrics_series,
        )

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)

