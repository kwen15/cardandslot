You have one new message.

Skip to content
Using Camarines Sur Polytechnic Colleges Mail with screen readers

Conversations
 
Program Policies
Powered by Google
Last account activity: in 5 minutes
Details
# Card and Slot

A Flask-based betting simulation application that provides interactive casino-style games and Monte Carlo simulations to analyze house edge and player outcomes across various game types.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Game Types](#game-types)
- [API Endpoints](#api-endpoints)
- [Simulation Engine](#simulation-engine)
- [License](#license)

## Overview

Card and Slot is an educational and analytical tool designed to demonstrate the mathematical principles behind casino games. The application allows users to play interactive games, run Monte Carlo simulations, and visualize statistical outcomes including win rates, ROI, and cumulative profit over time.

## Features

- Interactive web-based interface for playing casino games
- Multiple game variants with configurable parameters
- Monte Carlo simulation engine for statistical analysis
- Real-time visualization of simulation results
- RESTful API endpoints for game interactions
- Comprehensive statistics including win rate, ROI, and house edge calculations

## Project Structure

```
cardandslot/
├── app. py              # Flask application and route definitions
├── games. py            # Game model implementations
├── simulation.py       # Monte Carlo simulation engine
└── templates/          # HTML templates
    ├── base.html       # Base template with common layout
    ├── home. html       # Landing page
    ├── about.html      # About page
    ├── play.html       # Interactive game interface
    ├── simulate.html   # Simulation configuration page
    ├── results.html    # Simulation results display
    └── index.html      # Index page
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Dependencies

Install the required packages:

```bash
pip install flask numpy pandas
```

### Running the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/kwen15/cardandslot.git
   cd cardandslot
   ```

2. Start the Flask development server:
   ```bash
   python app.py
   ```

3. Access the application at `http://localhost:5000`

## Usage

### Web Interface

Navigate to the application in your browser to access: 

- **Home** (`/`): Landing page with navigation options
- **About** (`/about`): Information about the application
- **Play** (`/play`): Interactive game interface
- **Simulation** (`/run-simulation`): Configure and run Monte Carlo simulations

### Running Simulations

1. Navigate to the simulation page
2. Select the game types to simulate
3. Configure parameters such as number of simulations and bet amount
4. View results including statistical metrics and profit charts

## Game Types

### Dice Games

| Game Type | Description |
|-----------|-------------|
| **Fair Game** | Standard dice game with fair probabilities and full payout multiplier |
| **Reduced Payout** | Dice game with reduced payout multiplier creating house edge |
| **Weighted Probabilities** | Dice game with modified outcome probabilities |
| **Modified Payout** | Dice game with configurable payout multiplier |
| **Normal Distribution** | Payout multiplier drawn from a normal distribution |

### Card Games

| Game Type | Description |
|-----------|-------------|
| **Lucky 9** | Card game where players compete against the dealer to get closest to 9 |

### Slot Games

| Game Type | Description |
|-----------|-------------|
| **Slot Machine** | 3-reel slot machine with weighted symbols and triple payouts |

## API Endpoints

### Dice Roll

```
POST /api/roll
```

**Request Body:**
```json
{
  "bet_color": "red",
  "bet_amount": 1.0,
  "mode": "fair",
  "chosen_prob": 0.18
}
```

**Response:**
```json
{
  "dice":  ["red", "blue", "red"],
  "matches": 2,
  "payout": 2.0,
  "player_profit": 1.0,
  "house_profit": -1.0,
  "mode": "fair",
  "bet_color": "red",
  "probabilities": [0.166, 0.166, 0.166, 0.166, 0.166, 0.166]
}
```

### Lucky 9

```
POST /api/lucky9
```

**Request Body:**
```json
{
  "bet_amount": 10.0,
  "payout_multiplier": 2.0
}
```

### Lucky 9 Peek (View Initial Cards)

```
POST /api/lucky9/peek
```

### Lucky 9 Draw (Draw Additional Card)

```
POST /api/lucky9/draw
```

### Lucky 9 Resolve (Determine Winner)

```
POST /api/lucky9/resolve
```

### Slot Machine Spin

```
POST /api/slot/spin
```

**Request Body:**
```json
{
  "bet_amount": 1.0
}
```

**Response:**
```json
{
  "spin":  ["A", "B", "A"],
  "multiplier": 0.0,
  "payout": 0.0,
  "player_profit": -1.0,
  "house_profit": 1.0
}
```

## Simulation Engine

The simulation engine uses Monte Carlo methods to run thousands of game iterations and compute statistical metrics. 

### Available Statistics

- **Win Rate**: Percentage of games won by the player
- **Player ROI**: Return on investment for the player
- **House ROI**: Return on investment for the house
- **Final Balance**: Cumulative profit/loss at simulation end
- **Theoretical House Edge**: Mathematical advantage (where applicable)

### Configurable Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `num_simulations` | Number of games to simulate | 5000 |
| `bet_amount` | Amount wagered per game | 1.0 |
| `tweaked_payout` | Payout multiplier for reduced payout game | 5.0 |
| `weighted_prob` | Player number probability for weighted game | 0.12 |
| `modified_payout` | Payout multiplier for modified payout game | 5.7 |
| `normal_mean` | Mean multiplier for normal distribution game | 5.0 |
| `normal_std` | Standard deviation for normal distribution game | 1.5 |
| `lucky9_payout` | Payout multiplier for Lucky 9 | 2.0 |

### House Edge Calculation

The theoretical house edge is calculated using the formula: 

```
House Edge = (1 - (Win Probability * Payout Multiplier)) * 100
```

## License

This project is available for educational and analytical purposes. 
README.md
Displaying README.md.
