import pygame
import time
from queue import PriorityQueue
from configure import heuristic, reconstruct_path

def run_greedy(draw, grid, start, end):
    start_time = time.time()
    count = 0
    open_set = PriorityQueue()
    open_set.put((heuristic(start.get_pos(), end.get_pos()), count, start))
    came_from = {}
    
    open_set_hash = {start}
    visited = {start}
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
            return "Busca Gulosa (Greedy)", time.time() - start_time, nodes_explored, cost

        for neighbor in current.neighbors:
            if neighbor not in visited:
                came_from[neighbor] = current
                visited.add(neighbor)
                count += 1
                h_score = heuristic(neighbor.get_pos(), end.get_pos())
                open_set.put((h_score, count, neighbor))
                open_set_hash.add(neighbor)
                neighbor.make_open()
        
        draw()
        if current != start:
            current.make_closed()
            nodes_explored += 1

    return "Busca Gulosa (Greedy)", time.time() - start_time, nodes_explored, "Falha (Sem caminho)"