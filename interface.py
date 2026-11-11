import math
import queue
import threading
import time
from itertools import pairwise

import pygame

import maps
from tsp import solve_tsp_brute_force_metric, solve_tsp_dijkstra

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
YELLOW_DIM = (105, 82, 12)
PURPLE = (167, 139, 250)
RED = (248, 113, 113)
EDGE = (68, 80, 102)

NODE_FILL = (45, 55, 74)
NODE_BORDER = (96, 111, 140)

WIDTH, HEIGHT = 1440, 950
HEADER_H = 86

PANEL_X = 916
PANEL_Y = 106
PANEL_WIDTH = 500
PANEL_HEIGHT = 812
PAD = 26
CONTENT_X = PANEL_X + PAD
CONTENT_WIDTH = PANEL_WIDTH - 2 * PAD

GRAPH_CENTER = (455, 505)
LEGEND_Y = HEIGHT - 44

MAP_CONFIG = {
    "brute_force": {
        "title": "Mapa de 5 vértices",
        "subtitle": "Força bruta nas permutações + caminhos mínimos por busca exaustiva",
        "control": "Força bruta (5)",
        "loader": maps.brute_force_map,
        "max_size": (600, 500),
        "node_radius": 28,
        "node_font": 22,
        "edge_font": 15,
        "badge_radius": 14,
        "badge_font": 12,
        "route_label": "Trajeto físico (caminhos mínimos)",
    },
    "dijkstra": {
        "title": "Mapa de 18 vértices",
        "subtitle": "Resolução exclusiva com Dijkstra (17! inviável por força bruta)",
        "control": "Dijkstra (18)",
        "loader": maps.dijkstra_map,
        "max_size": (800, 610),
        "node_radius": 16,
        "node_font": 13,
        "edge_font": 10,
        "badge_radius": 9,
        "badge_font": 9,
        "route_label": "Trajeto mínimo (Dijkstra)",
    },
}


def load_font(size, bold=False):
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


def fit_positions(raw_positions, center, max_width, max_height):
    xs = [x for x, _ in raw_positions.values()]
    ys = [y for _, y in raw_positions.values()]
    width = max(xs) - min(xs) or 1
    height = max(ys) - min(ys) or 1
    scale = min(max_width / width, max_height / height)
    offset_x, offset_y = min(xs), min(ys)
    used_width, used_height = width * scale, height * scale
    left = center[0] - used_width / 2
    top = center[1] - used_height / 2
    return {
        vertex: (
            int(round(left + (x - offset_x) * scale)),
            int(round(top + (y - offset_y) * scale)),
        )
        for vertex, (x, y) in raw_positions.items()
    }


