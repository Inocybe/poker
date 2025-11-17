# Poker Bot Tournament System

A comprehensive Python-based poker tournament system where students create AI bots to compete in Texas Hold'em tournaments.

## 🎯 Overview

Students create Python poker bots that compete against each other in automated tournaments. Each bot implements the `PokerBotAPI` interface and must make decisions within a time limit or they automatically fold.

## 📁 Project Structure

```
poker/
├── engine/                 # Core poker game logic
│   ├── cards.py           # Card, deck, and hand evaluation
│   ├── poker_game.py      # Texas Hold'em game engine
│   └── __init__.py
├── players/               # Student bot directory
│   ├── random_bot.py      # Example random bot
│   ├── conservative_bot.py # Example tight bot
│   └── aggressive_bot.py  # Example loose/aggressive bot
├── logs/                  # Tournament logs and results
├── bot_api.py            # Bot interface and helper functions
├── bot_manager.py        # Bot loading and execution management
├── tournament.py         # Tournament structure and management
├── tournament_runner.py  # Main tournament execution
└── README.md
```

## 🚀 Quick Start

### 1. Run a Tournament

```bash
# Basic tournament with default settings
python tournament_runner.py

# Custom tournament settings
python tournament_runner.py --starting-chips 2000 --small-blind 20 --big-blind 40 --time-limit 15.0
```

### 2. Create Your Bot

Copy the template and implement your strategy:

```bash
cp players/bot_template.py players/my_bot.py
```

Edit `my_bot.py` and rename the class:

```python
class MyAwesomeBot(PokerBotAPI):
    def get_action(self, game_state, hole_cards, legal_actions, min_bet, max_bet):
        # Your poker strategy here!
        return PlayerAction.CALL, 0
```

## 🤖 Bot API Reference

### Required Methods

Every bot must implement these methods:

```python
def get_action(self, game_state, hole_cards, legal_actions, min_bet, max_bet) -> tuple:
    """
    Make a decision about what action to take.
    
    Args:
        game_state: Current game state (pot, bets, community cards, etc.)
        hole_cards: Your two hole cards
        legal_actions: List of legal actions you can take
        min_bet: Minimum raise amount
        max_bet: Maximum bet (your chips + current bet)
    
    Returns:
        tuple: (PlayerAction, amount)
        - PlayerAction.FOLD: (PlayerAction.FOLD, 0)
        - PlayerAction.CHECK: (PlayerAction.CHECK, 0) 
        - PlayerAction.CALL: (PlayerAction.CALL, 0)
        - PlayerAction.RAISE: (PlayerAction.RAISE, total_bet_amount)
        - PlayerAction.ALL_IN: (PlayerAction.ALL_IN, 0)
    """

def hand_complete(self, game_state, hand_result):
    """
    Called when a hand finishes. Use this to learn from results.
    
    Args:
        game_state: Final game state
        hand_result: Dictionary with winners, winnings, etc.
    """
```

### Helper Functions

Use the `GameInfoAPI` class for useful calculations:

```python
from bot_api import GameInfoAPI

# Calculate pot odds
pot_odds = GameInfoAPI.get_pot_odds(game_state.pot, amount_to_call)

# Get position information
position_info = GameInfoAPI.get_position_info(game_state, self.name)

# Check if heads-up
is_heads_up = GameInfoAPI.is_heads_up(game_state)

# Get opponent list
opponents = GameInfoAPI.get_active_opponents(game_state, self.name)
```

### Game State Information

The `game_state` object contains:

- `pot`: Current pot size
- `community_cards`: List of community cards dealt so far
- `current_bet`: Current highest bet amount
- `player_chips`: Dict of player name -> chip count
- `player_bets`: Dict of player name -> current bet amount
- `active_players`: List of players still in the hand
- `round_name`: "preflop", "flop", "turn", or "river"
- `big_blind`, `small_blind`: Blind amounts

## ⚙️ Tournament Settings

Customize tournaments by modifying `TournamentSettings`:

```python
settings = TournamentSettings(
    starting_chips=1000,           # Starting chip count
    small_blind=10,                # Initial small blind
    big_blind=20,                  # Initial big blind
    blind_increase_interval=10,    # Hands between blind increases
    blind_increase_factor=1.5,     # Blind multiplier
    time_limit_per_action=10.0,    # Seconds per decision
    max_players_per_table=6,       # Max players per table
    min_players_per_table=2        # Min players per table
)
```

