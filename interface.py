import math
import queue
import threading
import time
from itertools import pairwise

import pygame

from dijkstra import dijkstra, reconstruct_path
from generate_graph import generate_graph
from tsp import solve_tsp, solve_tsp_classic

# ---------------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------------
BACKGROUND = (14, 17, 24)
HEADER = (19, 23, 33)
PANEL = (23, 28, 39)
CARD = (31, 37, 51)
CARD_HOVER = (40, 48, 64)
BORDER = (50, 59, 78)
GRID_DOT = (29, 35, 47)

TEXT = (232, 238, 247)
MUTED = (138, 150, 171)
FAINT = (94, 104, 124)

BLUE = (88, 158, 255)
BLUE_DIM = (40, 78, 138)
GREEN = (52, 211, 153)
GREEN_DIM = (22, 84, 64)
YELLOW = (250, 204, 21)
PURPLE = (167, 139, 250)
RED = (248, 113, 113)
EDGE = (68, 80, 102)

NODE_FILL = (45, 55, 74)
NODE_BORDER = (96, 111, 140)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1440, 950
HEADER_H = 86

GRAPH_CENTER = (452, 528)
GRAPH_RADIUS = 300
NODE_RADIUS = 28

PANEL_X = 916
PANEL_Y = 106
PANEL_WIDTH = 500
PANEL_HEIGHT = 812
PAD = 26
CONTENT_X = PANEL_X + PAD
CONTENT_WIDTH = PANEL_WIDTH - 2 * PAD

def load_font(size, bold=False):
    """Carrega uma fonte agradável disponível no sistema (fallback embutido)."""
    for name in ("dejavusans", "liberationsans", "freesans", "ubuntu", "notosans"):
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size, bold=bold)


def mix(color_a, color_b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(color_a[i] + (color_b[i] - color_a[i]) * t) for i in range(3))


def draw_text(surface, text, font, color, pos, anchor="topleft"):
    image = font.render(text, True, color)
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def draw_card(surface, rect, color=CARD, radius=14, border=True, border_color=BORDER):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border_color, rect, width=1, border_radius=radius)


