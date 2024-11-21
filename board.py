import numpy as np
import pygame as pg
import matplotlib.pyplot as plt


class Board:
    
    def __init__(self, game, board_matrix):
        self.game = game
        self.board_matrix = board_matrix
        self.screen = self.game.screen
        self.board_width, self.board_height = self.board_matrix.shape
        self.n_queen = len(np.unique(self.board_matrix))
        cmap = plt.cm.get_cmap('tab10', self.n_queen) 
        self.colors_list = [tuple(int(c * 255) for c in cmap(i)[:3]) for i in range(self.n_queen)]
        self.colors = [[] for _ in range(self.n_queen)]
        self.player_matrix = np.zeros((self.board_width, self.board_height), dtype=int)
        self.cells = np.empty((self.board_width, self.board_height), dtype=pg.Rect)
        self.subcells = np.empty((self.board_width, self.board_height), dtype=pg.Rect)
        self.queens_placed = 0
        
        self.allow_double_colors = True
        self.allow_wrong_placements = True
        self.queen_display_mode = "geometric"
        
        self.subcell_ratio = 0.8
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
        sub_width = self.cell_width * self.subcell_ratio
        sub_height = self.cell_height * self.subcell_ratio
        for i in range(self.board_width):
            for j in range(self.board_height):
                self.cells[i, j] = pg.Rect(i * self.cell_width, j * self.cell_height, self.cell_width, self.cell_height)
                self.subcells[i, j] = pg.Rect(i * self.cell_width + (self.cell_width - sub_width) / 2, j * self.cell_height + (self.cell_height - sub_height) / 2, sub_width, sub_height)
                
    def create_grid(self):
        for i in range(self.board_width):
            pg.draw.line(self.screen, (0, 0, 0), (i * self.cell_width, 0), (i * self.cell_width, self.game.height))
        
        for j in range(self.board_height):
            pg.draw.line(self.screen, (0, 0, 0), (0, j * self.cell_height), (self.game.width, j * self.cell_height))
        
        
    def display(self):
        
        for i in range(self.board_width):
            for j in range(self.board_height):
                pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.cells[i, j])
        
        self.create_grid()
                
                
    def get_col(self, value):
        return self.colors_list[value]
        
    
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
        return True
    
        
    def get_cell(self, pos):
        return pos[0] // self.cell_width, pos[1] // self.cell_height
    
    def victory(self, debug=False):
        if self.n_queen != self.queens_placed:
            if debug:
                print(f"Wrong number of queens: {self.n_queen} not equal to {self.queens_placed}")
            return False
        if not all(map(len, self.colors)):
            if debug:
                print(f"No queen for all colors: ", all(map(len, self.colors)), map(len, self.colors))
            return False
        for i in range(self.board_width):
            for j in range(self.board_height):
                if self.board_matrix[i, j] == 1:
                    print(i, j)
                    break
            else:
                if debug:
                    print(f"No queen in line {i}")
                return False
        for j in range(self.board_height):
            for i in range(self.board_width):
                if self.board_matrix[i, j] == 1:
                    print(i, j)
                    break
            else:
                if debug:
                    print(f"No queen in column {j}")
                return False
        return True
    
    def check_victory(self):
        if self.victory():
            self.game.victory()
    
    def left_click(self, pos):
        i, j = self.get_cell(pos)
        col = self.board_matrix[i, j]
        
        if self.player_matrix[i, j] == 1:
            self.remove_queen(i, j)
            return
        
        if self.player_matrix[i, j] == 2:
            print("No Queen here")
            return
        
        if not self.allow_wrong_placements and not self.can_place_queen(i, j):
            print("Cannot place Queen here")
            return

        if self.colors[col] != [] and not self.allow_double_colors:
            for i, j in self.colors[col]:
                self.remove_queen(i, j)
        self.place_queen(i, j)
    
    def remove_queen(self, i, j):
        print("Queen removed")
        self.player_matrix[i, j] = 0
        self.colors[self.board_matrix[i, j]].remove((i, j))
        self.queens_placed -= 1
        
        pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.subcells[i, j])
        self.check_victory()
        
    def remove_noqueen(self, i, j):
        self.player_matrix[i, j] = 0
        
        pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.subcells[i, j])
        
        
    def place_queen(self, i, j):
        print("Queen placed")
        self.player_matrix[i, j] = 1
        self.colors[self.board_matrix[i, j]].append((i, j))
        self.queens_placed += 1
        
        if self.queen_display_mode == "geometric":
            pg.draw.rect(self.screen, (0, 0, 0), self.subcells[i, j])
        self.check_victory()
        
    def place_noqueen(self, i, j):
        self.player_matrix[i, j] = 2
        
        if self.queen_display_mode == "geometric":
            pg.draw.rect(self.screen, (255, 255, 255), self.subcells[i, j])
        
    def right_click(self, pos):
        i, j = self.get_cell(pos)
        
        if self.player_matrix[i, j] == 2:
            self.remove_noqueen(i, j)
            return
        
        if self.player_matrix[i, j] == 1:
            print("Queen already here")
            return
        
        self.place_noqueen(i, j)
        
    def reset_player(self):
        self.player_matrix = np.zeros((self.board_width, self.board_height), dtype=int)
        self.queens_placed = 0
        self.colors = [[] for _ in range(self.n_queen)]
        self.init_display()