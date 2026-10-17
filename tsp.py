import time
from itertools import permutations


def solve_tsp(vertices, distances, start=None, progress_callback=None):
    if not vertices:
        raise ValueError("É necessário informar pelo menos um vértice.")

    start_time = time.perf_counter()
    start = start or vertices[0]
    others = [vertex for vertex in vertices if vertex != start]
    total_permutations = 1
    for number in range(2, len(others) + 1):
        total_permutations *= number

    best_route = None
    best_cost = float("inf")
    evaluated = 0

    for ordering in permutations(others):
        route = (start,) + ordering + (start,)
        cost = sum(distances[route[i]][route[i + 1]] for i in range(len(route) - 1))
        evaluated += 1

        if cost < best_cost:
            best_cost = cost
            best_route = route

        if progress_callback and (
            evaluated % 25 == 0 or evaluated == total_permutations
        ):
            progress_callback(evaluated, total_permutations, best_route, best_cost)

    elapsed = time.perf_counter() - start_time
    return {
        "route": list(best_route),
        "cost": best_cost,
        "evaluated": evaluated,
        "total": total_permutations,
        "elapsed": elapsed,
    }


def solve_tsp_classic(vertices, graph, start=None, progress_callback=None):
    if not vertices:
        raise ValueError("É necessário informar pelo menos um vértice.")

    start_time = time.perf_counter()
    start = start or vertices[0]
    others = [vertex for vertex in vertices if vertex != start]
    total_permutations = 1
    for number in range(2, len(others) + 1):
        total_permutations *= number

    best_route = None
    best_cost = float("inf")
    evaluated = 0
    feasible_count = 0

    for ordering in permutations(others):
        route = (start,) + ordering + (start,)
        evaluated += 1

        if any(route[i + 1] not in graph[route[i]] for i in range(len(route) - 1)):
            continue

        feasible_count += 1
        cost = sum(graph[route[i]][route[i + 1]] for i in range(len(route) - 1))

        if cost < best_cost:
            best_cost = cost
            best_route = route

        if progress_callback and (
            evaluated % 25 == 0 or evaluated == total_permutations
        ):
            progress_callback(evaluated, total_permutations, best_route, best_cost)

    elapsed = time.perf_counter() - start_time
    feasible = best_route is not None
    return {
        "route": list(best_route) if feasible else [],
        "cost": best_cost if feasible else float("inf"),
        "evaluated": evaluated,
        "feasible_count": feasible_count,
        "total": total_permutations,
        "elapsed": elapsed,
        "feasible": feasible,
    }
