import time
from itertools import permutations

from dijkstra import dijkstra, reconstruct_path


def solve_tsp_brute_force(
    vertices, graph, start=None, progress_callback=None, progress_every=1
):
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
        valid = all(route[i + 1] in graph[route[i]] for i in range(len(route) - 1))
        cost = None

        if valid:
            feasible_count += 1
            cost = sum(graph[route[i]][route[i + 1]] for i in range(len(route) - 1))
            if cost < best_cost:
                best_cost = cost
                best_route = route

        if progress_callback and (
            evaluated % max(1, progress_every) == 0 or evaluated == total_permutations
        ):
            progress_callback(
                {
                    "evaluated": evaluated,
                    "total": total_permutations,
                    "current_route": list(route),
                    "current_valid": valid,
                    "current_cost": cost,
                    "best_route": list(best_route) if best_route else None,
                    "best_cost": best_cost if best_route else None,
                }
            )

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


def solve_tsp_dijkstra(graph, vertices, start=None, step_callback=None):
    if not vertices:
        raise ValueError("É necessário informar pelo menos um vértice.")

    start_time = time.perf_counter()
    start = start or vertices[0]
    unvisited = set(vertices)
    unvisited.discard(start)

    tour = [start]
    expanded = [start]
    cost = 0.0
    dijkstra_time = 0.0
    current = start
    steps = 0
    total = len(vertices)

    while unvisited:
        distances, previous, _order, elapsed = dijkstra(graph, current)
        dijkstra_time += elapsed
        target = min(unvisited, key=lambda vertex: (distances[vertex], vertex))
        path = reconstruct_path(previous, current, target)
        cost += distances[target]
        expanded.extend(path[1:])
        tour.append(target)
        unvisited.discard(target)
        steps += 1

        if step_callback:
            step_callback(
                {
                    "tour": list(tour),
                    "expanded": list(expanded),
                    "cost": cost,
                    "origin": current,
                    "target": target,
                    "step": steps,
                    "total": total,
                    "dijkstra_time": dijkstra_time,
                }
            )

        current = target

    distances, previous, _order, elapsed = dijkstra(graph, current)
    dijkstra_time += elapsed
    path = reconstruct_path(previous, current, start)
    cost += distances[start]
    expanded.extend(path[1:])
    tour.append(start)
    steps += 1

    if step_callback:
        step_callback(
            {
                "tour": list(tour),
                "expanded": list(expanded),
                "cost": cost,
                "origin": current,
                "target": start,
                "step": steps,
                "total": total,
                "dijkstra_time": dijkstra_time,
            }
        )

    elapsed = time.perf_counter() - start_time
    return {
        "route": tour,
        "expanded": expanded,
        "cost": cost,
        "dijkstra_time": dijkstra_time,
        "elapsed": elapsed,
        "steps": steps,
        "total": total,
        "evaluated": steps,
        "feasible": True,
    }


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