## 🛡️ Error Handling & Timeouts

- **Time Limit**: Bots have a configurable time limit (default 10 seconds) per action
- **Timeout Penalty**: Bots that timeout automatically fold
- **Error Handling**: Bots with errors automatically fold  
- **Disqualification**: Bots are disqualified after too many errors/timeouts
- **Invalid Actions**: Invalid actions are converted to folds

## 📊 Results & Logging

Tournaments generate detailed logs and results:

- **Console Output**: Live tournament progress
- **Log Files**: Detailed logs saved to `logs/tournament_TIMESTAMP.log`
- **Results JSON**: Complete results saved to `logs/results_TIMESTAMP.json`
- **Hand Histories**: Last 50 hands saved with complete action sequences

## 🎓 Student Assignment Ideas

### Beginner Level
1. **Simple Strategy Bot**: Implement basic tight/loose strategies
2. **Hand Strength Evaluator**: Create better hand evaluation functions
3. **Position-Aware Bot**: Adjust play based on table position

### Intermediate Level  
1. **Opponent Modeling**: Track opponent patterns and adjust strategy
2. **Pot Odds Calculator**: Make mathematically correct calling decisions
3. **Bluffing Bot**: Implement strategic bluffing based on game situation

### Advanced Level
1. **Monte Carlo Simulation**: Use simulation to estimate winning probabilities
2. **Game Theory Optimal**: Implement GTO-based strategies
3. **Dynamic Strategy**: Adjust strategy based on tournament stage and stack sizes

## 🔧 Development Tools

### Test Your Bot
```bash
# Run tournament with just your bot and examples
python tournament_runner.py --players-dir players
```

### Validate Bot Files
```python
from bot_manager import validate_bot_file

is_valid, message = validate_bot_file("players/my_bot.py")
print(f"Bot valid: {is_valid}, Message: {message}")
```

### Debug Mode
Add logging to your bot for debugging:

```python
class MyBot(PokerBotAPI):
    def get_action(self, game_state, hole_cards, legal_actions, min_bet, max_bet):
        self.logger.info(f"My cards: {hole_cards}, Pot: {game_state.pot}")
        # ... your strategy
```

## 🏆 Tournament Formats

Currently supports:
- **Freeze-out**: No rebuys, play until one player remains
- **Single Elimination**: Coming soon
- **Round Robin**: Coming soon

## 📚 Poker Concepts for Students

### Hand Rankings (Strongest to Weakest)
1. Royal Flush (A-K-Q-J-10 suited)
2. Straight Flush (5 consecutive suited cards)
3. Four of a Kind
4. Full House (3 of a kind + pair)
5. Flush (5 suited cards)
6. Straight (5 consecutive cards)
7. Three of a Kind
8. Two Pair
9. One Pair
10. High Card

### Key Poker Concepts
- **Position**: Acting later is advantageous
- **Pot Odds**: Compare bet cost to potential winnings
- **Hand Selection**: Not all starting hands are worth playing
- **Betting Patterns**: What opponents' bets tell you about their hands
- **Bluffing**: Betting with weak hands to make opponents fold
- **Tournament Strategy**: Adjust play based on chip stacks and blinds

## 🚨 Common Pitfalls for Students

1. **Taking Too Long**: Always return within the time limit
2. **Invalid Actions**: Check that your action is in `legal_actions`
3. **Wrong Return Format**: Must return `(PlayerAction, amount)` tuple
4. **Bet Sizing**: For raises, specify the **total** bet amount, not additional
5. **Exception Handling**: Wrap risky code in try/catch blocks

## 💡 Tips for Success

1. **Start Simple**: Begin with basic strategies before adding complexity
2. **Test Frequently**: Run small tournaments to test your bot
3. **Log Everything**: Use logging to understand your bot's decisions
4. **Study Opponents**: Track opponent patterns in `hand_complete()`
5. **Mathematical Approach**: Use pot odds and probabilities
6. **Adapt Strategy**: Adjust based on tournament stage and position

## 🔍 Example Bot Analysis

The included example bots demonstrate different strategies:

- **RandomBot**: Makes random legal decisions (baseline)
- **ConservativeBot**: Only plays premium hands, bets conservatively
- **AggressiveBot**: Plays many hands, bets and raises frequently

Study these examples to understand different approaches to poker AI!

---

**Good luck creating your poker bot!** 🃏🤖
