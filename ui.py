import os
import random
import pygame as pg
from pygame._sdl2 import Window, Texture, Image, Renderer
from collections import defaultdict
from stratego import random_board


#Code for getting image into sprite group
#inspired by https://github.com/pygame/pygame/blob/main/examples/sprite_texture.py
# and https://ehmatthes.github.io/pcc_2e/beyond_pcc/pygame_sprite_sheets/#a-simple-sprite-sheet

image_lookup = {}
screen = None

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
    global image_lookup, screen
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

start_game()