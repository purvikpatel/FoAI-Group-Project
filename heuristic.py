from curses.ascii import SP
import random
from spy import Spy
import copy
from scipy import spatial
import numpy as np
import utils

class Heuristic:
    def __init__(self, board):
        self.board = board
        self.starting_quantities = Spy()
        self.current_board = self.get_current_board()

    def get_current_board(self):
        current_board = { k: 0 for k in self.starting_quantities.keys() }
        for row in self.board:
            for piece in row:
                current_board[piece] += 1
        return current_board

    def evaluate(self):
        current_board = self.current_board
        starting_quantities = self.starting_quantities
        score = 0
        for key in starting_quantities.keys():
            score += abs(current_board[key] - starting_quantities[key])
        return score

    def get_best_board(self):
        maximum = -1
        bestboard = []
        for board in self.population:
            score = self.evaluate(board)
            if score > maximum:
                maximum = score
                bestboard = board
        return bestboard, maximum

    def random_swap_list(self, list1 , list2):
        r = random.random()
        if r <= 0.5:
            return list1, list2
        return list2, list1

    def compare(self, board1, board2):
        if (self.evaluate(board1) < self.evaluate(board2)):
            return -1
        elif (self.evaluate(board1) > self.evaluate(board2)):
            return 1
        else:
            return 0


