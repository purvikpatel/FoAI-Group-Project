import os
import random
from collections import defaultdict
from GeneticAlgorithm import genetic_algoritgm
from heuristic import Heuristic
class Board:

    def __init__(self):
        """Initialize a new board"""
        self.board = []
        self.size = 10
        self.no_mans_land = set([(4,2),(4,3),(5,2),(5,3),(4,6),(4,7),(5,6),(5,7)])
        self.piece_name_conversion = {
            "flag"  : "F",
            "spy"   : "S",
            "one"   : "1",
            "two"   : "2",
            "three" : "3",
            "four"  : "4",
            "five"  : "5",
            "six"   : "6",
            "seven" : "7",
            "eight" : "8",
            "nine"  : "9",
            "bomb"  : "B",
            "?"     : "?" }
        self.initialize()
        

    def initialize(self):
        """Create an empty board and fill it with None"""
        self.board = []
        for _ in range(self.size):
            self.board.append([None for _ in range(self.size)])        
        
    def set_at(self, piece, row, column):
        """Set the given piece at row, column. (0,0) is the upper left corner of the board"""
        if self.is_inbounds(row, column):
            self.board[row][column] = piece
        else:
            raise(f"BoardLocationOutOfBounds ({row},{column})")

    def is_occuppied(self, row, column):
        """Returns the piece at (row, column) or False if the location is empty"""
        if not self.is_inbounds(row, column):
            raise(f"BoardLocationOutOfBounds ({row},{column})")
        p = self.board[row][column]
        if p:
            return p
        return False

    def get_from(self, row, column):
        """Returns the piece at (row, column) or throws an exception if piece is empty"""
        p = self.is_occuppied(row, column)
        if not p:
            raise Exception(f"PieceNotFound at ({row}, {column})")
        return p

    def remove_at(self, row, column):
        """Removes the piece at (row, column). If piece is empty then nothing happens"""
        if not self.is_inbounds(row, column):
            raise(f"BoardLocationOutOfBounds ({row},{column})")
        
        self.board[row][column] = None

    def reduce(self, f, init_value=None):
        """Run reduce over the board. This is a very flexible iterator abstraction over the board."""
        acc = init_value
        for row in self.board:
            for piece in row:
                acc = f(piece, acc)
        return acc

    def is_inbounds(self, row, column):
        """Returns True if the (row, column) are within the 10 x 10 play space."""
        return 0 <= row < self.size and 0 <= column < self.size

    def clone(self):
        """Returns a new board with an identical layout as the current board"""
        c = Board()
        c.board = []
        for row in self.board:
            c.board.append(row[:])
        return c

            
    def is_path_clear(self, row, column, target_row, target_column):
        start_row = min(row, target_row)
        end_row = max(row, target_row)
        start_column = min(column, target_column)
        end_column = max(column, target_column)
        while(True):
            start_row += 0 if start_row == end_row else 1
            start_column += 0 if start_column == end_column else 1
            if (start_row == end_row and start_column == end_column):
                return True
            elif self.is_occuppied(start_row, start_column):
                return False
            elif (start_row, start_column) in self.no_mans_land:
                return False
        return True
    
    def abbr(self, piece):
        color, rank = piece.split("_")
        p = color.replace("red", "R").replace("blue", "B")
        p += self.piece_name_conversion[rank]
        return p
    
    def __str__(self):
        """Blue pieces will be prefixed with a 'B', and Red pieces will have a 'R'"""
        b = ""
        for row in self.board:
            b += "|".join([self.abbr(r) if r else "__" for r in row])
            b += "\n"

        return b
        

