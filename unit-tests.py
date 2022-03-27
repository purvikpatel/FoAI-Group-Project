import unittest
import stratego


class TestBoard(unittest.TestCase):

    def test_can_place_and_remove_piece(self):
        board = stratego.Board()
        board.set_at("blue_bomb", 0, 0)
        p = board.get_from(0,0)
        self.assertEqual(p, "blue_bomb", "Pieces are not equal")
        board.remove_at(0,0)
        p = board.is_occuppied(0,0)
        self.assertTrue(p == False, "Piece was not removed")

    def test_placing_out_of_bounds(self):
        board = stratego.Board()
        positions = [((0,0), True),
                     ((1,3), True),
                     ((9,9), True),
                     ((-1,0), False),
                     ((0,-1), False),
                     ((-1,-1), False),
                     ((10, 9), False),
                     ((9, 10), False),
                     ((10,10), False)]
    
        for pos, expected in positions:
            row, column = pos
            actual = board.is_inbounds(row, column)
            expected_bounds = "in-bounds" if expected else "out-of-bounds"
            self.assertEqual(expected, actual, \
                             f" ({row},{column}) should have been {expected_bounds}.")


class TestMovement(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.board = stratego.Board()
        self.board.set_at("blue_bomb", 0, 0)
        self.board.set_at("blue_one", 1, 1)

        self.board.set_at("blue_five", 4,4)
        self.board.set_at("blue_five", 3,4)
        self.board.set_at("red_five", 4,5)

        self.board.set_at("blue_nine", 9,8)
        self.board.set_at("blue_flag", 9,9)
        
        
    def test_bombs_and_flag_cannot_move(self):
        self.assertInvalidMove(0,0,0,1, "Bombs cannot move")
        self.assertInvalidMove(9,9,9,8, "Flags cannot move")

    def test_valid_moves(self):
        # Common movements
        self.assertValidMove(1,1,0,1, "One should be able to move up.")
        self.assertValidMove(1,1,2,1, "One should be able to move up.")
        self.assertValidMove(1,1,1,0, "One should be able to move left.")
        self.assertValidMove(1,1,1,2, "One should be able to move left.")

        # Commom attacking moves
        self.assertValidMove(4,4,4,5, "Piece should be able to attack.")
        
        # Special movement
        self.assertValidMove(9,8,0,8, "Nine/Scout should be able to move many spaces.")
        self.assertValidMove(9,8,9,0, "Nine/Scout should be able to move many spaces.")
     
    def test_invalid_moves(self):
        # Common invalid movements
        self.assertInvalidMove(1,1,1,1, "One should not be able to move in-place.")
        self.assertInvalidMove(1,1,2,2, "One should not be able to move diagonally.")
        self.assertInvalidMove(1,1,0,0, "One should not be able to move diagonally.")
        self.assertInvalidMove(1,1,0,2, "One should not be able to move diagonally.")
        self.assertInvalidMove(1,1,2,0, "One should not be able to move diagonally.")
        self.assertInvalidMove(1,1,1,3, "One should not be able to move more than 1 space.")
        self.assertInvalidMove(1,1,3,1, "One should not be able to move more than 1 space.")

        # Invalid moves around other pieces
        self.assertInvalidMove(4,4,3,4, "Place already occuppied by piece of the same color.")

        # TODO: moves into no-mans land
        
        
        
        

    def assertValidMove(self, row, column, d_row, d_column, message):
        actual = self.board.is_valid_move(row, column, d_row, d_column)
        self.assertTrue(actual, "Piece should be able to move. " + message)

    def assertInvalidMove(self, row, column, d_row, d_column, message):
        actual = self.board.is_valid_move(row, column, d_row, d_column)
        self.assertFalse(actual, "Piece should not be able to move like that. " + message)        

if __name__ == '__main__':
    unittest.main()
