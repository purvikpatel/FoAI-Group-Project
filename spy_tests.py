import unittest
import stratego
from spy import Spy

class TestPieceProbabilityDistribution(unittest.TestCase):

    def setUp(self):
        pass

    def test_full_size_board_starting_distributions(self):
        board = stratego.random_board()
        game = stratego.Game()
        game.board = board
        blue_board = game.board_as_seen_by("blue")
        spy = Spy(blue_board.board)
        dist = spy.at(9,1)
        self.assertAlmostEqual(dist["flag"],  0.025, delta=0.00001)
        self.assertAlmostEqual(dist["bomb"],  0.15,  delta=0.00001)
        self.assertAlmostEqual(dist["spy"],   0.025, delta=0.00001)
        self.assertAlmostEqual(dist["one"],   0.025, delta=0.00001)
        self.assertAlmostEqual(dist["two"],   0.025, delta=0.00001)
        self.assertAlmostEqual(dist["three"], 0.05,  delta=0.00001)
        self.assertAlmostEqual(dist["four"],  0.075, delta=0.00001)
        self.assertAlmostEqual(dist["five"],  0.1,   delta=0.00001)
        self.assertAlmostEqual(dist["six"],   0.1,   delta=0.00001)
        self.assertAlmostEqual(dist["seven"], 0.1,   delta=0.00001)
        self.assertAlmostEqual(dist["eight"], 0.125, delta=0.00001)
        self.assertAlmostEqual(dist["nine"],  0.2,   delta=0.00001)

    def test_single_item_board(self):
        board = [["blue_flag"]]
        spy = Spy(board)
        dist = spy.at(0,0)
        self.assertAlmostEqual(dist["flag"], 1.0, delta=0.00001)

    def test_simple_board(self):
        board = [["blue_flag", "red_?"]]
        spy = Spy(board)
        dist = spy.at(0,1)
        self.assertAlmostEqual(dist["flag"], 1.0, delta=0.00001)

    def test_2x2_board(self):
        board = [["blue_flag", "red_?"],
                 ["blue_one", "red_?"]]
        spy = Spy(board)
        dist = spy.at(0,1)
        self.assertAlmostEqual(dist["flag"], 0.5, delta=0.00001)
        spy.update(1,0,1,1, remained = "blue_one", removed = "red_one")
        dist = spy.at(0,1)
        self.assertAlmostEqual(dist["flag"], 1.0, delta=0.00001)

    def test_scout_detection(self):
        board = [["blue_flag", "red_?", "red_?"],
                 ["blue_nine", None, None],
                 [None, None, None]]
        spy = Spy(board)
        dist = spy.at(0,1)
        self.assertAlmostEqual(dist["nine"], 0.5, delta=0.00001)
        spy.update(0,2,2,2)
        dist = spy.at(2,2)
        self.assertAlmostEqual(dist["nine"], 1.0, delta=0.00001)

    def test_movement_means_not_flag_or_bomb(self):
        board = [["blue_flag", "red_?", "red_?"],
                 ["blue_bomb", "red_?", None],
                 ["blue_five", None, None]]
        spy = Spy(board)
        dist = spy.at(0,1)
        self.assertAlmostEqual(dist["flag"], 0.3333333, delta=0.00001)
        piece,prob = spy.max_at(0,1)
        self.assertEqual("bomb", piece)
        self.assertAlmostEqual(prob, 0.3333333, delta=0.00001)
        spy.update(0,2,1,2)
        dist = spy.at(1,2)
        self.assertAlmostEqual(dist["five"], 1.0, delta=0.00001)

