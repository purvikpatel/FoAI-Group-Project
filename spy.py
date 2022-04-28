from collections import defaultdict


class Spy:
    def __init__(self, board):
        """The goal of Spy is to watch the enemy moves to try and 
           figure out the enemy pieces.
        
        board : The board as seen from the perspective of a single player. It is assumed that
                piece distribution is the same for both players.
        """
        self.remaining_enemy_pieces = self.count_pieces(board)
        self.state = {}
        self.color = None
        self.rank_lookup = {
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
        

        starting_distribution = self.calc_distribution(self.remaining_enemy_pieces)        
        for row, columns in enumerate(board):
            for column, piece in enumerate(columns):                
                if piece is None:
                    continue
                p = self.normalize_piece(piece)
                if self.is_known_piece(p) and self.color is None:
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


    def calc_distribution(self, pieces, pred = None):
        if pred is None:
            pred = lambda v : v
        total_pieces = sum([v for k,v in pieces.items() if pred(k)])
        dist = {}
        for piece, count in pieces.items():
            if not pred(piece):
                continue
            dist[piece] = float(count) / total_pieces

        return dist

    def rebuild_state_distribution(self):
        counts_of_unknown_pieces = self.remaining_enemy_pieces
        counts_of_possible_locations = defaultdict(lambda:0)
        
        #remove known items from distribution
        for coord, d in self.state.items():
            if len(d) == 1:
                piece, prob = d.popitem()
                d[piece] = prob
                counts_of_unknown_pieces[piece] -= 1
            else:
                for piece,prob in d.items():
                    counts_of_possible_locations[piece] += 1

        #normalize counts
        for piece,value in counts_of_unknown_pieces.items():
            counts_of_unknown_pieces[piece] = max(0, value)

        
        #recalculate distribution
        for coord, d in self.state.items():
            if len(d) > 1:
                new_dist = {}
                sum_of_possible_pieces = 0
                for piece, prob in d.items():
                    sum_of_possible_pieces += counts_of_unknown_pieces[piece]

                for piece, prob in d.items():
                    if (counts_of_unknown_pieces[piece] > 0):
                        prob = counts_of_unknown_pieces[piece] / float(sum_of_possible_pieces)
                        prob = prob / float(counts_of_possible_locations[piece])
                        new_dist[piece] = prob

                #normalize dist
                s = 0
                for k,v in new_dist.items():
                    s += v
                
                for k,v in new_dist.items():
                    new_dist[k] = float(v)/s
                
                self.state[coord] = new_dist
            
       
    
                            
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

    def remove_bomb_or_flag_probabilities(self, row, column):
        no_flags_or_bombs = lambda k : not(k == "bomb" or k == "flag")
        dist = self.calc_distribution(self.remaining_enemy_pieces, pred = no_flags_or_bombs)
        self.state[(row, column)] = dist
        
    
    def update(self, start_row, start_column, end_row, end_column, remained=None, removed=None):
        """Update probability distributions based on enemy move"""
        if (start_row, start_column) not in self.state:
            raise Exception(f"Expected to find enemy at ({start_row}, {start_column})")


        if removed is None:
            if self.move_dist(start_row, start_column, end_row, end_column) > 1:
                self.state[(end_row, end_column)] = {"nine" : 1.0}
            else:
                self.state[(end_row, end_column)] = self.state[(start_row, start_column)]
                self.remove_bomb_or_flag_probabilities(end_row, end_column)
            self.state.pop((start_row, start_column))
            self.rebuild_state_distribution()
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
        """Return the probability distribution at (row, column)"""
        dist = self.state[(row,column)]
        return dist

    def max_rank(self, a, b):
        if self.rank_lookup[a] > self.rank_lookup[b]:
            return a
        return b

    def max_at(self, row, column):
        """Returns (piece, prob) with the highest probability at (row,column) and on equal return the higher ranking piece"""
        dist = self.state[(row,column)]
        max_piece = None
        max_prob = float("-inf")
        for piece, prob in dist.items():
            if prob > max_prob:
                max_prob = prob
                max_piece = piece
            if prob == max_prob:
                max_piece = self.max_rank(max_piece, piece)

        return (max_piece, max_prob)
