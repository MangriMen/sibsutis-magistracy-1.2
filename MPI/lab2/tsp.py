import itertools
import time
import random
import matplotlib.pyplot as plt


def generate_distance_matrix(n, max_dist=100):
    return [
        [random.randint(1, max_dist) if i != j else 0 for j in range(n)]
        for i in range(n)
    ]


def calc_distance(route, dist_matrix):
    return (
        sum(dist_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))
        + dist_matrix[route[-1]][route[0]]
    )


def tsp_brute_force(dist_matrix):
    n = len(dist_matrix)
    min_distance = float("inf")
    best_route = None

    for perm in itertools.permutations(range(1, n)):
        route = [0] + list(perm)
        dist = calc_distance(route, dist_matrix)
        if dist < min_distance:
            min_distance = dist
            best_route = route

    return best_route + [0], min_distance


def tsp_held_karp(dist_matrix):
    n = len(dist_matrix)
    memo = {}

    for k in range(1, n):
        memo[(1 << k, k)] = (dist_matrix[0][k], 0)

    for subset_size in range(2, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            bits = sum(1 << k for k in subset)
            for k in subset:
                prev = bits & ~(1 << k)
                res = []
                for m in subset:
                    if m == k:
                        continue
                    res.append((memo[(prev, m)][0] + dist_matrix[m][k], m))
                memo[(bits, k)] = min(res)

    bits = (1 << n) - 2
    res = [(memo[(bits, k)][0] + dist_matrix[k][0], k) for k in range(1, n)]
    opt_cost, parent = min(res)

    path = [0]
    bits = (1 << n) - 2
    last = parent

    for _ in range(n - 1):
        path.append(last)
        new_bits = bits & ~(1 << last)
        _, last = memo[(bits, last)]
        bits = new_bits

    path.append(0)
    return path, opt_cost


def compare_algorithms():
    brute_times = []
    dp_times = []
    ratios = []
    cities_range = range(4, 17)

    for n in cities_range:
        matrix = generate_distance_matrix(n)

        print(f"\nГорода: {n}")

        if n <= 10:
            start = time.perf_counter()
            tsp_brute_force(matrix)
            brute_time = time.perf_counter() - start
            print(f"  Полный перебор: {brute_time:.6f} сек")
        else:
            brute_time = None
            print(f"  Полный перебор: пропущен (слишком долго)")

        start = time.perf_counter()
        tsp_held_karp(matrix)
        dp_time = time.perf_counter() - start
        print(f"  Held-Karp (DP): {dp_time:.6f} сек")

        brute_times.append(brute_time)
        dp_times.append(dp_time)

        if brute_time is not None:
            ratio = brute_time / dp_time if dp_time > 0 else float("inf")
            print(
                f"  Отношение времени перебор/динамическое программирование: {ratio:.2f}"
            )
        else:
            ratio = None

        ratios.append(ratio)

    plt.figure(figsize=(10, 5))
    plt.plot(cities_range, ratios, marker="o", label="Ratio (Brute / DP)")
    plt.xlabel("Число пунктов маршрута")
    plt.ylabel("Отношение времени (перебор / DP)")
    plt.title("Сравнение полного перебора и динамического программирования (Held-Karp)")
    plt.grid(True)
    plt.xticks(cities_range)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    compare_algorithms()
