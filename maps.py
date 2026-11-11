"""Grafos fixos extraídos das imagens do projeto.

Cada mapa guarda os vértices, as arestas (com os pesos lidos das imagens) e as
posições originais em pixels. As funções ``brute_force_map`` e
``dijkstra_map`` devolvem ``(vertices, graph, positions)`` no mesmo formato de
``generate_graph.generate_graph``, para poderem ser usadas direto pelas
implementações de força bruta e de Dijkstra.

- ``images/brute_force_map.png``: 5 vértices, usado na força bruta.
- ``images/dijkstra_map.png``: 18 vértices, usado no Dijkstra.
"""

from __future__ import annotations

BRUTE_FORCE_VERTICES = ["1", "2", "3", "4", "5"]

BRUTE_FORCE_EDGES = [
    ("1", "2", 2),
    ("2", "3", 4),
    ("2", "4", 3),
    ("1", "4", 3),
    ("3", "4", 7),
    ("1", "5", 6),
    ("4", "5", 3),
    ("3", "5", 3),
]

BRUTE_FORCE_POSITIONS = {
    "1": (27.5, 112.5),
    "2": (127.5, 40.0),
    "3": (220.0, 110.0),
    "4": (75.0, 195.0),
    "5": (170.0, 197.5),
}

DIJKSTRA_VERTICES = [str(i) for i in range(1, 19)]

DIJKSTRA_EDGES = [
    ("1", "2", 20),
    ("1", "8", 29),
    ("1", "12", 29),
    ("1", "13", 37),
    ("2", "3", 25),
    ("2", "8", 28),
    ("2", "12", 39),
    ("3", "4", 25),
    ("3", "8", 30),
    ("3", "13", 54),
    ("4", "5", 39),
    ("4", "6", 32),
    ("4", "7", 42),
    ("4", "9", 23),
    ("4", "10", 33),
    ("4", "14", 56),
    ("5", "6", 12),
    ("5", "7", 26),
    ("5", "10", 19),
    ("6", "7", 17),
    ("6", "10", 35),
    ("6", "11", 30),
    ("7", "11", 38),
    ("8", "12", 25),
    ("8", "13", 22),
    ("9", "10", 26),
    ("9", "13", 34),
    ("9", "14", 56),
    ("9", "16", 43),
    ("10", "11", 24),
    ("10", "14", 30),
    ("10", "15", 19),
    ("11", "15", 26),
    ("11", "18", 36),
    ("12", "13", 27),
    ("12", "16", 43),
    ("13", "14", 24),
    ("13", "16", 19),
    ("14", "15", 20),
    ("14", "16", 19),
    ("14", "17", 17),
    ("15", "17", 18),
    ("15", "18", 21),
    ("16", "17", 26),
    ("17", "18", 15),
]

DIJKSTRA_POSITIONS = {
    "1": (27.0, 128.0),
    "2": (45.5, 69.0),
    "3": (121.5, 51.5),
    "4": (205.5, 41.75),
    "5": (303.75, 90.25),
    "6": (309.5, 41.25),
    "7": (349.5, 16.5),
    "8": (105.0, 139.25),
    "9": (177.5, 111.5),
    "10": (250.5, 127.75),
    "11": (337.5, 125.75),
    "12": (63.0, 198.25),
    "13": (153.0, 199.25),
    "14": (223.0, 204.75),
    "15": (276.0, 173.0),
    "16": (182.75, 245.0),
    "17": (267.0, 236.75),
    "18": (317.5, 224.5),
}

MAPS = {
    "brute_force": {
        "vertices": BRUTE_FORCE_VERTICES,
        "edges": BRUTE_FORCE_EDGES,
        "positions": BRUTE_FORCE_POSITIONS,
    },
    "dijkstra": {
        "vertices": DIJKSTRA_VERTICES,
        "edges": DIJKSTRA_EDGES,
        "positions": DIJKSTRA_POSITIONS,
    },
}


def build_graph(vertices, edges):
    """Constrói um grafo não direcionado ``{vertice: {vizinho: peso}}``."""
    graph = {vertex: {} for vertex in vertices}
    for a, b, weight in edges:
        if a not in graph or b not in graph:
            raise ValueError(f"Aresta com vértice inexistente: {(a, b)}")
        if weight < 0:
            raise ValueError(f"Dijkstra exige pesos não negativos: {(a, b)}")
        if b in graph[a]:
            raise ValueError(f"Aresta duplicada: {(a, b)}")
        graph[a][b] = weight
        graph[b][a] = weight
    return graph


def fit_positions(raw_positions, center=(390, 310), max_size=410):
    """Reposiciona as coordenadas da imagem preservando o formato original."""
    xs = [x for x, _ in raw_positions.values()]
    ys = [y for _, y in raw_positions.values()]
    width = max(xs) - min(xs) or 1
    height = max(ys) - min(ys) or 1
    scale = min(max_size / width, max_size / height)
    offset_x = min(xs)
    offset_y = min(ys)
    used_width = width * scale
    used_height = height * scale
    left = center[0] - used_width / 2
    top = center[1] - used_height / 2
    return {
        vertex: (
            int(round(left + (x - offset_x) * scale)),
            int(round(top + (y - offset_y) * scale)),
        )
        for vertex, (x, y) in raw_positions.items()
    }


def get_map(name, scaled_positions=True):
    """Retorna ``(vertices, graph, positions)`` de um dos mapas fixos."""
    try:
        data = MAPS[name]
    except KeyError as error:
        raise ValueError(f"Mapa desconhecido: {name!r}. Use {sorted(MAPS)}.") from error

    vertices = list(data["vertices"])
    graph = build_graph(vertices, data["edges"])
    positions = data["positions"]
    if scaled_positions:
        positions = fit_positions(positions)
    return vertices, graph, positions


def brute_force_map(scaled_positions=True):
    """Grafo de 5 vértices da imagem ``brute_force_map.png``."""
    return get_map("brute_force", scaled_positions)


def dijkstra_map(scaled_positions=True):
    """Grafo de 18 vértices da imagem ``dijkstra_map.png``."""
    return get_map("dijkstra", scaled_positions)


def is_connected(graph):
    """Indica se todos os vértices estão na mesma componente conexa."""
    if not graph:
        return False
    start = next(iter(graph))
    visited = {start}
    stack = [start]
    while stack:
        current = stack.pop()
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return len(visited) == len(graph)


def describe(graph):
    """Resumo simples usado nos testes manuais/CLI."""
    edges = sum(len(neighbors) for neighbors in graph.values()) // 2
    return {
        "vertices": len(graph),
        "edges": edges,
        "connected": is_connected(graph),
    }


if __name__ == "__main__":
    for map_name in MAPS:
        vertices, graph, positions = get_map(map_name)
        info = describe(graph)
        print(f"{map_name}: {info}")
        for vertex in vertices:
            neighbors = ", ".join(
                f"{neighbor}({weight})" for neighbor, weight in graph[vertex].items()
            )
            print(f"  {vertex}: {neighbors}")
        print()
