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


class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = stratego.Game()
        self.game.set_at("blue_bomb", 0, 0)
        self.game.set_at("blue_one", 1, 1)

        self.game.set_at("blue_five", 4,4)
        self.game.set_at("blue_five", 3,4)
        self.game.set_at("red_five", 4,5)

        self.game.set_at("blue_nine", 9,8)
        self.game.set_at("blue_flag", 9,9)
        
        
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

        # Invalid to jump over a piece
        self.game.set_at("blue_five", 5,8)
        self.assertInvalidMove(9,8,0,8, "Nine/Scout should not be able to jump over pieces.")

        # Invalid move into no-mans land
        self.game.set_at("blue_five", 3,2)
        self.assertInvalidMove(3,2,4,2, "Illegal move into no-man's land.")
        self.game.set_at("blue_five", 3,3)
        self.assertInvalidMove(3,3,4,3, "Illegal move into no-man's land.")        
        self.game.set_at("blue_five", 3,6)
        self.assertInvalidMove(3,6,4,6, "Illegal move into no-man's land.")
        self.game.set_at("blue_five", 3,7)
        self.assertInvalidMove(3,7,4,7, "Illegal move into no-man's land.")        
        self.game.set_at("red_five", 6,2)
        self.assertInvalidMove(6,2,5,2, "Illegal move into no-man's land.")
        self.game.set_at("red_five", 6,3)
        self.assertInvalidMove(6,3,5,3, "Illegal move into no-man's land.")        
        self.game.set_at("red_five", 6,6)
        self.assertInvalidMove(6,6,5,6, "Illegal move into no-man's land.")
        self.game.set_at("red_five", 6,7)
        self.assertInvalidMove(6,7,5,7, "Illegal move into no-man's land.")

        # Invalid to jump over no-mans land
        self.game.set_at("blue_nine", 5,0)
        self.assertInvalidMove(5,0,5,5, "Nine/Scout should not be able to jump over no-man's land.")

    def test_capturing(self):
        # Common attacking scenarios
        self.assertVictor("red_one", "blue_two", "red_one")
        self.assertVictor("red_two", "blue_three", "red_two")
        
        # Tie goes to the attacker
        self.assertVictor("blue_five", "red_five", "blue_five")
        self.assertVictor("red_five", "blue_five", "red_five")

        # Man vs Bomb
        self.assertVictor("red_five", "blue_bomb", "blue_bomb")
        self.assertVictor("blue_bomb", "red_five", "blue_bomb") #bomb's can't attack - but if they could...they'd win
        self.assertVictor("red_eight", "blue_bomb", "red_eight") #Miners can defuse bombs

        # Spy
        self.assertVictor("red_spy", "blue_one", "red_spy")
        self.assertVictor("blue_one", "red_spy", "blue_one") #Spy must attack first to win
        self.assertVictor("red_spy", "blue_spy", "red_spy")  #Tie goes to attacker
        self.assertVictor("red_spy", "blue_two", "blue_two")

        # Flag
        self.assertVictor("red_nine", "blue_flag", "red_nine")

    def test_game_over(self):
        g = stratego.Game()
        # Stalemate
        g.set_at("blue_flag", 0, 0)
        g.set_at("blue_bomb", 0, 1)
        g.set_at("red_flag", 1, 1)
        self.assertEqual("tie", g.game_over(), "Game should be over and a tie.")

        # Blue wins
        g = stratego.Game()
        g.set_at("blue_flag", 0, 0)
        self.assertEqual("blue", g.game_over(), "Game should be over and blue win.")

        # Red wins
        g = stratego.Game()
        g.set_at("red_flag", 0, 0)
        self.assertEqual("red", g.game_over(), "Game should be over and red win.")

        # Game not over yet
        g = stratego.Game()
        g.set_at("red_flag", 0, 0)
        g.set_at("blue_flag", 1, 1)
        g.set_at("red_one", 0, 1)
        self.assertFalse(g.game_over(), "Game should not be over yet.")


    def assertVictor(self, attacker, defender, expectedVictor):
        actual = self.game.attack(attacker, defender)
        self.assertEqual(actual, expectedVictor, f"Expected {expectedVictor} to win the fight.")
        
    def assertValidMove(self, row, column, d_row, d_column, message):
        actual = self.game.is_valid_move(row, column, d_row, d_column)
        self.assertTrue(actual, "Piece should be able to move. " + message)

    def assertInvalidMove(self, row, column, d_row, d_column, message):
        actual = self.game.is_valid_move(row, column, d_row, d_column)
        self.assertFalse(actual, "Piece should not be able to move like that. " + message)        


        
if __name__ == '__main__':
    unittest.main()
