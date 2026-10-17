import heapq
import time


def dijkstra(graph, start):
    start_time = time.perf_counter()
    distances = {vertex: float("inf") for vertex in graph}
    previous = {vertex: None for vertex in graph}
    distances[start] = 0
    queue = [(0, start)]
    processed_order = []
    visited = set()

    while queue:
        current_distance, current = heapq.heappop(queue)

        if current in visited:
            continue
        if current_distance > distances[current]:
            continue

        visited.add(current)
        processed_order.append(current)

        for neighbor, weight in graph[current].items():
            if weight < 0:
                raise ValueError("Dijkstra não aceita pesos negativos.")

            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current
                heapq.heappush(queue, (new_distance, neighbor))

    elapsed = time.perf_counter() - start_time
    return distances, previous, processed_order, elapsed


def reconstruct_path(previous, start, target):
    if start == target:
        return [start]

    path = []
    current = target
    while current is not None:
        path.append(current)
        if current == start:
            path.reverse()
            return path
        current = previous[current]

    return []
