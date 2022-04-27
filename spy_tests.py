import unittest
import stratego
from spy import Spy

class TestPieceInference(unittest.TestCase):

    def setUp(self):
        pass


    def test_single_item_board(self):
        board = [["blue_flag"]]
        spy = Spy(board)
        piece, prob = spy.at(0,0)
        self.assertTrue(piece == "flag")
        self.assertAlmostEqual(prob, 1.0, delta=0.00001)

    def test_simple_board(self):
        board = [["blue_flag", "red_?"]]
        spy = Spy(board)
        piece, prob = spy.at(0,1)
        self.assertTrue(piece == "flag")
        self.assertAlmostEqual(prob, 1.0, delta=0.00001)

    def test_2x2_board(self):
        board = [["blue_flag", "red_?"],
                 ["blue_one", "red_?"]]
        spy = Spy(board)
        piece, prob = spy.at(0,1)
        self.assertTrue(piece == "one" or piece == "flag")
        self.assertAlmostEqual(prob, 0.5, delta=0.00001)
        spy.update(1,0,1,1, remained = "blue_one", removed = "red_one")
        piece, prob = spy.at(0,1)
        self.assertTrue(piece == "flag")
        self.assertAlmostEqual(prob, 1.0, delta=0.00001)

    def test_scout_detection(self):
        board = [["blue_flag", "red_?", "red_?"],
                 ["blue_nine", None, None],
                 [None, None, None]]
        spy = Spy(board)
        piece, prob = spy.at(0,1)
        self.assertTrue(piece == "nine" or piece == "flag")
        self.assertAlmostEqual(prob, 0.5, delta=0.00001)
        spy.update(0,2,2,2)
        piece, prob = spy.at(2,2)
        self.assertTrue(piece == "nine")
        self.assertAlmostEqual(prob, 1.0, delta=0.00001)
