import os
import random
import pygame as pg
from pygame._sdl2 import Window, Texture, Image, Renderer
from collections import defaultdict

class Board:

    def __init__(self):
        """Builds and initializes a board"""
        self.board = []
        self.size = 10
        self.initialize()
        self.piece_value_lookup = {
            "flag"  : 0,
            "spy"   : 1,
            "one"   : 1,
            "two"   : 2,
            "three" : 3,
            "four"  : 4,
            "five"  : 5,
            "six"   : 6,
            "seven" : 7,
            "eight" : 8,
            "nine"  : 9,
            "bomb"  : 10 }

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
            "bomb"  : "B" }

        self.no_mans_land = set([(4,2),(4,3),(5,2),(5,3),(4,6),(4,7),(5,6),(5,7)])

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

    def is_inbounds(self, row, column):
        """Returns True if the (row, column) are within the 10 x 10 play space."""
        return 0 <= row < self.size and 0 <= column < self.size

    def clone(self):
        """Returns a new board with an identical layout as the current board"""
        c = Board()
        c.board = self.board[:]
        return c

    def is_valid_piece(self, piece):
        """Validates the name of the piece"""
        pass

    def is_valid_move(self, row, column, target_row, target_column):
        """Returns True if the piece at (row,column) is allowed to move to (target_row, target_column)"""
        p = self.is_occuppied(row, column)
        if not p:
            raise Exception(f"MoveInvalid - no piece located at ({row}, {column}).")

        if (target_row, target_column) in self.no_mans_land:
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
    
    
    def is_bomb(self, piece):
        return "bomb" in piece

    def is_flag(self, piece):
        return "flag" in piece

    def is_scout(self, piece):
        return "nine" in piece

    def attack(self, attacker, defender):
        """Return the piece that is victorious"""
        if self.same_color(attacker, defender):
            raise Exception("Illegal to attack teammates!")
        if self.is_bomb(attacker):
            return attacker
        elif self.is_bomb(defender):
            return defender

        return attacker

    def same_color(self, piece1, piece2):
        return self.color_of(piece1) == self.color_of(piece2)
    
    def color_of(self, piece):
        if "red" in piece:
            return "red"
        return "blue"
    
    def color_at(self, row, column):
        p = self.get_from(row, column)
        return self.color_of(p)

    
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
            board.append([])
            board.append([])

    b = Board()
    b.board = board
    return b














#Code for getting image into sprite group
#inspired by https://github.com/pygame/pygame/blob/main/examples/sprite_texture.py
# and https://ehmatthes.github.io/pcc_2e/beyond_pcc/pygame_sprite_sheets/#a-simple-sprite-sheet

class SpriteSheet():
    def __init__(self, filepath):
        self.img = pg.image.load(filepath).convert()

    def cut_sheet(self, x, y, tile_size, offset, rows, columns):
        """Return an array of rectangles that represent the parts of the sheet"""
        sprites = []
        t_x, t_y = x, y
        for i in range(rows):
            t_x = x
            for j in range(columns):
                rect = pg.Rect(t_x, t_y, x + tile_size, y + tile_size)
                image = pg.Surface(rect.size).convert()
                image.blit(self.img, (0,0), rect)
                image.set_colorkey((255,255,255), pg.RLEACCEL)
                sprites.append(image)
                t_x += tile_size + offset
            t_y += tile_size + offset
        return sprites

       


def draw_piece(piece_name, x, y):
    img = image_lookup[piece_name]
    scale_x = 50
    scale_y = 50
    img = pg.transform.scale(img, (scale_x, scale_y))
    rect = img.get_rect()
    rect.topleft = x,y
    screen.blit(img, rect)
        
def draw_board(board):
    x,y = 10,10
    tile_size = 60
    for row in board:
        x = 10
        for piece in row:
            if piece != "":
                draw_piece(piece, x, y)
            x += tile_size
        y += tile_size
            

def start_game():

    screen_width = 650
    screen_height = 650
    screen = pg.display.set_mode((screen_width, screen_height))
    asset_dir = os.path.join(os.getcwd(), "assets")

    pg.display.init()

    sheet = SpriteSheet(os.path.join(asset_dir, "pieces.png"))
    images_array = sheet.cut_sheet(5, 5, 90, 20, 4, 8)
    names_of_pieces = ["spy", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "bomb", "flag"]
    colors = ["blue", "red"]

    image_lookup = {}
    i = 0
    for color in colors:
        for piece in names_of_pieces:
            key = f"{color}_{piece}"
            image_lookup[key] = images_array[i]
            i += 1
        i = 16


    b = random_board()
    board = b.board

    clock = pg.time.Clock()

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((255,255,255))
        draw_board(board)
        pg.display.flip()
        clock.tick(60)


    pg.quit()