def route_edges(route):
    return {tuple(sorted((a, b))) for a, b in pairwise(route)}


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
        self.options = options
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
        pygame.display.set_caption("Caixeiro Viajante — Força Bruta x Dijkstra")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = load_font(33, bold=True)
        self.font_subtitle = load_font(16)
        self.font_section = load_font(17, bold=True)
        self.font_body = load_font(17)
        self.font_small = load_font(15)
        self.font_tiny = load_font(13)
        self.font_micro = load_font(11)
        self.font_metric_value = load_font(21, bold=True)
        self.font_cost = load_font(31, bold=True)
        self.font_badge = load_font(14, bold=True)

        self.updates = queue.Queue()
        self.running = False

        self._build_controls()
        self.load_map("brute_force")

    def _build_controls(self):
        self.map_control = SegmentedControl(
            (520, 23, 430, 40),
            [
                ("brute_force", MAP_CONFIG["brute_force"]["control"]),
                ("dijkstra", MAP_CONFIG["dijkstra"]["control"]),
            ],
            active="brute_force",
        )
        self.play_button = Button((CONTENT_X, 232, CONTENT_WIDTH, 54), "▶  Iniciar execução", "primary")
        self.reset_button = Button((CONTENT_X, 298, CONTENT_WIDTH, 44), "Reiniciar", "ghost")
        self.buttons = [self.play_button, self.reset_button]

    def load_map(self, name):
        config = MAP_CONFIG[name]
        self.map_name = name
        self.config = config
        self.vertices, self.graph, raw_positions = config["loader"](scaled_positions=False)
        self.positions = fit_positions(
            raw_positions, GRAPH_CENTER, *config["max_size"]
        )
        self.node_radius = config["node_radius"]
        self.font_node = load_font(config["node_font"], bold=True)
        self.font_edge = load_font(config["edge_font"], bold=True)
        self.font_order = load_font(config["badge_font"], bold=True)
        self.badge_radius = config["badge_radius"]
        self.start = self.vertices[0]
        self.map_control.active = name
        self.reset_result()

    def reset_result(self):
        self.phase = "idle"
        self.running = False
        self.status = (
            "Mapa pronto. Clique em Iniciar execução."
            if self.map_name == "brute_force"
            else "Mapa pronto. O Dijkstra montará a rota passo a passo."
        )
        self.status_color = MUTED
        self.progress = 0.0
        self.dijkstra_progress = 0.0
        self.tour_progress = 0.0
        self.evaluated = 0
        self.total = 0
        self.elapsed = 0.0
        self.dijkstra_time = 0.0
        self.shortest_path_time = 0.0
        self.current_route = []
        self.current_cost = None
        self.current_edges = set()
        self.best_route = None
        self.best_cost = None
        self.best_edges = set()
        self.expanded_route = []
        self.path_edges = set()
        self.visited_order = {}
        self.result = None
        self.current_origin = None
        self.started_at = None

    def start_run(self):
        if self.running:
            return
        self.reset_result()
        self.running = True
        self.started_at = time.perf_counter()
        if self.map_name == "brute_force":
            self.phase = "brute"
            self.status = "Testando todas as permutações por força bruta..."
            self.status_color = YELLOW
        else:
            self.phase = "dijkstra"
            self.status = f"Dijkstra a partir da cidade {self.start}..."
            self.status_color = BLUE
        threading.Thread(target=self._compute, daemon=True).start()

    def _compute(self):
        if self.map_name == "brute_force":
            self._compute_brute_force()
        else:
            self._compute_dijkstra()

    def _compute_brute_force(self):
        def on_progress(state):
            self.updates.put(("brute_progress", state))
            time.sleep(0.1)

        result = solve_tsp_brute_force_metric(
            self.vertices,
            self.graph,
            start=self.start,
            progress_callback=on_progress,
            progress_every=1,
        )
        self.updates.put(("finished", result))

    def _compute_dijkstra(self):
        def on_step(state):
            self.updates.put(("dijkstra_step", state))
            time.sleep(0.11)

        result = solve_tsp_dijkstra(
            self.graph,
            self.vertices,
            start=self.start,
            step_callback=on_step,
        )
        self.updates.put(("finished", result))

    def process_updates(self):
        while True:
            try:
                update = self.updates.get_nowait()
            except queue.Empty:
                break

            kind = update[0]
            if kind == "brute_progress":
                self._apply_brute_progress(update[1])
            elif kind == "dijkstra_step":
                self._apply_dijkstra_step(update[1])
            elif kind == "finished":
                self._apply_finished(update[1])

    def _apply_brute_progress(self, state):
        self.phase = "brute"
        self.evaluated = state["evaluated"]
        self.total = state["total"]
        self.progress = self.evaluated / self.total if self.total else 0.0
        current_expanded = state.get("current_expanded") or []
        self.current_route = state["current_route"] if state["current_valid"] else []
        self.current_cost = state["current_cost"]
        self.current_edges = route_edges(current_expanded)
        if state["best_route"]:
            self.best_route = state["best_route"]
            self.best_cost = state["best_cost"]
            self.expanded_route = state.get("best_expanded") or list(self.best_route)
            self.best_edges = route_edges(self.expanded_route)

        route_text = " → ".join(self.current_route)
        if state["current_valid"]:
            self.status = (
                f"Testando {self.evaluated}/{self.total}: {route_text} "
                f"(custo {state['current_cost']})"
            )
            expanded_text = " → ".join(current_expanded)
            if expanded_text != route_text:
                self.status += f" · trajeto {expanded_text}"
            self.status_color = YELLOW
        else:
            self.status = (
                f"Testando {self.evaluated}/{self.total}: rota inválida "
                f"(falta aresta direta)"
            )
            self.status_color = RED

    def _apply_dijkstra_step(self, state):
        self.phase = "dijkstra"
        self.current_origin = state["origin"]
        self.expanded_route = state["expanded"]
        self.path_edges = route_edges(self.expanded_route)
        self.current_cost = state["cost"]
        self.dijkstra_time = state["dijkstra_time"]
        self.evaluated = state["step"]
        self.total = state["total"]
        self.dijkstra_progress = state["step"] / state["total"]
        self.tour_progress = state["step"] / state["total"]
        self.visited_order = {}
        for index, vertex in enumerate(state["tour"]):
            self.visited_order.setdefault(vertex, index + 1)
        self.status = (
            f"Dijkstra de {state['origin']} → {state['target']}: "
            f"caminho mínimo encontrado (parcial {state['cost']})"
        )
        self.status_color = BLUE

    def _apply_finished(self, result):
        self.result = result
        self.running = False
        self.phase = "done"
        self.elapsed = result.get("elapsed", 0.0)
        self.best_route = result.get("route") or []
        self.best_cost = result.get("cost")
        self.current_route = []
        self.current_edges = set()
        self.expanded_route = result.get("expanded") or list(self.best_route)
        self.path_edges = route_edges(self.expanded_route)
        self.best_edges = set(self.path_edges)
        self.evaluated = result.get("evaluated", 0)
        self.total = result.get("total", 0)
        self.progress = 1.0
        self.dijkstra_progress = 1.0 if self.map_name == "dijkstra" else 0.0
        self.tour_progress = 1.0 if self.map_name == "dijkstra" else 0.0
        self.dijkstra_time = result.get("dijkstra_time", 0.0)
        self.shortest_path_time = result.get("shortest_path_time", 0.0)
        self.visited_order = {}
        for index, vertex in enumerate(self.best_route):
            self.visited_order.setdefault(vertex, index + 1)
        self.status = "Concluído! A rota calculada está destacada no grafo."
        self.status_color = GREEN

    def node_at(self, pos):
        for vertex in self.vertices:
            x, y = self.positions[vertex]
            radius = self.node_radius + 6
            if (pos[0] - x) ** 2 + (pos[1] - y) ** 2 <= radius**2:
                return vertex
        return None

    def set_start(self, vertex):
        if self.running or vertex == self.start:
            return
        self.start = vertex
        self.reset_result()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        idle = not self.running
        for button in self.buttons:
            button.update(mouse_pos, enabled=idle)
        self.map_control.update(mouse_pos, enabled=idle)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            selected_map = self.map_control.clicked(event) if idle else None
            if selected_map is not None and selected_map != self.map_name:
                self.load_map(selected_map)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and idle:
                vertex = self.node_at(event.pos)
                if vertex is not None:
                    self.set_start(vertex)
                    continue

            if self.play_button.clicked(event):
                self.start_run()
            elif self.reset_button.clicked(event):
                self.reset_result()
            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and idle
            ):
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
            "Força bruta no mapa pequeno · Dijkstra no mapa grande",
            self.font_subtitle,
            MUTED,
            (38, 56),
        )
        self.map_control.draw(self.screen, self.font_small)
        self.draw_steps(WIDTH - 36, 43)

    def draw_steps(self, x_right, center_y):
        if self.map_name == "brute_force":
            steps = [("1", "Força bruta"), ("2", "Resultado")]
            if self.phase == "idle":
                state = [0, 0]
            elif self.phase == "brute":
                state = [1, 0]
            else:
                state = [2, 2]
        else:
            steps = [("1", "Dijkstra"), ("2", "Rota"), ("3", "Resultado")]
            if self.phase == "idle":
                state = [0, 0, 0]
            elif self.phase == "dijkstra":
                state = [1, 1, 0]
            else:
                state = [2, 2, 2]

        chips = []
        for index, (number, label) in enumerate(steps):
            text_w = self.font_small.size(label)[0]
            width = 30 + text_w + 16
            chips.append((width, number, label, state[index]))

        total_w = sum(chip[0] for chip in chips) + 12 * (len(chips) - 1)
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

        draw_text(self.screen, self.config["title"], self.font_section, TEXT, (36, 104))
        draw_text(self.screen, self.config["subtitle"], self.font_tiny, MUTED, (38, 132))

        self.draw_edges()
        self.draw_arrows()
        self.draw_edge_labels()
        self.draw_nodes()
        self.draw_legend()

    def _edge_list(self):
        edges = []
        for a in self.vertices:
            for b, weight in self.graph[a].items():
                if a >= b:
                    continue
                key = tuple(sorted((a, b)))
                edges.append((a, b, weight, key))
        return edges

    def draw_edges(self):
        for a, b, _weight, key in self._edge_list():
            start, end = self.positions[a], self.positions[b]
            if key in self.current_edges:
                pygame.draw.line(self.screen, YELLOW_DIM, start, end, 7)
            if key in self.path_edges and self.map_name == "dijkstra" and self.running:
                pygame.draw.line(self.screen, BLUE_DIM, start, end, 9)
                pygame.draw.line(self.screen, BLUE, start, end, 4)
            if key in self.best_edges:
                pygame.draw.line(self.screen, GREEN_DIM, start, end, 11)
                pygame.draw.line(self.screen, GREEN, start, end, 5)
            else:
                pygame.draw.line(self.screen, EDGE, start, end, 2)

    def draw_edge_labels(self):
        for a, b, weight, key in self._edge_list():
            start, end = self.positions[a], self.positions[b]
            mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            highlighted = (
                key in self.best_edges
                or key in self.path_edges
                or key in self.current_edges
            )
            label = self.font_edge.render(str(weight), True, TEXT if highlighted else YELLOW)
            if self.map_name == "dijkstra":
                pill = label.get_rect(center=mid).inflate(6, 3)
            else:
                pill = label.get_rect(center=mid).inflate(14, 8)
            draw_card(
                self.screen,
                pill,
                (25, 30, 41),
                radius=5 if self.map_name == "dijkstra" else 7,
                border=True,
                border_color=GREEN if highlighted else BORDER,
            )
            self.screen.blit(label, label.get_rect(center=mid))

    def draw_arrows(self):
        if not self.result:
            return
        for a, b in pairwise(self.expanded_route):
            self.draw_arrow_head(self.positions[a], self.positions[b], GREEN)

    def draw_arrow_head(self, start, end, color, size=15):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        if length < 1:
            return
        ux, uy = dx / length, dy / length
        tip = (end[0] - ux * self.node_radius, end[1] - uy * self.node_radius)
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

    def draw_nodes(self):
        route_nodes = set(self.best_route) if self.best_route else set()
        pulse = (math.sin(time.perf_counter() * 4.5) + 1) / 2

        for vertex in self.vertices:
            x, y = self.positions[vertex]
            in_route = vertex in route_nodes

            if in_route:
                fill, border, fg = GREEN, (186, 255, 222), (9, 30, 22)
            else:
                fill, border, fg = NODE_FILL, NODE_BORDER, TEXT

            if self.running and vertex == self.current_origin:
                ring = self.node_radius + 6 + int(pulse * 5)
                pygame.draw.circle(self.screen, BLUE, (x, y), ring, 3)
            elif vertex == self.start:
                pygame.draw.circle(self.screen, YELLOW, (x, y), self.node_radius + 7, 3)

            pygame.draw.circle(self.screen, (9, 11, 16), (x + 2, y + 4), self.node_radius + 2)
            pygame.draw.circle(self.screen, fill, (x, y), self.node_radius)
            pygame.draw.circle(self.screen, border, (x, y), self.node_radius, 3)
            draw_text(self.screen, vertex, self.font_node, fg, (x, y + 1), "center")

            if vertex in self.visited_order:
                self.draw_order_badge(x, y, self.visited_order[vertex])

    def draw_order_badge(self, x, y, number):
        radius = self.badge_radius
        bx = x + int(self.node_radius * 0.82)
        by = y - int(self.node_radius * 0.82)
        pygame.draw.circle(self.screen, (9, 11, 16), (bx, by), radius + 2)
        pygame.draw.circle(self.screen, PURPLE, (bx, by), radius)
        draw_text(
            self.screen,
            str(number),
            self.font_order,
            (22, 16, 40),
            (bx, by + 1),
            "center",
        )

    def draw_legend(self):
        items = [
            ("Início", YELLOW, "ring"),
            ("Cidade", NODE_BORDER, "dot"),
            (self.config["route_label"], GREEN, "dot"),
        ]
        if self.result:
            items.append(("Ordem de visita", PURPLE, "badge"))

        font = self.font_tiny
        widths = [font.size(label)[0] + 40 for label, _, _ in items]
        total = sum(widths) + 22 * (len(items) - 1)
        x = GRAPH_CENTER[0] - total // 2

        for (label, color, kind), width in zip(items, widths):
            if kind == "ring":
                pygame.draw.circle(self.screen, color, (x + 9, LEGEND_Y), 8, 2)
            elif kind == "badge":
                pygame.draw.circle(self.screen, (9, 11, 16), (x + 9, LEGEND_Y), 11)
                pygame.draw.circle(self.screen, color, (x + 9, LEGEND_Y), 9)
                draw_text(
                    self.screen,
                    "1",
                    self.font_tiny,
                    (22, 16, 40),
                    (x + 9, LEGEND_Y + 1),
                    "center",
                )
            else:
                pygame.draw.circle(self.screen, color, (x + 9, LEGEND_Y), 7)
            draw_text(self.screen, label, font, MUTED, (x + 24, LEGEND_Y), "midleft")
            x += width + 22

    def draw_panel(self):
        draw_card(self.screen, (PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT), PANEL, radius=18)

        self.draw_section_title("CONTROLES", 124)
        self.draw_start_card(148)
        self.play_button.label = "Executando..." if self.running else "▶  Iniciar execução"
        self.play_button.draw(self.screen, self.font_section)
        self.reset_button.draw(self.screen, self.font_small)

        self.draw_divider(360)
        self.draw_section_title("PROGRESSO", 372)
        self.draw_progress_rows()
        self.draw_status(510)

        self.draw_divider(560)
        self.draw_section_title("MÉTRICAS", 572)
        self.draw_metrics(596)

        self.draw_divider(714)
        self.draw_section_title("RESULTADO", 726)
        self.draw_result(752)

    def draw_start_card(self, y):
        rect = pygame.Rect(CONTENT_X, y, CONTENT_WIDTH, 66)
        draw_card(self.screen, rect, CARD, radius=12)
        draw_text(self.screen, "CIDADE INICIAL", self.font_tiny, MUTED, (rect.x + 16, rect.y + 10))
        draw_text(self.screen, self.start, self.font_metric_value, TEXT, (rect.x + 16, rect.y + 30))
        draw_text(
            self.screen,
            "clique em outra cidade no grafo",
            self.font_tiny,
            FAINT,
            (rect.right - 16, rect.y + 34),
            "midright",
        )

    def draw_section_title(self, label, y):
        pygame.draw.rect(self.screen, BLUE, (CONTENT_X, y + 3, 4, 16), border_radius=2)
        draw_text(self.screen, label, self.font_section, TEXT, (CONTENT_X + 14, y), "midleft")

    def draw_divider(self, y):
        pygame.draw.line(self.screen, BORDER, (CONTENT_X, y), (CONTENT_X + CONTENT_WIDTH, y), 1)

    def draw_progress_rows(self):
        if self.map_name == "brute_force":
            self.draw_progress_row(
                400,
                "Força bruta",
                f"{self.evaluated}/{self.total} permutações",
                self.progress,
                YELLOW,
            )
            self.draw_progress_row(
                452,
                "Caminhos mínimos",
                "busca exaustiva (sem Dijkstra)",
                1.0 if self.phase in ("brute", "done") else 0.0,
                GREEN,
            )
        else:
            self.draw_progress_row(
                400,
                "Dijkstra",
                f"{min(self.evaluated, self.total)}/{self.total} trechos",
                self.dijkstra_progress,
                BLUE,
            )
            self.draw_progress_row(
                452,
                "Montagem da rota",
                f"{min(self.evaluated, self.total)}/{self.total} cidades",
                self.tour_progress,
                PURPLE,
            )

    def draw_progress_row(self, y, label, value, progress, color):
        draw_text(self.screen, label, self.font_small, TEXT, (CONTENT_X, y), "midleft")
        draw_text(
            self.screen,
            value,
            self.font_tiny,
            MUTED,
            (CONTENT_X + CONTENT_WIDTH, y),
            "midright",
        )
        draw_progress_bar(self.screen, CONTENT_X, y + 20, CONTENT_WIDTH, 14, progress, color)

    def draw_status(self, y):
        draw_text(self.screen, "●", self.font_small, self.status_color, (CONTENT_X, y), "midleft")
        lines = wrap_text(self.status, self.font_small, CONTENT_WIDTH - 22)
        for index, line in enumerate(lines[:2]):
            draw_text(
                self.screen,
                line,
                self.font_small,
                self.status_color,
                (CONTENT_X + 20, y + index * 21),
                "midleft",
            )

    def draw_metrics(self, y):
        edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        if self.map_name == "dijkstra":
            path_label, path_value = "Tempo Dijkstra", f"{self.dijkstra_time:.4f} s"
        else:
            path_label, path_value = "Tempo caminhos", f"{self.shortest_path_time:.4f} s"
        cards = [
            ("Vértices", str(len(self.vertices)), BLUE),
            ("Arestas", str(edges), BLUE),
            ("Tempo total", f"{self.elapsed:.4f} s", PURPLE),
            (path_label, path_value, PURPLE),
        ]
        card_w = (CONTENT_WIDTH - 14) // 2
        card_h = 48
        for index, (label, value, accent) in enumerate(cards):
            col, row = index % 2, index // 2
            rect = pygame.Rect(
                CONTENT_X + col * (card_w + 14),
                y + row * (card_h + 12),
                card_w,
                card_h,
            )
            draw_card(self.screen, rect, CARD, radius=12)
            pygame.draw.rect(
                self.screen,
                accent,
                (rect.x, rect.y + 12, 3, card_h - 24),
                border_radius=2,
            )
            draw_text(self.screen, label, self.font_tiny, MUTED, (rect.x + 14, rect.y + 7))
            draw_text(self.screen, value, self.font_metric_value, TEXT, (rect.x + 14, rect.y + 24))

    def _draw_route_lines(self, route, y, color, max_lines=2):
        lines = wrap_route([str(vertex) for vertex in route], self.font_small, CONTENT_WIDTH)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] += " …"
        for index, line in enumerate(lines):
            draw_text(self.screen, line, self.font_small, color, (CONTENT_X, y + index * 20))

    def draw_result(self, y):
        result = self.result
        partial_route = self.best_route if (self.running and self.best_route) else None
        partial_cost = self.best_cost if partial_route else None
        dijkstra_partial = (
            self.map_name == "dijkstra"
            and self.running
            and self.expanded_route
            and self.current_cost is not None
        )

        if result:
            label = (
                "MENOR CUSTO TOTAL"
                if self.map_name == "brute_force"
                else "CUSTO TOTAL DA ROTA"
            )
            cost = result["cost"]
            route = result["route"]
            accent = GREEN
        elif dijkstra_partial:
            label = "CUSTO PARCIAL (Dijkstra)"
            cost = self.current_cost
            route = self.expanded_route
            accent = BLUE
        elif partial_route:
            label = "MELHOR CUSTO PARCIAL"
            cost = partial_cost
            route = partial_route
            accent = YELLOW
        else:
            draw_text(
                self.screen,
                "Clique em Iniciar execução para ver a rota.",
                self.font_small,
                MUTED,
                (CONTENT_X, y + 25),
            )
            return

        draw_text(self.screen, label, self.font_tiny, MUTED, (CONTENT_X, y))
        draw_text(self.screen, f"{cost}", self.font_cost, accent, (CONTENT_X, y + 13))

        if result:
            if self.map_name == "brute_force":
                detail = f"{result['evaluated']:,} permutações".replace(",", ".")
            else:
                detail = f"{result['steps']} trechos via Dijkstra"
            draw_text(
                self.screen,
                detail,
                self.font_tiny,
                MUTED,
                (CONTENT_X + CONTENT_WIDTH, y + 42),
                "midright",
            )

        order_y = y + 58
        draw_text(self.screen, "Ordem de visita:", self.font_tiny, MUTED, (CONTENT_X, order_y))
        route_color = GREEN if result else accent
        self._draw_route_lines(route, order_y + 19, route_color)

        if result and self.expanded_route:
            physical_y = order_y + 64
            draw_text(
                self.screen,
                self.config["route_label"] + ":",
                self.font_tiny,
                MUTED,
                (CONTENT_X, physical_y),
            )
            self._draw_route_lines(self.expanded_route, physical_y + 18, TEXT, max_lines=1)

    def draw_footer(self):
        draw_text(
            self.screen,
            "Clique em uma cidade para escolher o início · ESPAÇO inicia · Reiniciar limpa o resultado",
            self.font_tiny,
            FAINT,
            (36, HEIGHT - 24),
        )

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.process_updates()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def run_app():
    App().run()


if __name__ == "__main__":
    run_app()
