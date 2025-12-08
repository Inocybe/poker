from typing import List, Dict, Any
import random


from bot_api import PokerBotAPI, PlayerAction, GameInfoAPI
from engine.cards import Card, Rank, HandEvaluator
from engine.poker_game import GameState


class LevBot(PokerBotAPI):


    
    def __init__(self, name: str):
        super().__init__(name)
        self.bot_name = "lev1_bot"

        self.hands_played = 0
        self.hands_won = 0

        """preflop variables"""
        self.raise_frequency = 0.2  # Default raise frequency
        self.play_frequency = 0.6   # Default play frequency
        self.premium_hand_play_frequency = 1
        self.raise_amount_multiplier = 0.3 # Start raise amount at the same amount as big blind
        self.premium_hand_bet_amount_multiplier = 2.5 # Amount to raise depeneding on good hands
        
        """postflop variables"""
        # variables that determine playing and raising and stuff
        self.strong_draw_play_rate = 0.7

        self.is_strong_pot_play_rate = 0.3

        self.good_hand_play_rate = 0.8
        self.great_hand_play_rate = 1.0
        
        self.good_hand_and_good_pot_play_rate = 0.5

        ##self.bluff_rate = 0.5 no bluffing, yet


        # Define strong starting hands
        self.premium_hands = [
            (Rank.ACE, Rank.ACE), (Rank.KING, Rank.KING), (Rank.QUEEN, Rank.QUEEN),
            (Rank.JACK, Rank.JACK), (Rank.TEN, Rank.TEN), (Rank.NINE, Rank.NINE),
            (Rank.ACE, Rank.KING), (Rank.ACE, Rank.QUEEN), (Rank.ACE, Rank.JACK),
            (Rank.KING, Rank.QUEEN), (Rank.KING, Rank.JACK), (Rank.QUEEN, Rank.JACK)
        ]
    




    def get_action(self, game_state: GameState, hole_cards: List[Card], 
                   legal_actions: List[PlayerAction], min_bet: int, max_bet: int) -> tuple:
        """
        Decide what action to take given the current game state.
        
        Args:
            game_state: Current state of the poker game
            hole_cards: Your two hole cards
            legal_actions: List of actions you can legally take
            min_bet: Minimum bet amount (for raises)
            max_bet: Maximum bet amount (your remaining chips + current bet)
        
        Returns:
            tuple: (PlayerAction, amount)
            - For FOLD, CHECK, CALL, ALL_IN: amount should be 0
            - For RAISE: amount should be the total bet amount (not additional amount)
        
        Examples:
            return (PlayerAction.FOLD, 0)
            return (PlayerAction.CALL, 0)  
            return (PlayerAction.RAISE, 100)  # Raise to 100 total
            return (PlayerAction.ALL_IN, 0)
        """

        if game_state.round_name == "preflop":
            return self._preflop_strategy(game_state, hole_cards, legal_actions, min_bet, max_bet)
        else:
            return self._postflop_strategy(game_state, hole_cards, legal_actions, min_bet, max_bet)
        

    
    def _preflop_strategy(self, game_state: GameState, hole_cards: List[Card], legal_actions: List[PlayerAction], 
                          min_bet: int, max_bet: int) -> tuple:
        

        premium_starting_hand = self._is_premium_starting_hand(hole_cards)
        pair_starting_hand = self._is_premium_starting_hand(hole_cards)

        # checking if I am the big blind
        if max(game_state.player_bets.values()) == game_state.current_bet:
            pass


        #TODO IF GET REALLY GOOD STARTING HAND, CHANGE THESE VARS : 
        #Important to remember this PlayerAction.CHECK in legal_actions
        #TODO ALSO FOR pair starting hand
        if (pair_starting_hand) or (premium_starting_hand):
            if PlayerAction.CALL in legal_actions:
                return PlayerAction.CALL, 0
            elif PlayerAction.CHECK in legal_actions:
                return PlayerAction.CHECK, 0
            return PlayerAction.FOLD, 0
            #self.raise_amount_multiplier = self.raise_amount_multiplier * self.premium_hand_bet_amount_multiplier
            #self.play_frequency = self.premium_hand_play_frequency


        # random choosing to play even if doesn't have a good starting hand, ya never know what'll happen
        if not random.random() < self.play_frequency:
            return PlayerAction.FOLD, 0


        # High probability of raising
        if PlayerAction.RAISE in legal_actions and random.random() < self.raise_frequency:

            # Raise 3-4x the big blind
            raise_amount = self.raise_amount_multiplier * game_state.big_blind
            raise_amount = self._clamp_raise_amount(game_state, min_bet, max_bet, raise_amount)
            
            
            if self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount) != None:
                return self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount)

    


        if PlayerAction.CALL in legal_actions:
            return PlayerAction.CALL, 0
            
        if PlayerAction.CHECK in legal_actions:
            return PlayerAction.CHECK, 0

        return PlayerAction.FOLD, 0



    def _postflop_strategy(self, game_state: GameState, hole_cards: List[Card], 
                           legal_actions: List[PlayerAction], min_bet: int, max_bet: int) -> tuple:
        """Aggressive post-flop strategy"""
        all_cards = hole_cards + game_state.community_cards
        hand_type, _, _ = HandEvaluator.evaluate_best_hand(all_cards)
        hand_rank = HandEvaluator.HAND_RANKINGS[hand_type]

        strong_draw = self._has_strong_draw(all_cards)
        strong_pot = self._is_strong_pot(all_cards)

        good_hand_rank = hand_rank >= HandEvaluator.HAND_RANKINGS['pair']
        great_hand_rank = hand_rank >= HandEvaluator.HAND_RANKINGS['three_of_a_kind']

        if good_hand_rank and strong_pot:
            if random.random() < self.good_hand_and_good_pot_play_rate:
                if self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount) != None:
                    return self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount)



        # Great hand (three of a kind or better)
        if great_hand_rank:
            if PlayerAction.RAISE in legal_actions and random.random() < great_hand_rank:
                raise_amount = (game_state.pot * self.raise_amount_multiplier)
                raise_amount = self._clamp_raise_amount(game_state, min_bet, max_bet, raise_amount)
                
                if self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount) != None:
                    return self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount)


        # Strong hand (top pair or better)
        if good_hand_rank:
            if PlayerAction.RAISE in legal_actions and random.random() < good_hand_rank:
                raise_amount = (game_state.pot * self.raise_amount_multiplier)
                raise_amount = self._clamp_raise_amount(game_state, min_bet, max_bet, raise_amount)
                
                if self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount) != None:
                    return self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount)




            
        if hand_rank < HandEvaluator.HAND_RANKINGS['pair']:
            if PlayerAction.CALL in legal_actions:
                return PlayerAction.CALL, 0
            if PlayerAction.CHECK in legal_actions:
                return PlayerAction.CHECK, 0
        
        if random.random() < self.raise_frequency:
            raise_amount = game_state.pot / 2
            raise_amount = self._clamp_raise_amount(game_state, min_bet, max_bet, raise_amount)

            if raise_amount > game_state.current_bet:
                return PlayerAction.RAISE, raise_amount

        
        if PlayerAction.CHECK in legal_actions:
            return PlayerAction.CHECK, 0
        
        return PlayerAction.FOLD, 0
    
























    """
    if self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount) != None:
        return self._apply_raise_amount_if_able(game_state, legal_actions, raise_amount)
    """
    def _apply_raise_amount_if_able(self, game_state: GameState, legal_actions: List[PlayerAction], raise_amount: float) -> PlayerAction:
        if raise_amount > game_state.current_bet:
            return PlayerAction.RAISE, raise_amount
        elif PlayerAction.CALL in legal_actions:
            return PlayerAction.CALL, 0
        elif PlayerAction.CHECK in legal_actions:
            return PlayerAction.CHECK, 0
        return None



    def _has_strong_draw(self, all_cards: List[Card]) -> bool:
        """Check for strong drawing hands (flush or open-ended straight)"""
        # Flush draw
        suits = [card.suit for card in all_cards]
        for suit in set(suits):
            if suits.count(suit) == 4:
                return True
        
        # Open-ended straight draw
        ranks = sorted(list(set(card.rank.value for card in all_cards)))
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] == 3 and len(ranks) >=4 :
                return True
            if set(ranks).issuperset({2,3,4,5}) or set(ranks).issuperset({14,2,3,4}):
                 return True
        return False
    
    def _is_strong_pot(self, community_cards):
        # Check if there is 3 of the same suit, it is dangerous for us to play because someone could have a flush
        suits = [card.suit for card in community_cards]
        for suit in set(suits):
            if suits.count(suit) == 3 or suits.count(suit) == 4:
                return True

        # Open-ended straight draw
        ranks = sorted(list(set(card.rank.value for card in community_cards)))
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] == 3 and len(ranks) >=4 :
                return True
            if set(ranks).issuperset({2,3,4,5}) or set(ranks).issuperset({14,2,3,4}):
                 return True
        return False
    
    def _is_premium_starting_hand(self, hole_cards: List[Card]) -> bool:
        card1, card2 = hole_cards
        
        # Check if we have a premium hand
        hand_tuple1 = (card1.rank, card2.rank)
        hand_tuple2 = (card2.rank, card1.rank)  # Check both orders

        return (hand_tuple1 in self.premium_hands or 
                     hand_tuple2 in self.premium_hands)
    
    
    def _is_pair_starting_hand(self, hold_hards: List[Card]) -> bool:
        card1, card2 = hold_hards

        return (card1.rank == card2.rank)
    
    def _clamp_raise_amount(self, game_state: GameState, min_bet: float, max_bet: float, amount: float) -> float:
        # Bet half pot on a draw
        raise_amount = min(amount, max_bet)
        raise_amount = max(raise_amount, min_bet)
        
        return raise_amount


    def hand_complete(self, game_state: GameState, hand_result: Dict[str, any]):
        """
        Called when a hand is complete. Use this to learn from the results.
        
        Args:
            game_state: Final game state
            hand_result: Dictionary containing:
                - 'winners': List of winning players
                - 'winning_hands': Dict of player -> best hand
                - 'pot_distribution': Dict of player -> winnings
                - 'showdown_hands': Dict of all revealed hands (if showdown)
        """
        pass

    def tournament_start(self, players: List[str], starting_chips: int):
        super().tournament_start(players, starting_chips)
        """
        if len(players) <= 4:
            self.raise_frequency = 0.33
            self.play_frequency = 0.3
        elif len(players) >= 8:
            self.raise_frequency = 0.4
            self.play_frequency = 0.15
        """