def draw_progress_bar(surface, x, y, width, height, progress, color):
    progress = max(0.0, min(1.0, progress))
    track = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (37, 44, 58), track, border_radius=height // 2)
    fill_width = int(width * progress)
    if fill_width >= height:
        fill = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, color, fill, border_radius=height // 2)
    elif fill_width > 0:
        pygame.draw.rect(surface, color, (x, y, height, height), border_radius=height // 2)


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if font.size(candidate)[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def wrap_route(route, font, max_width):
    if not route:
        return []
    lines, current = [], route[0]
    for vertex in route[1:]:
        candidate = current + " → " + vertex
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current + " →")
            current = vertex
    lines.append(current)
    return lines

class Button:
    def __init__(self, rect, label, kind="secondary"):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.kind = kind
        self.hovered = False
        self.enabled = True

    def update(self, mouse_pos, enabled=True):
        self.enabled = enabled
        self.hovered = enabled and self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def colors(self):
        if not self.enabled:
            return (30, 35, 46), (42, 49, 63), FAINT
        if self.kind == "primary":
            bg = mix(BLUE_DIM, BLUE, 0.55) if self.hovered else BLUE_DIM
            return bg, BLUE, TEXT
        if self.kind == "ghost":
            bg = CARD_HOVER if self.hovered else (26, 31, 42)
            return bg, BORDER, MUTED if not self.hovered else TEXT
        bg = CARD_HOVER if self.hovered else CARD
        return bg, BORDER, TEXT

    def draw(self, screen, font):
        bg, border, fg = self.colors()
        draw_card(screen, self.rect, bg, radius=12, border=True, border_color=border)
        draw_text(screen, self.label, font, fg, self.rect.center, anchor="center")


class SegmentedControl:
    def __init__(self, rect, options, active=None):
        self.rect = pygame.Rect(rect)
        self.options = options  # lista de (valor, rótulo)
        self.active = active if active is not None else options[0][0]
        self.hovered_index = None

    def _index_at(self, pos):
        if not self.rect.collidepoint(pos):
            return None
        seg_w = self.rect.width / len(self.options)
        index = int((pos[0] - self.rect.x) / seg_w)
        return max(0, min(len(self.options) - 1, index))

    def update(self, mouse_pos, enabled=True):
        self.hovered_index = self._index_at(mouse_pos) if enabled else None

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._index_at(event.pos)
            if index is not None:
                return self.options[index][0]
        return None

    def draw(self, screen, font):
        draw_card(screen, self.rect, (26, 31, 42), radius=12, border=True)
        seg_w = self.rect.width / len(self.options)
        for index, (value, label) in enumerate(self.options):
            seg = pygame.Rect(
                int(self.rect.x + index * seg_w) + 3,
                self.rect.y + 3,
                int(seg_w) - 6,
                self.rect.height - 6,
            )
            if value == self.active:
                draw_card(screen, seg, BLUE_DIM, radius=9, border=True, border_color=BLUE)
                fg = TEXT
            elif self.hovered_index == index:
                draw_card(screen, seg, CARD_HOVER, radius=9, border=False)
                fg = TEXT
            else:
                fg = MUTED
            draw_text(screen, label, font, fg, seg.center, anchor="center")


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Caixeiro Viajante — Dijkstra + TSP")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = load_font(33, bold=True)
        self.font_subtitle = load_font(16)
        self.font_section = load_font(17, bold=True)
        self.font_body = load_font(17)
        self.font_small = load_font(15)
        self.font_tiny = load_font(13)
        self.font_node = load_font(22, bold=True)
        self.font_metric_value = load_font(21, bold=True)
        self.font_cost = load_font(31, bold=True)
        self.font_badge = load_font(14, bold=True)

        self.vertex_count = 6
        self.model = "metric"
        self.updates = queue.Queue()
        self.running = False
        self.overall_start = None

        self._build_buttons()
        self.new_graph(self.vertex_count)

    def _build_buttons(self):
        stepper_y = 150
        self.count_box = pygame.Rect(CONTENT_X, stepper_y, 214, 44)
        self.minus_button = Button((CONTENT_X + 222, stepper_y, 46, 44), "−")
        self.plus_button = Button((CONTENT_X + 274, stepper_y, 46, 44), "+")
        half = (CONTENT_WIDTH - 16) // 2
        self.new_graph_button = Button((CONTENT_X, 204, half, 44), "Novo grafo")
        self.reset_button = Button((CONTENT_X + half + 16, 204, half, 44), "Limpar", "ghost")
        self.play_button = Button((CONTENT_X, 258, CONTENT_WIDTH, 54), "▶  Iniciar execução", "primary")
        self.buttons = [
            self.minus_button,
            self.plus_button,
            self.new_graph_button,
            self.play_button,
            self.reset_button,
        ]

        self.model_control = SegmentedControl(
            (560, 23, 360, 40),
            [("metric", "TSP + Dijkstra"), ("classic", "TSP Clássico")],
            active=self.model,
        )

    def layout_positions(self):
        center_x, center_y = GRAPH_CENTER
        result = {}
        count = len(self.vertices)
        for i, vertex in enumerate(self.vertices):
            angle = -math.pi / 2 + (2 * math.pi * i / count)
            result[vertex] = (
                int(center_x + GRAPH_RADIUS * math.cos(angle)),
                int(center_y + GRAPH_RADIUS * math.sin(angle)),
            )
        return result

    def set_model(self, model):
        self.model = model
        self.model_control.active = model
        self.new_graph(self.vertex_count)

    def new_graph(self, count=None):
        if count is not None:
            self.vertex_count = count
        self.vertices, self.graph, _ = generate_graph(
            self.vertex_count, ensure_hamiltonian=(self.model == "classic")
        )
        self.positions = self.layout_positions()
        self.selected_start = self.vertices[0]
        self.reset_result()

    def reset_result(self):
        self.phase = "idle"
        self.status = "Grafo pronto. Clique em Iniciar execução."
        self.status_color = MUTED
        self.current_origin = None
        self.processed_vertices = []

        self.dijkstra_completed = 0
        self.tsp_completed = 0
        self.tsp_total = 0
        self.elapsed_dijkstra = 0.0
        self.elapsed_tsp = 0.0

        self.dijkstra_progress = 0.0
        self.tsp_progress = 0.0
        self.dijkstra_shown = 0.0
        self.tsp_shown = 0.0

        self.distances = {}
        self.previous_by_source = {}
        self.tsp_result = None
        self.best_partial = None
        self.comparison = None

        self.expanded_route = []
        self.highlighted_edges = set()
        self.overall_start = None

    def start_run(self):
        self.reset_result()
        self.running = True
        if self.model == "classic":
            self.phase = "tsp"
            self.status = "Resolvendo o Caixeiro Viajante clássico (visita única)..."
            self.status_color = PURPLE
        else:
            self.phase = "dijkstra"
            self.status = "Executando Dijkstra para cada origem..."
            self.status_color = BLUE
        self.overall_start = time.perf_counter()
        threading.Thread(target=self._compute, daemon=True).start()

    def _compute(self):
        if self.model == "classic":
            self._compute_classic()
        else:
            self._compute_metric()

    @staticmethod
    def _tsp_progress_message(done, total_perm, best_route, best_cost):
        route = list(best_route) if best_route else []
        return ("tsp_progress", done, total_perm, route, best_cost)

    def _compute_classic(self):

        def on_progress(done, total_perm, best_route, best_cost):
            self.updates.put(
                self._tsp_progress_message(done, total_perm, best_route, best_cost)
            )

        result = solve_tsp_classic(
            self.vertices,
            self.graph,
            start=self.selected_start,
            progress_callback=on_progress,
        )
        self.updates.put(("finished", result))

    def _compute_metric(self):
        all_distances, all_previous = {}, {}
        dijkstra_total = 0.0

        for index, source in enumerate(self.vertices):
            self.updates.put(("dijkstra_state", source, index))
            dist, prev, order, elapsed = dijkstra(self.graph, source)
            all_distances[source] = dist
            all_previous[source] = prev
            dijkstra_total += elapsed
            self.updates.put(("dijkstra_state", source, index + 1, order))

        self.updates.put(("dijkstra_done", all_distances, all_previous, dijkstra_total))

        def on_tsp_progress(done, total_perm, best_route, best_cost):
            self.updates.put(
                self._tsp_progress_message(done, total_perm, best_route, best_cost)
            )

        result = solve_tsp(
            self.vertices,
            all_distances,
            start=self.selected_start,
            progress_callback=on_tsp_progress,
        )
        comparison = solve_tsp_classic(
            self.vertices, self.graph, start=self.selected_start
        )
        self.updates.put(("comparison", comparison))
        self.updates.put(("finished", result))

    def process_updates(self):
        while True:
            try:
                update = self.updates.get_nowait()
            except queue.Empty:
                break

            kind = update[0]
            if kind == "dijkstra_state":
                _, origin, completed, *rest = update
                self.phase = "dijkstra"
                self.current_origin = origin
                self.dijkstra_completed = completed
                self.dijkstra_progress = completed / len(self.vertices)
                if rest:
                    self.processed_vertices = rest[0]

            elif kind == "dijkstra_done":
                _, self.distances, self.previous_by_source, self.elapsed_dijkstra = update
                self.phase = "tsp"
                self.dijkstra_completed = len(self.vertices)
                self.dijkstra_progress = 1.0
                self.status = "Dijkstra concluído. Resolvendo o Caixeiro Viajante..."
                self.status_color = PURPLE

            elif kind == "tsp_progress":
                _, done, total, route, cost = update
                self.phase = "tsp"
                self.tsp_completed = done
                self.tsp_total = total
                self.tsp_progress = done / total if total else 0.0
                self.best_partial = (route, cost) if route else None
                self.status = "Avaliando permutações de rotas..."
                self.status_color = PURPLE

            elif kind == "comparison":
                _, self.comparison = update

            elif kind == "finished":
                _, self.tsp_result = update
                self.running = False
                self.phase = "done"
                self.elapsed_tsp = self.tsp_result["elapsed"]
                self.tsp_completed = self.tsp_total or self.tsp_result["total"]
                self.tsp_progress = 1.0
                self.status = "Concluído! A melhor rota está destacada no grafo."
                self.status_color = GREEN
                self._expand_route()

    def _expand_route(self):
        route = self.tsp_result["route"]
        if not route:
            self.expanded_route = []
            self.highlighted_edges = set()
            return

        if self.model == "classic":
            expanded = list(route)
        else:
            expanded = []
            for a, b in pairwise(route):
                segment = reconstruct_path(self.previous_by_source[a], a, b)
                if not segment:
                    continue
                expanded.extend(segment[1:] if expanded else segment)

        self.expanded_route = expanded
        self.highlighted_edges = set()
        for a, b in pairwise(expanded):
            self.highlighted_edges.add(tuple(sorted((a, b))))

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        idle = not self.running
        for button in self.buttons:
            button.update(mouse_pos, enabled=idle)
        self.model_control.update(mouse_pos, enabled=idle)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            selected_model = self.model_control.clicked(event) if idle else None
            if selected_model is not None and selected_model != self.model:
                self.set_model(selected_model)
                continue

            if self.minus_button.clicked(event) and self.vertex_count > 5:
                self.new_graph(self.vertex_count - 1)
            elif self.plus_button.clicked(event) and self.vertex_count < 10:
                self.new_graph(self.vertex_count + 1)
            elif self.new_graph_button.clicked(event):
                self.new_graph(self.vertex_count)
            elif self.reset_button.clicked(event):
                self.reset_result()
            elif self.play_button.clicked(event) or event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.running:
                self.start_run()

        return True

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_graph_area()
        self.draw_header()
        self.draw_panel()
        self.draw_footer()
        pygame.display.flip()

    def draw_header(self):
        pygame.draw.rect(self.screen, HEADER, (0, 0, WIDTH, HEADER_H))
        pygame.draw.line(self.screen, BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)

        draw_text(self.screen, "Caixeiro Viajante", self.font_title, TEXT, (36, 15))
        draw_text(
            self.screen,
            "Compare os dois modelos de TSP",
            self.font_subtitle,
            MUTED,
            (38, 56),
        )
        self.model_control.draw(self.screen, self.font_small)
        self.draw_steps(WIDTH - 36, 43)

    def draw_steps(self, x_right, center_y):
        if self.model == "classic":
            steps = [
                ("1", "Caixeiro Viajante"),
                ("2", "Resultado"),
            ]
            if self.phase == "idle":
                state = [0, 0]
            elif self.phase == "tsp":
                state = [1, 0]
            else:
                state = [2, 2]
        else:
            steps = [
                ("1", "Dijkstra"),
                ("2", "Caixeiro Viajante"),
                ("3", "Resultado"),
            ]
            if self.phase == "idle":
                state = [0, 0, 0]
            elif self.phase == "dijkstra":
                state = [1, 0, 0]
            elif self.phase == "tsp":
                state = [2, 1, 0]
            else:
                state = [2, 2, 2]

        chips = []
        for index, (number, label) in enumerate(steps):
            text_w = self.font_small.size(label)[0]
            width = 30 + text_w + 16
            chips.append((width, number, label, state[index]))

        total_w = sum(c[0] for c in chips) + 12 * (len(chips) - 1)
        x = x_right - total_w
        for width, number, label, st in chips:
            rect = pygame.Rect(x, center_y - 17, width, 34)
            if st == 1:
                bg, border, fg = BLUE_DIM, BLUE, TEXT
            elif st == 2:
                bg, border, fg = GREEN_DIM, GREEN, TEXT
            else:
                bg, border, fg = (26, 31, 42), BORDER, MUTED
            draw_card(self.screen, rect, bg, radius=17, border=True, border_color=border)

            circle_color = GREEN if st == 2 else (BLUE if st == 1 else (52, 61, 78))
            pygame.draw.circle(self.screen, circle_color, (x + 20, center_y), 11)
            draw_text(self.screen, number, self.font_badge, TEXT, (x + 20, center_y), "center")
            draw_text(self.screen, label, self.font_small, fg, (x + 38, center_y), "midleft")
            x += width + 12

    def draw_graph_area(self):
        area = pygame.Rect(0, HEADER_H, PANEL_X, HEIGHT - HEADER_H)
        for gx in range(area.left + 30, area.right, 42):
            for gy in range(area.top + 30, area.bottom, 42):
                pygame.draw.circle(self.screen, GRID_DOT, (gx, gy), 1)

        self.draw_edges()
        self.draw_arrows()
        self.draw_nodes()
        self.draw_edge_labels()
        self.draw_legend()

    def _edge_list(self):
        edges = []
        for a in self.vertices:
            for b, weight in self.graph[a].items():
                if a >= b:
                    continue
                key = tuple(sorted((a, b)))
                edges.append((a, b, weight, key in self.highlighted_edges))
        return edges

    def draw_edges(self):
        for a, b, _weight, highlighted in self._edge_list():
            start, end = self.positions[a], self.positions[b]
            if highlighted:
                pygame.draw.line(self.screen, GREEN_DIM, start, end, 11)
                pygame.draw.line(self.screen, GREEN, start, end, 5)
            else:
                pygame.draw.line(self.screen, EDGE, start, end, 3)

    def draw_edge_labels(self):
        for a, b, weight, highlighted in self._edge_list():
            start, end = self.positions[a], self.positions[b]
            mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            label = self.font_small.render(str(weight), True, TEXT if highlighted else YELLOW)
            pill = label.get_rect(center=mid).inflate(14, 8)
            draw_card(
                self.screen,
                pill,
                (25, 30, 41),
                radius=7,
                border=True,
                border_color=GREEN if highlighted else BORDER,
            )
            self.screen.blit(label, label.get_rect(center=mid))

    def draw_arrows(self):
        if not self.tsp_result:
            return
        for a, b in pairwise(self.expanded_route):
            self.draw_arrow_head(self.positions[a], self.positions[b], GREEN)

    def draw_arrow_head(self, start, end, color, size=15):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        if length < 1:
            return
        ux, uy = dx / length, dy / length
        tip = (end[0] - ux * NODE_RADIUS, end[1] - uy * NODE_RADIUS)
        base = (tip[0] - ux * size, tip[1] - uy * size)
        px, py = -uy, ux
        half = size * 0.62
        pygame.draw.polygon(
            self.screen,
            color,
            [
                tip,
                (base[0] + px * half, base[1] + py * half),
                (base[0] - px * half, base[1] - py * half),
            ],
        )

    def visit_order(self):
        order = {}
        if self.tsp_result:
            for index, vertex in enumerate(self.tsp_result["route"]):
                order.setdefault(vertex, index + 1)
        return order

    def draw_nodes(self):
        route_nodes = set(self.tsp_result["route"]) if self.tsp_result else set()
        order = self.visit_order()
        pulse = (math.sin(time.perf_counter() * 4.5) + 1) / 2

        for vertex in self.vertices:
            x, y = self.positions[vertex]
            in_route = vertex in route_nodes

            if in_route:
                fill, border, fg = GREEN, (186, 255, 222), (9, 30, 22)
            else:
                fill, border, fg = NODE_FILL, NODE_BORDER, TEXT

            if self.running and self.phase == "dijkstra" and vertex == self.current_origin:
                ring = NODE_RADIUS + 6 + int(pulse * 5)
                pygame.draw.circle(self.screen, BLUE, (x, y), ring, 3)
            elif vertex == self.selected_start:
                pygame.draw.circle(self.screen, YELLOW, (x, y), NODE_RADIUS + 7, 3)

            pygame.draw.circle(self.screen, (9, 11, 16), (x + 2, y + 4), NODE_RADIUS + 2)
            pygame.draw.circle(self.screen, fill, (x, y), NODE_RADIUS)
            pygame.draw.circle(self.screen, border, (x, y), NODE_RADIUS, 3)
            draw_text(self.screen, vertex, self.font_node, fg, (x, y + 1), "center")

            if vertex in order:
                self.draw_order_badge(x, y, order[vertex])

    def draw_order_badge(self, x, y, number):
        bx = x + int(NODE_RADIUS * 0.82)
        by = y - int(NODE_RADIUS * 0.82)
        pygame.draw.circle(self.screen, (9, 11, 16), (bx, by), 14)
        pygame.draw.circle(self.screen, PURPLE, (bx, by), 12)
        draw_text(self.screen, str(number), self.font_badge, (22, 16, 40), (bx, by + 1), "center")

    def draw_legend(self):
        route_item = (
            "Trajeto (arestas diretas)"
            if self.model == "classic"
            else "Trajeto físico (Dijkstra)"
        )
        items = [
            ("Início", YELLOW, "ring"),
            ("Cidade", NODE_BORDER, "dot"),
            (route_item, GREEN, "dot"),
        ]
        if self.tsp_result:
            items.append(("Ordem de visita", PURPLE, "badge"))

        font = self.font_tiny
        widths = [font.size(label)[0] + 40 for label, _, _ in items]
        total = sum(widths) + 22 * (len(items) - 1)
        x = GRAPH_CENTER[0] - total // 2
        y = HEIGHT - 72

        for (label, color, kind), width in zip(items, widths):
            if kind == "ring":
                pygame.draw.circle(self.screen, color, (x + 9, y), 8, 2)
            elif kind == "badge":
                pygame.draw.circle(self.screen, (9, 11, 16), (x + 9, y), 11)
                pygame.draw.circle(self.screen, color, (x + 9, y), 9)
                draw_text(self.screen, "1", self.font_tiny, (22, 16, 40), (x + 9, y + 1), "center")
            else:
                pygame.draw.circle(self.screen, color, (x + 9, y), 7)
            draw_text(self.screen, label, font, MUTED, (x + 24, y), "midleft")
            x += width + 22

        if self.tsp_result and self.tsp_result.get("feasible", True):
            note = (
                "Modo clássico: cada cidade é visitada uma única vez (arestas diretas)."
                if self.model == "classic"
                else "O trajeto verde segue os menores caminhos e pode passar por outras cidades."
            )
            draw_text(self.screen, note, font, FAINT, (GRAPH_CENTER[0], HEIGHT - 42), "center")

    def draw_panel(self):
        draw_card(self.screen, (PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT), PANEL, radius=18)

        self.draw_section_title("CONTROLES", 124)
        draw_card(self.screen, self.count_box, CARD, radius=12)
        draw_text(
            self.screen,
            f"Vértices: {self.vertex_count}",
            self.font_body,
            TEXT,
            self.count_box.center,
            "center",
        )
        self.minus_button.draw(self.screen, self.font_body)
        self.plus_button.draw(self.screen, self.font_body)
        self.new_graph_button.draw(self.screen, self.font_small)
        self.reset_button.draw(self.screen, self.font_small)
        self.play_button.draw(self.screen, self.font_section)

        self.draw_divider(330)
        self.draw_section_title("PROGRESSO", 342)
        if self.model == "classic":
            self.draw_progress_row(368, "Dijkstra", "não usado (clássico)", 0.0, BLUE)
        else:
            self.draw_progress_row(
                368,
                "Dijkstra",
                f"{self.dijkstra_completed}/{len(self.vertices)} origens",
                self.dijkstra_shown,
                BLUE,
            )
        self.draw_progress_row(
            420,
            "Caixeiro Viajante",
            f"{self.tsp_completed:,}/{self.tsp_total:,}".replace(",", ".") + " permutações",
            self.tsp_shown,
            PURPLE,
        )
        self.draw_status(474)

        self.draw_divider(512)
        self.draw_section_title("MÉTRICAS", 524)
        self.draw_metrics(548)

        self.draw_divider(678)
        self.draw_section_title("RESULTADO", 690)
        self.draw_result(718)

    def draw_section_title(self, label, y):
        pygame.draw.rect(self.screen, BLUE, (CONTENT_X, y + 3, 4, 16), border_radius=2)
        draw_text(self.screen, label, self.font_section, TEXT, (CONTENT_X + 14, y), "midleft")

    def draw_divider(self, y):
        pygame.draw.line(self.screen, BORDER, (CONTENT_X, y), (CONTENT_X + CONTENT_WIDTH, y), 1)

    def draw_progress_row(self, y, label, value, progress, color):
        draw_text(self.screen, label, self.font_small, TEXT, (CONTENT_X, y), "midleft")
        draw_text(self.screen, value, self.font_tiny, MUTED, (CONTENT_X + CONTENT_WIDTH, y), "midright")
        draw_progress_bar(self.screen, CONTENT_X, y + 20, CONTENT_WIDTH, 14, progress, color)

    def draw_status(self, y):
        draw_text(self.screen, "●", self.font_small, self.status_color, (CONTENT_X, y), "midleft")
        lines = wrap_text(self.status, self.font_small, CONTENT_WIDTH - 22)
        for index, line in enumerate(lines[:2]):
            draw_text(self.screen, line, self.font_small, self.status_color, (CONTENT_X + 20, y + index * 21), "midleft")

    def draw_metrics(self, y):
        edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        dijkstra_time = (
            f"{self.elapsed_dijkstra:.4f} s" if self.model == "metric" else "—"
        )
        cards = [
            ("Vértices", str(len(self.vertices)), BLUE),
            ("Arestas", str(edges), BLUE),
            ("Tempo Dijkstra", dijkstra_time, PURPLE),
            ("Tempo TSP", f"{self.elapsed_tsp:.4f} s", PURPLE),
        ]
        card_w = (CONTENT_WIDTH - 14) // 2
        card_h = 52
        for index, (label, value, accent) in enumerate(cards):
            col, row = index % 2, index // 2
            rect = pygame.Rect(CONTENT_X + col * (card_w + 14), y + row * (card_h + 12), card_w, card_h)
            draw_card(self.screen, rect, CARD, radius=12)
            pygame.draw.rect(self.screen, accent, (rect.x, rect.y + 12, 3, card_h - 24), border_radius=2)
            draw_text(self.screen, label, self.font_tiny, MUTED, (rect.x + 14, rect.y + 9))
            draw_text(self.screen, value, self.font_metric_value, TEXT, (rect.x + 14, rect.y + 26))

    def _draw_route_lines(self, route, y, color, max_lines=2):
        lines = wrap_route([str(v) for v in route], self.font_small, CONTENT_WIDTH)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] += " …"
        for index, line in enumerate(lines):
            draw_text(self.screen, line, self.font_small, color, (CONTENT_X, y + index * 20))

    def draw_result(self, y):
        result = self.tsp_result
        partial = self.best_partial if (self.phase == "tsp" and self.best_partial) else None

        if result and not result.get("feasible", True):
            draw_text(
                self.screen,
                "Sem rota clássica válida:",
                self.font_small,
                RED,
                (CONTENT_X, y + 4),
            )
            draw_text(
                self.screen,
                "o grafo não possui ciclo hamiltoniano.",
                self.font_small,
                MUTED,
                (CONTENT_X, y + 26),
            )
            return

        if result:
            prefix = " (clássico)" if self.model == "classic" else ""
            cost_label, cost_value = f"MENOR CUSTO TOTAL{prefix}", result["cost"]
            route, accent = result["route"], GREEN
        elif partial:
            cost_label, cost_value = "MELHOR CUSTO (parcial)", partial[1]
            route, accent = partial[0], YELLOW
        else:
            draw_text(
                self.screen,
                "Clique em Iniciar execução para ver a melhor rota.",
                self.font_small,
                MUTED,
                (CONTENT_X, y + 25),
            )
            return

        draw_text(self.screen, cost_label, self.font_tiny, MUTED, (CONTENT_X, y))
        draw_text(self.screen, f"{cost_value}", self.font_cost, accent, (CONTENT_X, y + 13))
        if result:
            evaluated = f"{result['evaluated']:,}".replace(",", ".")
            draw_text(
                self.screen,
                f"{evaluated} permutações",
                self.font_tiny,
                MUTED,
                (CONTENT_X + CONTENT_WIDTH, y + 56),
                "midright",
            )
            self.draw_comparison(y + 56)

        order_y = y + 80
        draw_text(self.screen, "Ordem de visita (TSP):", self.font_tiny, MUTED, (CONTENT_X, order_y))
        self._draw_route_lines(route, order_y + 20, GREEN if result else YELLOW)

        if result and self.expanded_route:
            phys_y = order_y + 58
            label = (
                "Trajeto no grafo (arestas diretas):"
                if self.model == "classic"
                else "Trajeto no grafo (Dijkstra):"
            )
            draw_text(self.screen, label, self.font_tiny, MUTED, (CONTENT_X, phys_y))
            self._draw_route_lines(self.expanded_route, phys_y + 20, TEXT)

    def draw_comparison(self, y):
        if self.model != "metric" or not self.comparison:
            return
        if self.comparison.get("feasible"):
            text = f"TSP Clássico (mesmo grafo): custo {self.comparison['cost']}"
            color = MUTED
        else:
            text = "TSP Clássico: inviável (sem ciclo hamiltoniano)"
            color = FAINT
        draw_text(self.screen, text, self.font_tiny, color, (CONTENT_X, y))

    def draw_footer(self):
        draw_text(
            self.screen,
            "Escolha o modelo no topo · ESPAÇO inicia · use + / − para 5 a 10 vértices",
            self.font_tiny,
            FAINT,
            (36, HEIGHT - 24),
        )

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.process_updates()

            self.dijkstra_shown += (self.dijkstra_progress - self.dijkstra_shown) * 0.2
            self.tsp_shown += (self.tsp_progress - self.tsp_shown) * 0.2

            self.draw()
            self.clock.tick(60)

        pygame.quit()


def run_app():
    App().run()


if __name__ == "__main__":
    run_app()
