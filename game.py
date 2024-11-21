from board import Board
import numpy as np
import pygame as pg


class Game:
    
    def __init__(self, game_shape=(8, 8)):
        
        self.width, self.height = 800, 800
        self.screen = pg.display.set_mode((self.width, self.height))
        
        self.shape_game = game_shape
        
        
        self.running = False
        
    def start(self):
        self.running = True
        self.new_board()
        
        while self.running:
            self.interact()
            self.board.init_display()
            pg.display.flip()
        
        
    def new_board(self):
        self.create_board_matrix()
        self.board = Board(self, self.board_matrix)
        
    def create_board_matrix(self):
        raise NotImplementedError
        
    def interact(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                self.running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.board.left_click(event.pos)
                elif event.button == 3:
                    self.board.right_click(event.pos)