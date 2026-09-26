import pygame
import time
from queue import PriorityQueue
from configure import heuristic, reconstruct_path

def run_a_star(draw, grid, start, end):
    start_time = time.time()
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    
    open_set_hash = {start}
    nodes_explored = 0

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            cost = reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return "Algoritmo A-Star (A*)", time.time() - start_time, nodes_explored, cost

        for neighbor in current.neighbors:
            temp_g = g_score[current] + 1
            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score = temp_g + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score, count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        
        draw()
        if current != start:
            current.make_closed()
            nodes_explored += 1

    return "Algoritmo A-Star (A*)", time.time() - start_time, nodes_explored, "Falha (Sem caminho)"