class Game:
    def __init__(self):
        self.piece_value_lookup = {
            "flag"  : 0,
            "spy"   : 0,
            "one"   : 9,
            "two"   : 8,
            "three" : 7,
            "four"  : 6,
            "five"  : 5,
            "six"   : 4,
            "seven" : 3,
            "eight" : 2,
            "nine"  : 1,
            "bomb"  : 100 }

        self.board = Board()

    def is_bomb(self, piece):
        return "bomb" in piece

    def is_flag(self, piece):
        return "flag" in piece

    def is_scout(self, piece):
        return "nine" in piece

    def is_miner(self, piece):
        return "eight" in piece

    def is_spy(self, piece):
        return "spy" in piece

    def is_marshall(self, piece):
        return "one" in piece

    def is_movable(self, piece):
        return not(self.is_flag(piece) or self.is_bomb(piece))

    def piece_value(self, piece):
        color, rank = piece.split("_")
        return self.piece_value_lookup[rank]
    
    def stronger_piece(self, a, b):
        # Tie goes to the attacker
        if self.piece_value(a) >= self.piece_value(b):
            return a
        return b
    
    def attack(self, attacker, defender):
        """Return the piece that is victorious"""
        if self.same_color(attacker, defender):
            raise Exception("Illegal to attack teammates!")
        if self.is_bomb(attacker):
            return attacker
        elif self.is_bomb(defender):
            if self.is_miner(attacker):
                return attacker
            return defender
        elif self.is_spy(attacker):
            if self.is_marshall(defender):
                return attacker
        
        return self.stronger_piece(attacker, defender)

    def is_valid_move(self, row, column, target_row, target_column):
        """Returns True if the piece at (row,column) is allowed to move to (target_row, target_column)"""
        #print(f"({row},{column}) -> ({target_row},{target_column})")
        p = self.is_occuppied(row, column)
        if not p:
            raise Exception(f"MoveInvalid - no piece located at ({row}, {column}).")

        if self.in_no_mans_land(target_row, target_column):
            return False
        # Check if we are trying to move an immobile piece
        elif self.is_bomb(p) or self.is_flag(p):
            return False
        # Check if location is already occuppied by same color piece
        elif self.is_occuppied(target_row, target_column):
            return self.color_at(row, column) != self.color_at(target_row, target_column)
        # Check for moving in-place
        elif row == target_row and column == target_column:
            return False 
        # Check for diagonal movements
        elif row != target_row and column != target_column:
            return False
        # Check for moving more than 1 space
        elif abs(row - target_row) > 1 or abs(column - target_column) > 1:
            # Allow the scout to move > 1 space
            if self.is_scout(p):
                return self.is_path_clear(row, column, target_row, target_column)
            return False
        return True

    def same_color(self, piece1, piece2):
        return self.color_of(piece1) == self.color_of(piece2)
    
    def color_of(self, piece):
        if "red" in piece:
            return "red"
        return "blue"
    
    def color_at(self, row, column):
        p = self.get_from(row, column)
        return self.color_of(p)

    def is_path_clear(self, row, column, target_row, target_column):
        return self.board.is_path_clear(row, column, target_row, target_column)

    def is_occuppied(self, row, column):
        return self.board.is_occuppied(row, column)

    def get_from(self, row, column):
        return self.board.get_from(row, column)

    def set_at(self, piece, row, column):
        self.board.set_at(piece, row, column)

    def remove_at(self, row, column):
        self.board.remove_at(row, column)

    def in_no_mans_land(self, row, column):
        return (row,column) in self.board.no_mans_land

    def board_contains(self, predicate):
        f = lambda p, acc: acc or predicate(p)
        return self.board.reduce(f, False)

    def on_board(self, piece):
        # Fun with higher-order functions :)
        pred = lambda p : p == piece
        return self.board_contains(pred)

    def game_over(self):
        """If game is over return winner color or 'tie' - else return False"""
        if not self.on_board("red_flag"):
            return "blue" 
        elif not self.on_board("blue_flag"):
            return "red"
        movable_entries = lambda p: p is not None and self.is_movable(p)
        if not self.board_contains(movable_entries):
            return "tie"
        return False

    def board_as_seen_by(self, color):
        opposite_color = "blue"
        if color == opposite_color:
            opposite_color = "red"
        clone = self.board.clone()
        for row in clone.board:
            for i in range(len(row)):
                if row[i] is not None and color not in row[i]:
                    row[i] = opposite_color + "_?"
        return clone

    def start(self):
        player = "blue"
        while (not self.game_over()):
            self.display_board()
            b = self.board_as_seen_by(player)
            move = self.select_move(player, b)
            self.make_move(move)
            player = self.next_turn(player)

    def select_move(self, player, board):
        print(f"======{player} Perspective============")
        move = Heuristic.get_best_board(board, player)
        print(board)
        return (3,0,4,0)

    def next_turn(self, player):
        if "red" in player:
            return "blue"
        return "red"

    def display_board(self):
        print("--------Full Perspective----------------")
        print(self.board)

    def make_move(self, move):
        row, column, target_row, target_column = move
        
        if not self.is_valid_move(row, column, target_row, target_column):
            raise Exception("Requested illegal move!")
        
        attacker = self.get_from(row, column)
        if self.is_occuppied(target_row, target_column):
            defender = self.get_from(target_row, target_column)
            victor = self.attack(attacker, defender)
            self.set_at(victor, target_row, target_column)
        else:
            self.set_at(attacker, target_row, target_column)
        self.remove_at(row, column)



def random_board():
    names_of_pieces = ["spy", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "bomb", "flag"]
    colors = ["blue", "red"]
    starting_quantities = {"bomb"  : 6,
                           "one"   : 1,
                           "two"   : 1,
                           "three" : 2,
                           "four"  : 3,
                           "five"  : 4,
                           "six"   : 4,
                           "seven" : 4,
                           "eight" : 5,
                           "nine"  : 8,
                           "spy"   : 1,
                           "flag"  : 1}

    board_rows = 10
    board_columns = 10
    board = []
    row = []
    for color in colors:
        n = 0
        pieces_used = defaultdict(lambda: 0)
        while n < 40:
            piece = random.choice(names_of_pieces)
            if pieces_used[piece] < starting_quantities[piece]:
                row.append(f"{color}_{piece}")
                pieces_used[piece] += 1
                n += 1
                if len(row) == board_columns:
                    board.append(row)
                    row = []

        if color == "blue":
            board.append([None for _ in range(board_columns)])
            board.append([None for _ in range(board_columns)])

    b = Board()
    b.board = board
    return b

def create_new_board():
    b = Board()
    b.initialize()
    ga = genetic_algoritgm(100, 10000,  0.4, 0.6)
    ga.execute()
    i = random.sample(range(10), 2)

    blue_board = ga.population[i[0]]
    red_board = ga.population[i[1]]

    
    for i in range(4):
        for j in range(10):
            x = blue_board[i][j]
            b.board[i][j] = f"blue_{x}"
    
    for i in reversed(range(6,10)):
        for j in reversed(range(10)):
            x = red_board[9-i][9 -j]
            b.board[i][j] = f"red_{x}"
        
    return b




board = create_new_board()

game = Game()
game.board = board
game.display_board()
# game.start()