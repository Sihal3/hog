"""The Game of Hog."""

from dice import six_sided, make_test_dice
from ucb import main, trace, interact
from math import log2
from fractions import Fraction
from best_move_w_prob import best_move
from best_score import best_score

GOAL = 100  # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################


def roll_dice(num_rolls, dice=six_sided):
    """Simulate rolling the DICE exactly NUM_ROLLS > 0 times. Return the sum of
    the outcomes unless any of the outcomes is 1. In that case, return 1.

    num_rolls:  The number of dice rolls that will be made.
    dice:       A function that simulates a single dice roll outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    # BEGIN PROBLEM 1

    sum = 0
    one_rolled = False
    for _ in range(num_rolls):
        roll = dice()
        if roll == 1:
           one_rolled = True
        sum += roll

    return 1 if one_rolled else sum

    # END PROBLEM 1


def tail_points(opponent_score):
    """Return the points scored by rolling 0 dice according to Pig Tail.

    opponent_score:   The total score of the other player.
    """
    # BEGIN PROBLEM 2
    ones = opponent_score % 10
    tens = (opponent_score // 10) % 10
    return 2 * abs(tens - ones) + 1
    # END PROBLEM 2


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Return the points scored on a turn rolling NUM_ROLLS dice when the
    opponent has OPPONENT_SCORE points.

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the other player.
    dice:            A function that simulates a single dice roll outcome.
    """
    # Leave these assert statements here; they help check for errors.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice in take_turn.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    # BEGIN PROBLEM 3
    return tail_points(opponent_score) if num_rolls == 0 else roll_dice(num_rolls, dice)
    # END PROBLEM 3


def simple_update(num_rolls, player_score, opponent_score, dice=six_sided):
    """Return the total score of a player who starts their turn with
    PLAYER_SCORE and then rolls NUM_ROLLS DICE, ignoring Square Swine.
    """
    return player_score + take_turn(num_rolls, opponent_score, dice)


def square_update(num_rolls, player_score, opponent_score, dice=six_sided):
    """Return the total score of a player who starts their turn with
    PLAYER_SCORE and then rolls NUM_ROLLS DICE, *including* Square Swine.
    """
    score = player_score + take_turn(num_rolls, opponent_score, dice)
    if perfect_square(score):  # Implement perfect_square
        return next_perfect_square(score)  # Implement next_perfect_square
    else:
        return score


# BEGIN PROBLEM 4
def perfect_square(score) -> bool:
    """
    Returns a bool value about whether SCORE is a perfect square or not.
    """
    return ((score ** 0.5) % 1) == 0  # I'm a bit worried about float math messing this up, but it seems to work.

def next_perfect_square(score) -> int:
    """
    Returns the closest integer square above SCORE.
    """
    return (int(score ** 0.5) + 1) ** 2
# END PROBLEM 4


def always_roll_5(score, opponent_score):
    """A strategy of always rolling 5 dice, regardless of the player's score or
    the oppononent's score.
    """
    return 5


