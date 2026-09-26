import pygame
from configure import *
from a_star import run_a_star
from greedy_search import run_greedy

pygame.init()
pygame.font.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Busca: A* vs Busca Gulosa")
FONT = pygame.font.SysFont("Arial", 22)

def draw_ui(win, grid, rows, width, metrics=None):
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win)
            
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))
    
    pygame.draw.rect(win, BLACK, (0, width, width, HEIGHT - width))
    
    if metrics:
        algo_name, elapsed_time, nodes_explored, cost = metrics
        texts = [
            FONT.render(f"Algoritmo: {algo_name}", True, WHITE),
            FONT.render(f"Tempo: {elapsed_time:.4f} seg", True, WHITE),
            FONT.render(f"Nós Explorados: {nodes_explored}", True, WHITE),
            FONT.render(f"Custo do Caminho: {cost}", True, WHITE)
        ]
        win.blit(texts[0], (20, width + 20))
        win.blit(texts[1], (400, width + 20))
        win.blit(texts[2], (20, width + 50))
        win.blit(texts[3], (400, width + 50))
    else:
        inst = FONT.render("A = Algoritmo A* | G = Busca Gulosa | C = Limpar | Esq = Desenhar | Dir = Apagar", True, ORANGE)
        win.blit(inst, (20, width + 35))

    pygame.display.update()

def main():
    grid = make_grid(ROWS, WIDTH)
    start = end = metrics = None
    run = True

    while run:
        draw_ui(WIN, grid, ROWS, WIDTH, metrics)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Controles do Mouse
            if pygame.mouse.get_pressed()[0]: # Click Esquerdo
                pos = pygame.mouse.get_pos()
                if pos[1] < WIDTH:
                    row, col = get_clicked_pos(pos, ROWS, WIDTH)
                    node = grid[row][col]
                    
                    if not start and node != end:
                        start = node
                        start.make_start()
                    elif not end and node != start:
                        end = node
                        end.make_end()
                    elif node != end and node != start:
                        node.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # Click Direito
                pos = pygame.mouse.get_pos()
                if pos[1] < WIDTH:
                    row, col = get_clicked_pos(pos, ROWS, WIDTH)
                    node = grid[row][col]
                    node.reset()
                    if node == start: start = None
                    if node == end: end = None

            # Controles do Teclado
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_g] and start and end:
                    clear_path(grid) # Limpa rota anterior
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                            
                    if event.key == pygame.K_a:
                        metrics = run_a_star(lambda: draw_ui(WIN, grid, ROWS, WIDTH, metrics), grid, start, end)
                    elif event.key == pygame.K_g:
                        metrics = run_greedy(lambda: draw_ui(WIN, grid, ROWS, WIDTH, metrics), grid, start, end)

                if event.key == pygame.K_c:
                    start = end = metrics = None
                    grid = make_grid(ROWS, WIDTH)

    pygame.quit()

if __name__ == "__main__":
    main()