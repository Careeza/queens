import numpy as np
import pygame as pg
import matplotlib.pyplot as plt

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)



class Board:
    
    def __init__(self, game, board_matrix: np.ndarray):
        self.game = game
        self.board_matrix: np.ndarray = board_matrix
        self.screen: pg.Surface = game.screen
        self.board_width: int = self.board_matrix.shape[0]
        self.board_height: int = self.board_matrix.shape[1]
        self.n_queen: int = len(np.unique(self.board_matrix))
        
        self.colors_list: list[tuple[int, int, int]]
        self.colors_filled: list[list[tuple[int, int]]]
        self.player_matrix: np.ndarray
        self.queens_placed: int
        self.cells: np.ndarray
        self.subcells: np.ndarray
        
        self.terminal_debug: bool = False
        self.use_right_click: bool = False
        self.allow_double_colors: bool = True
        self.allow_wrong_placements: bool = True
        
        self.grid_color = BLACK
        self.contour_color = BLACK
        
        self.subcell_ratio: float = 0.6
        self.grid_line_size: int = 10
        self.contour_line_size: int = 10
        self.cross_line_size: int = 2
        
        self.init_colors()
        self.create_cells()
        self.reset_player()
        
    def line_height(self, i):
        return round(self.contour_line_size + 1 - (1+self.grid_line_size) % 2 + (self.game.height - self.contour_line_size * 2 - self.grid_line_size + 1) * i / self.board_height)
    
    def row_width(self, i):
        return round(self.contour_line_size + 1 - (1+self.grid_line_size) % 2 + (self.game.width - self.contour_line_size * 2 - self.grid_line_size + 1) * i / self.board_width)

    def reset_player(self):
        self.player_matrix = np.zeros((self.board_width, self.board_height), dtype=int)
        self.queens_placed = 0
        self.colors_filled = [[] for _ in range(self.n_queen)]
        self.init_display()
        self.update_screen()
        
    def init_display(self):
        self.display()
        self.create_grid()
        
    def update_screen(self):
        pg.display.flip()
        
    def get_cell_coord(self, i, j):
        left = self.row_width(i) + self.grid_line_size - self.grid_line_size%2
        top = self.line_height(j) + self.grid_line_size - self.grid_line_size%2
        cell_width = self.row_width(i+1) - left - self.grid_line_size%2
        cell_height = self.line_height(j+1) - top - self.grid_line_size%2
        return left, top, cell_width, cell_height
    
    def get_subcell_coord(self, i, j):
        top, left, cell_width, cell_height = self.get_cell_coord(i, j)
        sub_width = cell_width * self.subcell_ratio
        sub_height = cell_height * self.subcell_ratio
        return top + (cell_height - sub_height) / 2, left + (cell_width - sub_width) / 2, sub_width, sub_height
        
    def create_cells(self):
        self.cells = np.empty((self.board_width, self.board_height), dtype=pg.Rect)
        self.subcells = np.empty((self.board_width, self.board_height), dtype=pg.Rect)
        for i in range(self.board_width):
            for j in range(self.board_height):
                self.cells[i, j] = pg.Rect(*self.get_cell_coord(i, j))
                self.subcells[i, j] = pg.Rect(*self.get_subcell_coord(i, j))

    def create_grid(self):
        pg.draw.line(self.screen, self.contour_color, (0, self.contour_line_size/2 - 1), (self.game.width - 1, self.contour_line_size/2 - 1), self.contour_line_size)
        pg.draw.line(self.screen, self.contour_color, (self.contour_line_size/2 - 1, 0), (self.contour_line_size/2 - 1,self.game.height - 1), self.contour_line_size)
        pg.draw.line(self.screen, self.contour_color, (self.game.width - self.contour_line_size/2, 0), (self.game.width - self.contour_line_size/2, self.game.height), self.contour_line_size)
        pg.draw.line(self.screen, self.contour_color, (0, self.game.height - self.contour_line_size/2), (self.game.width, self.game.height - self.contour_line_size/2), self.contour_line_size)

        for i in range(self.board_width+1):
            width = self.row_width(i) + self.grid_line_size / 2 - 1
            pg.draw.line(self.screen, self.grid_color, (width , self.contour_line_size), (width, self.game.height - self.contour_line_size), self.grid_line_size)
        for j in range(self.board_height+1):
            height = self.line_height(j) + self.grid_line_size / 2 - 1
            pg.draw.line(self.screen, self.grid_color, (self.contour_line_size, height), (self.game.width - self.contour_line_size, height), self.grid_line_size)

    def display(self):
        for i in range(self.board_width):
            for j in range(self.board_height):
                if self.player_matrix[i, j] != 0 or True:
                    pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.cells[i, j])
        self.update_screen()
                    
    def init_colors(self):
        cmap = plt.cm.get_cmap('tab10', self.n_queen)
        self.colors_list = [tuple(int(c * 255) for c in cmap(i)[:3]) for i in range(self.n_queen)]
                
    def get_col(self, value) -> tuple[int, int, int]:
        return self.colors_list[value]
            
    def get_cell(self, pos) -> tuple[int, int]:
        cell_width = self.game.width // self.board_width
        cell_height = self.game.height // self.board_height
        return pos[0] // cell_width, pos[1] // cell_height
    
    def victory(self, debug=False):
        if self.n_queen != self.queens_placed:
            if debug:
                print(f"Wrong number of queens: {self.n_queen} not equal to {self.queens_placed}")
            return False
        if not all(map(len, self.colors_filled)):
            if debug:
                print(f"No queen for all colors: ", all(map(len, self.colors_filled)), map(len, self.colors_filled))
            return False
        for i in range(self.board_width):
            for j in range(self.board_height):
                if self.player_matrix[i, j] == 1:
                    break
            else:
                if debug:
                    print(f"No queen in line {i}")
                return False
        for j in range(self.board_height):
            for i in range(self.board_width):
                if self.player_matrix[i, j] == 1:
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
        if self.use_right_click:
            if self.player_matrix[i, j] == 1:
                self.remove_queen(i, j)
            elif self.player_matrix[i, j] != 2 and (self.allow_wrong_placements or self.can_place_queen(i, j)):
                if self.colors_filled[col] != [] and not self.allow_double_colors:
                    for i, j in self.colors_filled[col]:
                        self.remove_queen(i, j)
                self.place_queen(i, j)
            else:
                print("Cannot place Queen here")
        else:
            if self.player_matrix[i, j] == 0:
                self.place_noqueen(i, j)
            elif self.player_matrix[i, j] == 2:
                self.remove_noqueen(i, j)
                self.place_queen(i, j)
            elif self.player_matrix[i, j] == 1:
                self.remove_queen(i, j)
            else:
                raise NotImplementedError
            
    
    def right_click(self, pos):
        if self.use_right_click:
            i, j = self.get_cell(pos)
            if self.player_matrix[i, j] == 2:
                self.remove_noqueen(i, j)
                return            
            if self.player_matrix[i, j] == 1:
                if self.terminal_debug:
                    print("Queen already here")
                return            
            self.place_noqueen(i, j)
    
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
        
    def place_queen(self, i, j):
        if self.terminal_debug:
            print("Queen placed")
        self.player_matrix[i, j] = 1
        self.colors_filled[self.board_matrix[i, j]].append((i, j))
        self.queens_placed += 1
        left, top, cell_width, cell_height = self.get_subcell_coord(i, j)
        queen = pg.image.load("assets/queen.png")
        queen = pg.transform.scale(queen, (cell_width, cell_height))
        self.screen.blit(queen, (left, top))
        self.check_victory()
        self.update_screen()
    
    def remove_queen(self, i, j):
        if self.terminal_debug:
            print("Queen removed")
        self.player_matrix[i, j] = 0
        self.colors_filled[self.board_matrix[i, j]].remove((i, j))
        self.queens_placed -= 1
        pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.subcells[i, j])
        self.check_victory()
        self.update_screen()
        
    def place_noqueen(self, i, j):
        self.player_matrix[i, j] = 2
        left, top, cell_width, cell_height = self.get_subcell_coord(i, j)
        left, top, cell_width, cell_height = left + self.cross_line_size, top + self.cross_line_size, cell_width - 2 * self.cross_line_size, cell_height - 2 * self.cross_line_size
        pg.draw.line(self.screen, (0, 0, 0), (left, top), (left + cell_width, top + cell_height), self.cross_line_size)
        pg.draw.line(self.screen, (0, 0, 0), (left, top + cell_height), (left + cell_width, top), self.cross_line_size)
        self.update_screen()
        
    def remove_noqueen(self, i, j):
        self.player_matrix[i, j] = 0
        pg.draw.rect(self.screen, self.get_col(self.board_matrix[i, j]), self.subcells[i, j])
        self.update_screen()