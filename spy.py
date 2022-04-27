from collections import defaultdict

class Spy:
    def __init__(self, board):
        """The goal of Spy is to watch the progressive game states to try and 
           figure out the enemy pieces"""
        self.remaining_enemy_pieces = self.count_pieces(board)
        self.state = {}
        self.color = None

        starting_distribution = self.calc_distribution(self.remaining_enemy_pieces)        
        for row, columns in enumerate(board):
            for column, piece in enumerate(columns):                
                if piece is None:
                    continue
                p = self.normalize_piece(piece)
                if self.is_known_piece(p):
                    self.state[(row,column)] = {p : 1.0}
                    if self.color is None:
                        self.color = self.piece_color(piece)
                else:
                    self.state[(row,column)] = starting_distribution.copy()             
    
    def count_pieces(self, board):
        pieces = defaultdict(lambda: 0)
        for row in board:
            for piece in row:
                if piece is None:
                    continue
                if self.is_known_piece(piece):
                    p = self.normalize_piece(piece)
                    pieces[p] += 1
        return pieces


    def calc_distribution(self, pieces):
        total_pieces = sum([v for k,v in pieces.items()])
        dist = {}
        for piece, count in pieces.items():
            dist[piece] = float(count) / total_pieces

        return dist

    def rebuild_state_distribution(self):
        new_state = {}
        dist = self.calc_distribution(self.remaining_enemy_pieces)
        for coord, d in self.state.items():
            if len(d) == 1:
                new_state[coord] = d
            else:
                new_state[coord] = dist.copy()
            
        self.state = new_state
    
                            
    def is_known_piece(self, piece):
        return "?" not in piece

    def normalize_piece(self, piece):
        color, rank = piece.split("_")
        return rank

    def piece_color(self, piece):
        color, rank = piece.split("_")
        return color

    def move_dist(self, start_row, start_column, end_row, end_column):
        return max(abs(start_row - end_row), abs(start_column - end_column))

    def update(self, start_row, start_column, end_row, end_column, remained=None, removed=None):
        """Update probability distributions based on move"""
        if removed is None:
            if self.move_dist(start_row, start_column, end_row, end_column) > 1:
                self.state[(end_row, end_column)] = {"nine" : 1.0}
            else:
                self.state[(end_row, end_column)] = self.state[(start_row, start_column)]
            self.state.pop((start_row, start_column))
            return

        p = self.normalize_piece(remained)
        self.state[(end_row,end_column)] = {p : 1.0}
        self.state.pop((start_row, start_column))

        discovered_piece = self.normalize_piece(removed)
        if self.piece_color(removed) == self.color:
            discovered_piece = self.normalize_piece(remained)
            
        self.remaining_enemy_pieces[discovered_piece] -= 1
        self.rebuild_state_distribution()
                
    
    def at(self, row, column):
        """Return the most likely piece at (row, column) and the confidence level between 0 and 1.0 (0 is no confidence, and 1 is known)"""

        dist = self.state[(row,column)]
        max_prob = float("-inf")
        max_piece = None
        for piece, prob in dist.items():
            if prob > max_prob:
                max_prob = prob
                max_piece = piece

        return (max_piece, max_prob)