class MinMax():
    def __init__(self, board):
        self.board = board
        self.starting_quantities = Spy()
        self.current_board = self.get_current_board()

    def __init__(self, team, depth=None):
        super(MinMax, self).__init__(team=team)
        # rewards for planning the move
        self.kill_reward = 10  # killing an enemy piece
        self.neutral_fight = 2  # a neutral outcome of a fight
        self.winGameReward = 100  # finding the enemy flag
        self.certainty_multiplier = 1.2  # killing known, not guessed, enemy pieces

        # initial maximum depth of the minimax algorithm
        self.ext_depth = depth
        self.max_depth = 2  # standard max depth

        # the matrix table for deciding battle outcomes between two pieces
        self.battleMatrix = utils.get_bm()

    def decide_move(self, state, logic):
        """
        Depending on the amount of enemy pieces left, we are entering the start, mid or endgame
        and planning through the minimax algorithm.
        :return: tuple of tuple positions representing the move
        """
        if self.ext_depth is None:
            self.set_max_depth()  # set max_depth each turn
        else:
            self.max_depth = self.ext_depth
        # make sure a flag win will be discounted by a factor that guarantees a preference towards immediate flag kill
        self.winGameReward = max(self.winGameReward, self.max_depth * self.kill_reward)
        return self.minmax(max_depth=self.max_depth)

    def set_max_depth(self):
        n_alive_enemies = sum(
            [True for piece in self.ordered_opp_pieces if not piece.dead]
        )
        if 7 < n_alive_enemies <= 10:
            # one move each player lookahead
            self.max_depth = 2
        elif 4 <= n_alive_enemies <= 7:
            # two moves each player lookahead
            self.max_depth = 4
        elif n_alive_enemies <= 3:
            # four moves each player lookahead
            self.max_depth = 8

    def minmax(self, max_depth):
        """
        given the maximum depth, copy the known board so far, assign the pieces by random, while still
        respecting the current knowledge, and then decide the move via minimax algorithm.
        :param max_depth: int
        :return: tuple of spatial tuples
        """
        curr_board = copy.deepcopy(self.board)
        curr_board = self.draw_consistent_enemy_setup(curr_board)
        chosen_action = self.max_val(
            curr_board, 0, -float("inf"), float("inf"), max_depth
        )[1]
        return chosen_action

    def max_val(self, board, current_reward, alpha, beta, depth):
        """
        Do the max players step in the minimax algorithm. Check first if the given board is in
        a terminal state. If not, we will do each possible move once and send the process to
        min_val to do the min players step.
        :param board: the current board, numpy array
        :param current_reward: the current value the path has accumulated
        :param alpha: alpha threshold of the minimax alg
        :param beta: beta threshold of the minimax alg
        :param depth: the depth the process is at, integer
        :return: tuple of best value, and a associated best_action (float, tuple)
        """
        # this is what the expectimax agent will think

        # get my possible actions, then shuffle them to ensure randomness when no action
        # stands out as the best
        my_doable_actions = utils.get_poss_moves(board, self.team)
        np.random.shuffle(my_doable_actions)

        # check for terminal-state scenario
        done, won = self.goal_test(my_doable_actions, board, max_val=True)
        if done or depth == 0:
            return current_reward + self.get_terminal_reward(done, won, depth), None

        val = -float("inf")
        best_action = None
        for action in my_doable_actions:
            board, fight_result = self.do_move(
                action, board=board, bookkeeping=False, true_gameplay=False
            )
            temp_reward = current_reward + self.add_temp_reward(fight_result)
            new_val = self.min_val(board, temp_reward, alpha, beta, depth - 1)[0]
            if val < new_val:
                val = new_val
                best_action = action
            if val >= beta:
                self.undo_last_move(board)
                best_action = action
                return val, best_action
            alpha = max(alpha, val)
            board = self.undo_last_move(board)
        return val, best_action

    def min_val(self, board, current_reward, alpha, beta, depth):
        """
        Step of the minimizing player in the minimax algorithm. See max_val for documentation.
        """
        # this is what the opponent will think, the min-player

        # get my possible actions, then shuffle them to ensure randomness when no action
        # stands out as the best
        my_doable_actions = utils.get_poss_moves(board, self.other_team)
        np.random.shuffle(my_doable_actions)

        # check for terminal-state scenario or maximum depth
        done, won = self.goal_test(my_doable_actions, board, max_val=False)
        if done or depth == 0:
            return current_reward + self.get_terminal_reward(done, won, depth), None

        val = float("inf")  # initial value set, so min comparison later possible
        best_action = None
        # iterate through all actions
        for action in my_doable_actions:
            board, fight_result = self.do_move(
                action, board=board, bookkeeping=False, true_gameplay=False
            )
            temp_reward = current_reward - self.add_temp_reward(fight_result)
            new_val = self.max_val(board, temp_reward, alpha, beta, depth - 1)[0]
            if val > new_val:
                val = new_val
                best_action = action
            if val <= alpha:
                self.undo_last_move(board)
                return val, best_action
            beta = min(beta, val)
            board = self.undo_last_move(board)
        return val, best_action

    def add_temp_reward(self, fight_result):
        """
        reward the fight given the outcome of it.
        :param fight_result: integer category of the fight outcome
        :return: reward, float
        """
        # depending on the fight we want to update the current paths value
        temp_reward = 0
        if fight_result is not None:
            if fight_result == 1:  # attacker won
                temp_reward = self.kill_reward
            elif fight_result == 2:  # attacker won, every piece was known before
                temp_reward = int(self.certainty_multiplier * self.kill_reward)
            elif fight_result == 0:  # neutral outcome
                temp_reward = self.neutral_fight  # both pieces die
            elif fight_result == -1:  # attacker lost
                temp_reward = -self.kill_reward
            elif fight_result == -2:  # attacker lost, every piece was known before
                temp_reward = -int(self.certainty_multiplier * self.kill_reward)
        return temp_reward

    def goal_test(self, actions_possible, board, max_val):
        """
        check the board for whether a flag has been captured already and return the winning game rewards,
        if not check whether there are no actions possible anymore, return TRUE then, or FALSE.
        :param actions_possible: list of moves
        :param board: numpy array (5, 5)
        :param max_val: boolean, decider whether this is a goal test for maximizing player
        :return: boolean: reached terminal state, boolean: own team (True) or other team won (False)
        """
        flag_alive = [False, False]
        for pos, piece in np.ndenumerate(board):
            if piece is not None and int == 0:
                flag_alive[piece.team] = True
        if not flag_alive[self.other_team]:
            return True, True
        # if not flag_alive[self.team]:
        #     return True, False
        if not actions_possible:
            # print('cannot move anymore')
            if (
                max_val
            ):  # the minmax agent is the one doing max_val, so if he cant move -> loss for him
                won = False
            else:
                won = True
            return True, won
        else:
            return False, None

    def get_terminal_reward(self, done, won, depth):
        """
        Reward for ending the game on a certain depth. If ended because of flag capture, then
        reward with a depth discounted winGameReward. If ended because of depth limitation,
        return 0
        :param done: boolean, indicate whether the game ended
        :param won: boolean, indicate whether the game was won or lost
        :param depth: the depth at which the game ended
        :return: game end reward, float
        """
        if not done:
            return 0
        else:
            if won:
                terminal_reward = self.winGameReward
            else:
                terminal_reward = -self.winGameReward
            return (
                terminal_reward
                * (depth + 1)
                / (self.max_depth + 1)
                * (terminal_reward / self.kill_reward)
            )

    def update_prob_by_fight(self, enemy_piece):
        """
        update the information about the given piece, after a fight occured
        :param enemy_piece: object of class Piece
        :return: change is in-place, no value specified
        """
        enemy_piece.potential_types = [2]

    def update_prob_by_move(self, move, moving_piece):
        """
        update the information about the given piece, after it did the given move
        :param move: tuple of positions tuples
        :param moving_piece: object of class Piece
        :return: change is in-place, no value specified
        """
        move_dist = spatial.distance.cityblock(move[0], move[1])
        if move_dist > 1:
            moving_piece.hidden = False
            moving_piece.potential_types = [2]  # piece is 2
        else:
            immobile_enemy_types = [
                idx
                for idx, type in enumerate(moving_piece.potential_types)
                if type in [0, 11]
            ]
            moving_piece.potential_types = np.delete(
                moving_piece.potential_types, immobile_enemy_types
            )

    def draw_consistent_enemy_setup(self, board):
        """
        Draw a setup of the enemies pieces on the board provided that aligns with the current status of
        information about said pieces, then place them on the board. This is done via iterative random sampling,
        until a consistent draw occurs. This draw may or may not represent the overall true distribution of the pieces.
        :param board: numpy array (5, 5)
        :return: board with the assigned enemy pieces in it.
        """
        # get information about enemy pieces (how many, which alive, which types, and indices in assign. array)
        enemy_pieces = copy.deepcopy(self.ordered_opp_pieces)
        enemy_pieces_alive = [piece for piece in enemy_pieces if not piece.dead]
        tokens_alive = [piece.token for piece in enemy_pieces_alive]

        # do the following as long as the drawn assignment is not consistent with the current knowledge about them
        consistent = False
        sample = None
        while not consistent:
            # choose as many pieces randomly as there are enemy pieces alive
            sample = np.random.choice(tokens_alive, len(tokens_alive), replace=False)
            # while-loop break condition
            consistent = True
            for idx, piece in enumerate(enemy_pieces_alive):
                # if the drawn type doesn't fit the potential types of the current piece, then redraw
                if sample[idx] not in piece.potential_types:
                    consistent = False
                    break
        # place this draw now on the board by assigning the types and changing critical attributes
        for idx, piece in enumerate(enemy_pieces_alive):
            # add attribute of the piece being guessed (only happens in non-real gameplay aka planning)
            piece.guessed = not piece.hidden
            int = sample[idx]
            if int in [0, 11]:
                piece.can_move = False
                piece.move_range = 0
            elif int == 2:
                piece.can_move = True
                piece.move_range = float("inf")
            else:
                piece.can_move = True
                piece.move_range = 1
            piece.hidden = False
            board[piece.position] = piece
        return board

    def undo_last_move(self, board):
        """
        Undo the last move in the memory. Return the updated board.
        :param board: numpy array (5, 5)
        :return: board
        """
        last_move = self.last_N_moves.pop_last()
        if last_move is None:
            raise ValueError("No last move to undo detected!")
        before_piece = self.pieces_last_N_Moves_beforePos.pop_last()
        board[last_move[0]] = before_piece
        # the piece at the 'before' spatial was the one that moved, so needs its
        # last entry in the move history deleted
        before_piece.position = last_move[0]
        board[last_move[1]] = self.pieces_last_N_Moves_afterPos.pop_last()
        return board