def play(strategy0, strategy1, update,
         score0=0, score1=0, dice=six_sided, goal=GOAL):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first and Player 1's score second.

    E.g., play(always_roll_5, always_roll_5, square_update) simulates a game in
    which both players always choose to roll 5 dice on every turn and the Square
    Swine rule is in effect.

    A strategy function, such as always_roll_5, takes the current player's
    score and their opponent's score and returns the number of dice the current
    player chooses to roll.

    An update function, such as square_update or simple_update, takes the number
    of dice to roll, the current player's score, the opponent's score, and the
    dice function used to simulate rolling dice. It returns the updated score
    of the current player after they take their turn.

    strategy0: The strategy for player0.
    strategy1: The strategy for player1.
    update:    The update function (used for both players).
    score0:    Starting score for Player 0
    score1:    Starting score for Player 1
    dice:      A function of zero arguments that simulates a dice roll.
    goal:      The game ends and someone wins when this score is reached.
    """
    who = 0  # Who is about to take a turn, 0 (first) or 1 (second)
    # BEGIN PROBLEM 5
    while score0 < goal and score1 < goal:
        if who == 0:
            score0 = update(strategy0(score0, score1), score0, score1, dice)
        else:
            assert who == 1, "Something has gone very wrong internally with the turn variable."
            score1 = update(strategy1(score1, score0), score1, score0, dice)
        who = (who + 1) % 2

    # END PROBLEM 5
    return score0, score1


#######################
# Phase 2: Strategies #
#######################


def always_roll(n):
    """Return a player strategy that always rolls N dice.

    A player strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(3)
    >>> strategy(0, 0)
    3
    >>> strategy(99, 99)
    3
    """
    assert n >= 0 and n <= 10
    # BEGIN PROBLEM 6
    def roller(score, opponents_score):
        """A strategy of always rolling N dice, regardless of the player's score or
        the opponent's score.
        """
        return n

    return roller
    # END PROBLEM 6


def catch_up(score, opponent_score):
    """A player strategy that always rolls 5 dice unless the opponent
    has a higher score, in which case 6 dice are rolled.

    >>> catch_up(9, 4)
    5
    >>> strategy(17, 18)
    6
    """
    if score < opponent_score:
        return 6  # Roll one more to catch up
    else:
        return 5


def is_always_roll(strategy, goal=GOAL):
    """Return whether strategy always chooses the same number of dice to roll.

    >>> is_always_roll(always_roll_5)
    True
    >>> is_always_roll(always_roll(3))
    True
    >>> is_always_roll(catch_up)
    False
    """
    # BEGIN PROBLEM 7
    past_roll = strategy(0,0)

    score = 0
    while score < goal:
        opponent_score = 0
        while opponent_score < goal:
            if past_roll != strategy(score, opponent_score):
                return False
            opponent_score += 1
        score += 1

    return True
    # END PROBLEM 7


def make_averaged(original_function, total_samples=1000):
    """Return a function that returns the average value of ORIGINAL_FUNCTION
    called TOTAL_SAMPLES times.

    To implement this function, you will have to use *args syntax.

    >>> dice = make_test_dice(4, 2, 5, 1)
    >>> averaged_dice = make_averaged(roll_dice, 40)
    >>> averaged_dice(1, dice)  # The avg of 10 4's, 10 2's, 10 5's, and 10 1's
    3.0
    """
    # BEGIN PROBLEM 8
    def averaged(*args):
        sum = 0
        for _ in range(total_samples):
            sum += original_function(*args)
        return sum/total_samples

    return averaged
    # END PROBLEM 8


def max_scoring_num_rolls(dice=six_sided, total_samples=1000):
    """Return the number of dice (1 to 10) that gives the highest average turn score
    by calling roll_dice with the provided DICE a total of TOTAL_SAMPLES times.
    Assume that the dice always return positive outcomes.

    >>> dice = make_test_dice(1, 6)
    >>> max_scoring_num_rolls(dice)
    1
    """
    # BEGIN PROBLEM 9
    avg_roll = make_averaged(roll_dice, total_samples)

    max = 0
    for num_rolls in range(1,11):
        avg_sum = avg_roll(num_rolls, dice)
        if avg_sum > max:
            max = avg_sum
            best_roll = num_rolls

    return best_roll
    # END PROBLEM 9


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1, square_update)
    if score0 > score1:
        return 0
    else:
        return 1


def average_win_rate(strategy, baseline=always_roll(6), total_samples=1000):
    """Return the average win rate of STRATEGY against BASELINE. Averages the
    winrate when starting the game as player 0 and as player 1.
    """
    win_rate_as_player_0 = 1 - make_averaged(winner, total_samples=total_samples)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner, total_samples=total_samples)(baseline, strategy)

    return (win_rate_as_player_0 + win_rate_as_player_1) / 2


def run_experiments(total_samples=1000):
    """Run a series of strategy experiments and report results."""
    six_sided_max = max_scoring_num_rolls(six_sided, total_samples=total_samples)
    print('Max scoring num rolls for six-sided dice:', six_sided_max)

    print('always_roll(6) win rate:', average_win_rate(always_roll(6),total_samples=total_samples))  # near 0.5
    print('catch_up win rate:', average_win_rate(catch_up,total_samples=total_samples))
    print('always_roll(3) win rate:', average_win_rate(always_roll(3),total_samples=total_samples))
    print('always_roll(8) win rate:', average_win_rate(always_roll(8),total_samples=total_samples))

    print('tail_strategy win rate:', average_win_rate(tail_strategy,total_samples=total_samples))
    print('square_strategy win rate:', average_win_rate(square_strategy,total_samples=total_samples))
    print('final_strategy win rate:', average_win_rate(final_strategy,total_samples=total_samples))

    maxnums, max_rate = 0,0
    for i in range(0,105,5):
        for j in range(0,105,5):
            win_rate = average_win_rate(final_strategy_v05(i,j),total_samples=total_samples)
            print(f'final_strategy_v05_{i}-{j} win rate:', win_rate)
            if max_rate < win_rate:
                max_rate = win_rate
                maxnums = str(i)+" "+str(j)
    print(maxnums)
    "*** You may add additional experiments as you wish ***"


def tail_strategy(score, opponent_score, threshold=12, num_rolls=6):
    """This strategy returns 0 dice if Pig Tail gives at least THRESHOLD
    points, and returns NUM_ROLLS otherwise. Ignore score and Square Swine.
    """
    # BEGIN PROBLEM 10
    return 0 if tail_points(opponent_score) >= threshold else num_rolls
    # END PROBLEM 10


def square_strategy(score, opponent_score, threshold=12, num_rolls=6):
    """This strategy returns 0 dice when your score would increase by at least threshold."""
    # BEGIN PROBLEM 11
    return 0 if square_update(0, score, opponent_score)-score >= threshold else num_rolls
    # END PROBLEM 11


def dice_result(n):
    result = [[], []]
    if n == 1:
        result = [[1,2,3,4,5,6], [1]*6]
    else:
        arr = dice_result(n-1)
        for i, sums in enumerate(arr[0]):
            for roll in range(1,7):
                new_roll = 1 if sums == 1 or roll == 1 else sums+roll
                if new_roll in result[0]:
                    result[1][result[0].index(new_roll)] += arr[1][i]
                else:
                    result[0].append(new_roll)
                    result[1].append(arr[1][i])

    total = sum(result[1])
    result[1] = [Fraction(i,total) for i in result[1]]

    if prob_cutoff:
        new_result1 = []
        new_result2 = []
        for i in range(len(result[1])):
            if result[1][i] > prob_cutoff:
                new_result1.append(result[0][i])
                new_result2.append(result[1][i])
        result[0] = new_result1
        result[1] = new_result2

    return result

def square_add(score, roll_sum):
    score = score + roll_sum
    return next_perfect_square(score) if perfect_square(score) else score  # Implement next_perfect_square

def max_prob_calc(num_roll, score, opponent_score, best_move):
    win_prob = Fraction(0, 1)

    if num_roll != 0:
        points = dice_result(num_roll)
    else:
        points = [[tail_points(opponent_score)], [Fraction(1 / 1)]]

    for i, result in enumerate(points[0]):
        if square_add(score, result) >= 100:
            win_prob += 1 * points[1][i]
        else:
            win_prob += (1 - find_best_move(opponent_score, square_add(score, result), best_move)[1]) * points[1][i]

    return win_prob

def max_score_roll(score, opponent_score, best_score=best_score):

    if best_score[score][opponent_score] != -1:
        return best_score[score][opponent_score]

    max_score = 0
    for num_roll in range(0, 11):

        if num_roll != 0:
            rolls = dice_result(num_roll)
            new_points = score+sum([roll * rolls[1][i] for i, roll in enumerate(rolls[0])])
        else:
            new_points = square_add(score, tail_points(opponent_score))

        if new_points > max_score:
            max_score = new_points
            max_roll = num_roll

    best_score[score][opponent_score] = max_roll
    print(f'Best Roll for ({score},{opponent_score}) is to roll {max_roll} dice.')
    return best_score[score][opponent_score]

def find_best_move(score, opponent_score, best_move=best_move):
    assert score < 100 and opponent_score < 100, "score too large"

    if best_move[score][opponent_score] != 0:
        return best_move[score][opponent_score]

    max_prob = Fraction(-1,1)
    for num_roll in range(0,11):

        win_prob = max_prob_calc(num_roll, score, opponent_score, best_move)

        if win_prob > max_prob:
            max_prob = win_prob
            max_roll = num_roll

    best_move[score][opponent_score] = [max_roll, max_prob]
    print(f'Best Move for ({score},{opponent_score}) is to roll {max_roll} dice, with a win probablility of {round(float(max_prob),5)}.')
    return best_move[score][opponent_score]

def gen_final_strategy():

    best_move = [[0] * 100 for _ in range(100)]

    for i in reversed(range(100)):
        for j in reversed(range(100)):
            if best_move[i][j] == 0:
                find_best_move(i, j, best_move)

    best_move_w_prob = [[[item[0], round(float(item[1]),5)] for item in row] for row in best_move]
    best_move_wo_prob = [[item[0] for item in row] for row in best_move]

    file_wo_prob = open("best_move.py", 'w')
    file_wo_prob.write("best_move=")
    file_wo_prob.write(str(best_move_wo_prob))

    file_with_prob = open("best_move_w_prob.py", 'w')
    file_with_prob.write("best_move=")
    file_with_prob.write(str(best_move_w_prob))

    for i in range(100):
        for j in range(100):
            print(f"({i}, {j}) - {best_move[i][j][0]}, win_prob={float(best_move[i][j][1])}")

    print(best_move)


    #print(best_move)

# I ran gen_final_strategy, and then copied the result here.
def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.

    I want to be statistically optimal. So I'll just run a tree-search simulation beforehand for every possible score situation
    and then consult an array to decide how many to roll.

    """
    # BEGIN PROBLEM 12
    if best_move[score][opponent_score] != -1:
        return best_move[score][opponent_score][0]
    else:
        return find_best_move(score, opponent_score, )[0]
    # END PROBLEM 12

