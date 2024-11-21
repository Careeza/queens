import numpy as np
import pygame as pg


class Board:
    
    def __init__(self, game, board_matrix):
        self.game = game
        self.board_matrix = board_matrix
        self.screen = self.game.screen
        self.board_width, self.board_height = self.board_matrix.shape
        self.n_queen = np.unique(self.board_matrix)
        self.colors = [None for i in range(self.n_queen)]
        self.player_matrix = np.zeros((self.board_width, self.board_height), dtype=int)
        self.cells = np.empty((self.board_width, self.board_height), dtype=pg.Rect)
        self.queens_placed = 0
        self.create_cells()
        
    @property
    def cell_width(self):
        return self.game.width // self.n_queen
        
    @property
    def cell_height(self):
        return self.game.height // self.n_queen
        
    def init_display(self):
        self.create_grid()
        self.display()
        
    def create_cells(self):
        for i in range(self.board_width):
            for j in range(self.board_height):
                self.cases[i, j] = pg.Rect(i * self.cell_width, j * self.cell_height, self.cell_width, self.cell_height)
                
    def create_grid(self):
        for i in range(self.board_width):
            pg.draw.line(self.screen, (0, 0, 0), (i * self.cell_width, 0), (i * self.cell_width, self.game.height))
        
        for j in range(self.board_height):
            pg.draw.line(self.screen, (0, 0, 0), (0, i * self.cell_height), (self.game.width, i * self.cell_height))
        
        
    def display(self):
        self.create_grid()
        
        for i in range(self.board_width):
            for j in range(self.board_height):
                pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.cells[i, j])
                
                
    def get_col(self, value):
        return 0, 255 * value // self.n_queen, 255 - (255 * value) // self.n_queen
        
    
    def can_place_queen(self, i, j):
        col = self.board_matrix[i, j]
        for _j in range(self.board_height):
            if self.player_matrix[i, _j] == 1 and self.board_matrix[i, _j] != col:
                return False
        for _i in range(self.board_width):
            if self.player_matrix[_i, j] == 1 and self.board_matrix[_i, j] != col:
                return False
            
        adjacents = [(i + dep_i, j + dep_j) for dep_i in [-1, 0, 1]
                                            for dep_j in [-1, 0, 1] 
                                            if (dep_i != 0 or dep_j != 0) 
                                                and 0 <= i + dep_i < self.board_width 
                                                and 0 <= j + dep_j < self.board_height
                                                and self.board_matrix[i + dep_i, j + dep_j] != col]
        for adj in adjacents:
            if self.player_matrix[adj] == 1:
                return False
    
        
    def get_cell(self, pos):
        return pos[0] // self.cell_width, pos[1] // self.cell_height
    
    def left_click(self, pos):
        i, j = self.get_cell(pos)
        col = self.board_matrix[i, j]
        
        if self.player_matrix[i, j] == 1:
            print("Queen removed")
            self.player_matrix[i, j] = 0
            self.colors[col] = None
            self.queens_placed -= 1
            return
        
        if self.player_matrix[i, j] == 2:
            print("No Queen here")
            return
        
        if not self.can_place_queen(i, j):
            print("Cannot place Queen here")
            return

        print("Queen placed")
        self.player_matrix[i, j] = 1
        if self.colors[col] is not None:
            self.queens_placed -= 1
        self.colors[col] = i, j
        self.queens_placed += 1
        
        
    def right_click(self, pos):
        i, j = self.get_cell(pos)
        
        if self.player_matrix[i, j] == 2:
            print("No Queen already here")
            return
        
        if self.player_matrix[i, j] == 1:
            print("Queen already here")
            return
        
        print("No Queen placed")
        self.player_matrix[i, j] = 2