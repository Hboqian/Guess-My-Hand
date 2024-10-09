import numpy as np

# Shared global variables
PARTNERS = {
    "North": "South",
    "East": "West",
    "South": "North",
    "West": "East",
}
SUIT_ORDER = {"Hearts": 0, "Diamonds": 2, "Clubs": 1, "Spades": 3}
VALUE_ORDER = {
    "2": 7,
    "3": 10,
    "4": 4,
    "5": 5,
    "6": 11,
    "7": 3,
    "8": 2,
    "9": 13,
    "10": 6,
    "J": 1,
    "Q": 9,
    "K": 12,
    "A": 8,
}

def playing(player, deck):
    """
    Playing strategy goes here (what card will the player expose to their partner)
    """
    if not player.hand:
        return None

    print(" ")
    print(f"-------------- Playing: {player.name} -----------------")

    hand_indices = [get_card_index(card) for card in player.hand]
    card_to_play_index = get_max_card(hand_indices)
    return card_to_play_index

def get_card_index(card):
    """
    This function maps cards to an index and scrambles the index.
    """
    # Hash formula that combines suit and value in a less predictable way
    suit = SUIT_ORDER[card.suit]
    value = VALUE_ORDER[card.value]

    index = suit * 13 + value
    return index

def get_max_card(hand_indices):
    """
    Play card with the highest index to create upper bound value.
    """
    max_index = hand_indices.index(max(hand_indices))
    return max_index

def use_max_value_index(player, g_cards):
    """
    Use the upper bound value strategy to inform guess
    """
    # Take card exposed by partner and use it to inform the rest of our guesses
    partner_exposed_card = player.exposed_cards[PARTNERS[player.name]][-1]
    max_index = get_card_index(partner_exposed_card)

    guess_indices = [get_card_index(card) for card in g_cards]

    index_filter = []
    for i, guess_index in enumerate(guess_indices):
        if guess_index<max_index:
            index_filter.append(i)

    below_max_cards = [g_cards[i] for i in index_filter]
    return below_max_cards

def get_guessable_cards(player, cards):
    # Remove cards that in the player's hand
    g_cards = list(set(cards) - set(player.hand))
    # Remove cards that have been exposed in gameplay
    for _, exposed in player.exposed_cards.items():
        g_cards = list(set(g_cards) - set(exposed))
    return g_cards

def get_card_prob(player, g_cards, round):

    # Get constants
    G = 13 - round  # Number of guesses / cards in your partner's hand
    T = len(g_cards)  # Number of cards that are possible guesses
    probs = None

    # Calculate probabilities for different rounds
    if round == 1:
        # First round we won't have any information about previous guesses
        probs = [1 / T] * T
    elif round == 12:
        pass
    else:
        print(f"Guesses: {len(player.guesses[round - 2])}, {player.guesses[round - 2]}")
        print(f"cval: {player.cVals[round - 2]}")

        #todo - Make this work for more than just the previous round of guesses
        probs = []
        C = player.cVals[round-2] # Minus 2 because first round is skipped so index at Round 2 starts at 0.
        guesses = player.guesses[round-2]

        prob_guessed_card = C / (G + 1)  # Probability for each guessed card
        try:
            prob_not_guessed_card = (G + 1 - C) / (T - G)  # Probability for each unguessed card
        except:
            prob_not_guessed_card = 0

        # Normalize probabilities to ensure they sum to 1
        total_prob = prob_guessed_card * G + prob_not_guessed_card * (T - G)
        prob_guessed_card /= total_prob
        prob_not_guessed_card /= total_prob

        for card in g_cards:
            if card in guesses:
                probs.append(prob_guessed_card)
            else:
                probs.append(prob_not_guessed_card)

        # Add a check to ensure the probabilities sum to 1
        total_sum = sum(probs)
        print("total_sum is: " + str(total_sum))
        if total_sum != 1:
            # force to renomrmalize
            probs = [p / total_sum for p in probs]

    return probs

def guessing(player, cards, round):
    """
    Guessing strategy based on ranking guessable cards from highest to lowest probability 
    and selecting top N guesses.

    :param player: The Player object.
    :param cards: List of all Card objects in the game.
    :param round: Integer representing the current round number.
    :return: List of guessed Card objects.
    """
    print(" ")
    print(f"-------------- Guessing: {player.name}, Round: {round} -----------------")

    # Determine the number of guesses needed
    num_guesses = 13 - round
    print(f"Round {round}: Number of guesses needed: {num_guesses}")

    if num_guesses <= 0:
        print(f"Round {round}: No guesses needed.")
        return []

    # Remove cards from list that are not valid guesses for this round.
    g_cards = get_guessable_cards(player, cards)
    print(f"Round {round}: Guessable cards after filtering: {g_cards}")

    # Apply strategy to narrow possible cards
    s_cards = use_max_value_index(player, g_cards)
    print(f"Round {round}: Cards after applying max value index strategy: {s_cards}")

    if not s_cards:
        print(f"Round {round}: No guessable cards available after applying strategy.")
        return []

    # Update probability of possible cards
    p_cards = get_card_prob(player, s_cards, round)
    print(f"Round {round}: Probabilities of guessable cards: {p_cards}")

    if not p_cards or len(p_cards) != len(s_cards):
        print(f"Round {round}: Invalid probability distribution. Assigning uniform probabilities.")
        p_cards = [1 / len(s_cards)] * len(s_cards)

    # Pair each card with its probability
    card_prob_pairs = list(zip(s_cards, p_cards))

    # Sort the pairs based on probability in descending order
    sorted_pairs = sorted(card_prob_pairs, key=lambda pair: pair[1], reverse=True)
    print(f"Round {round}: Sorted guessable cards by probability: {sorted_pairs}")

    # Select the top N cards based on the current round
    selected_guesses = [card for card, prob in sorted_pairs[:num_guesses]]
    print(f"Round {round}: Selected guesses: {selected_guesses}")

    return selected_guesses