def gen_final_strategy_v05():

    best_score = [[-1] * 100 for _ in range(100)]

    for i in reversed(range(100)):
        for j in reversed(range(100)):
            if best_score[i][j] == -1:
                best_score[i][j] = max_score_roll(i, j, best_score)

    file= open("best_score.py", 'w')
    file.write("best_score=")
    file.write(str(best_score))

    for i in range(100):
        for j in range(100):
            print(f"({i}, {j}) - {best_score[i][j]}")

    print(best_score)

def final_strategy_v05(loss_switch=10, end_switch=16):

    def strat(score, opponent_score):

        if score < opponent_score + loss_switch:
            return find_best_move(score, opponent_score)[0]
        elif score > GOAL - end_switch:
            return find_best_move(score, opponent_score)[0]
        else:
            return max_score_roll(score, opponent_score)

    return strat





##########################
# Command Line Interface #
##########################

# NOTE: The function in this section does not need to be changed. It uses
# features of Python not yet covered in the course.

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r',nargs='?',const=1000,
                        help='Runs strategy experiments')

    global prob_cutoff
    prob_cutoff = 0.001

    args = parser.parse_args()

    if args.run_experiments:
        run_experiments(total_samples=int(args.run_experiments))



    #gen_final_strategy()
    #gen_final_strategy_v05()


