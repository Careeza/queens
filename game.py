from board import Board
import numpy as np
import pygame as pg
import random as rd


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
            pg.display.flip()
        
        
    def new_board(self):
        self.create_board_matrix()
        self.board = Board(self, self.board_matrix)
        self.board.init_display()
        
        
    def victory(self):
        self.running = False
        print("Victory !")
        
    def create_board_matrix(self):
        self.board_matrix = rd.choice([np.array([[0,0,0,0,1,1,1,1],
                                [0,0,1,1,1,2,2,3],
                                [0,0,5,0,2,2,2,3],
                                [4,5,5,0,3,3,3,3],
                                [4,5,5,0,6,0,0,0],
                                [5,5,5,6,6,6,0,0],
                                [5,5,6,6,6,7,0,7],
                                [5,5,6,0,6,7,7,7],
                                ]), 
                                np.array([[0,0,1,1,1,0,2,0],
                                [0,1,1,1,2,2,2,0],
                                [1,1,3,4,2,2,0,0],
                                [5,5,3,4,4,2,2,0],
                                [5,5,4,4,4,2,2,0],
                                [5,5,4,4,4,2,2,6],
                                [5,5,7,4,7,6,0,6],
                                [5,5,7,7,7,6,6,6],
                                ])])
        
    def interact(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.board.left_click(event.pos)
                elif event.button == 3:
                    self.board.right_click(event.pos)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_r:
                    self.board.reset_player()
                elif event.key == pg.K_n:
                    self.new_board()
                elif event.key == pg.K_w:
                    print(self.board.victory(debug=True))