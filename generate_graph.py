import math
import random


def _components(graph, vertices):
    remaining = set(vertices)
    components = []
    while remaining:
        start = next(iter(remaining))
        component = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in graph[current]:
                if neighbor not in component:
                    component.add(neighbor)
                    stack.append(neighbor)
        remaining -= component
        components.append(component)
    return components


def _ensure_connected(graph, vertices, rng, min_weight, max_weight):
    components = _components(graph, vertices)
    while len(components) > 1:
        first, second = components.pop(), components.pop()
        a, b = rng.choice(sorted(first)), rng.choice(sorted(second))
        weight = rng.randint(min_weight, max_weight)
        graph[a][b] = weight
        graph[b][a] = weight
        components.append(first | second)


def generate_graph(
    vertex_count: int,
    min_weight: int = 1,
    max_weight: int = 20,
    seed=None,
    ensure_hamiltonian: bool = False,
):
    if not 5 <= vertex_count <= 10:
        raise ValueError("A quantidade de vértices deve estar entre 5 e 10.")

    rng = random.Random(seed)
    vertices = [chr(ord("A") + i) for i in range(vertex_count)]
    graph = {vertex: {} for vertex in vertices}

    shuffled = vertices[:]
    rng.shuffle(shuffled)
    for i in range(1, vertex_count):
        a = shuffled[i]
        b = rng.choice(shuffled[:i])
        weight = rng.randint(min_weight, max_weight)
        graph[a][b] = weight
        graph[b][a] = weight

    possible_edges = [
        (a, b)
        for i, a in enumerate(vertices)
        for b in vertices[i + 1 :]
        if b not in graph[a]
    ]
    rng.shuffle(possible_edges)
    extra_count = rng.randint(1, max(1, min(len(possible_edges), vertex_count)))
    for a, b in possible_edges[:extra_count]:
        weight = rng.randint(min_weight, max_weight)
        graph[a][b] = weight
        graph[b][a] = weight

    if ensure_hamiltonian:
        cycle = vertices[:]
        rng.shuffle(cycle)
        for i, a in enumerate(cycle):
            b = cycle[(i + 1) % len(cycle)]
            if b not in graph[a]:
                weight = rng.randint(min_weight, max_weight)
                graph[a][b] = weight
                graph[b][a] = weight

    _ensure_connected(graph, vertices, rng, min_weight, max_weight)

    center_x, center_y = 390, 310
    radius = 205
    positions = {}
    for i, vertex in enumerate(vertices):
        angle = -math.pi / 2 + (2 * math.pi * i / vertex_count)
        positions[vertex] = (
            int(center_x + radius * math.cos(angle)),
            int(center_y + radius * math.sin(angle)),
        )

    return vertices, graph, positions
