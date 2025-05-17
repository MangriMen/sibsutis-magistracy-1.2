import itertools
import time
import random
import matplotlib.pyplot as plt


# Вычисление времени выполнения последовательности
def calc_makespan(sequence, A, B):
    time_A = 0
    time_B = 0
    for i in sequence:
        time_A += A[i]
        time_B = max(time_A, time_B) + B[i]
    return time_B


def johnson_brute_force(A, B):
    n = len(A)
    best_seq = None
    best_time = float("inf")

    for perm in itertools.permutations(range(n)):
        t = calc_makespan(perm, A, B)
        if t < best_time:
            best_time = t
            best_seq = perm

    return list(best_seq), best_time


def johnson_algorithm(A, B):
    n = len(A)
    jobs = list(range(n))
    left = []
    right = []

    for job in jobs:
        if A[job] <= B[job]:
            left.append((A[job], job))
        else:
            right.append((B[job], job))

    left.sort()
    right.sort(reverse=True)

    sequence = [job for _, job in left] + [job for _, job in right]
    return sequence, calc_makespan(sequence, A, B)


# Генерация случайных данных
def generate_tasks(n, max_time=20):
    A = [random.randint(1, max_time) for _ in range(n)]
    B = [random.randint(1, max_time) for _ in range(n)]
    return A, B


def compare_johnson_algorithms():
    brute_times = []
    johnson_times = []
    ratios = []
    n_values = range(4, 17)

    for n in n_values:
        A, B = generate_tasks(n)

        print(f"\nДеталей: {n}")

        if n <= 11:
            start = time.perf_counter()
            johnson_brute_force(A, B)
            t_brute = time.perf_counter() - start
            print(f"  Полный перебор: {t_brute:.6f} сек")
        else:
            t_brute = None
            print(f"  Полный перебор: пропущен (слишком долго)")

        start = time.perf_counter()
        johnson_algorithm(A, B)
        t_johnson = time.perf_counter() - start
        print(f"  Алгоритм Джонсона: {t_johnson:.6f} сек")

        brute_times.append(t_brute)
        johnson_times.append(t_johnson)

        if t_brute is not None:
            ratio = t_brute / t_johnson if t_johnson > 0 else float("inf")
            print(f"  Отношение времени перебор/алгоритм Джонсона: {ratio:.2f}")
        else:
            ratio = None

        ratios.append(ratio)

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(n_values, ratios, marker="o", label="Brute / Johnson")
    plt.xlabel("Число деталей")
    plt.ylabel("Отношение времени")
    plt.title("Сравнение полного перебора и алгоритма Джонсона")
    plt.grid(True)
    plt.xticks(n_values)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    compare_johnson_algorithms()
