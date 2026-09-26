import pygame

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================
WIDTH, HEIGHT = 800, 900
ROWS = 50

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
TURQUOISE = (64, 224, 208)
 
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row, self.col = row, col
        self.x, self.y = row * width, col * width
        self.width, self.total_rows = width, total_rows
        self.color = WHITE
        self.neighbors = []

    def get_pos(self): return self.row, self.col
    def is_barrier(self): return self.color == BLACK

    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = GREEN
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = TURQUOISE
    def make_path(self): self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < self.total_rows and 0 <= c < self.total_rows:
                if not grid[r][c].is_barrier():
                    self.neighbors.append(grid[r][c])


def heuristic(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def reconstruct_path(came_from, current, draw):
    cost = 0
    while current in came_from:
        current = came_from[current]
        current.make_path()
        cost += 1
        draw()
    return cost

def make_grid(rows, width):
    gap = width // rows
    return [[Node(i, j, gap, rows) for j in range(rows)] for i in range(rows)]

def clear_path(grid):
    for row in grid:
        for node in row:
            if node.color in [GREEN, RED, PURPLE]:
                node.reset()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos

    row = x // gap
    col = y // gap
    
    return row, col