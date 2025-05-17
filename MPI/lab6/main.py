import random
import math
import matplotlib.pyplot as plt


def simulate_buffon_needle(l: float, a: float, N: int) -> float:
    """Симулирует N бросков и возвращает экспериментальную вероятность"""
    success = 0
    for _ in range(N):
        x = random.uniform(0, a / 2)
        theta = random.uniform(0, math.pi / 2)
        if x <= (l / 2) * math.sin(theta):
            success += 1
    return success / N


def theoretical_probability(l: float, a: float) -> float:
    return (2 * l) / (a * math.pi)


def run_experiment(l: float, a: float, steps: int, max_N: int):
    Ns = [int(max_N * i / steps) for i in range(1, steps + 1)]
    deltas = []

    P_theoretical = theoretical_probability(l, a)

    for N in Ns:
        P_exp = simulate_buffon_needle(l, a, N)
        delta = abs(P_theoretical - P_exp) / P_theoretical
        deltas.append(delta)
        print(f"N={N}, P_exp={P_exp:.5f}, Δ={delta:.5f}")

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(Ns, deltas, marker="o", label="Δ = |P - P_exp| / P")
    plt.xlabel("Число бросков N")
    plt.ylabel("Нормированное отклонение Δ")
    plt.title("Зависимость Δ от числа бросков N")
    plt.grid(True)
    plt.legend()
    plt.show()


# Параметры (можно менять)
l = 1.0  # длина иглы
a = 2.0  # расстояние между линиями (l / a = 0.5)
run_experiment(l=l, a=a, steps=30, max_N=10000)
