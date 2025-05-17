import random
import math

from matplotlib import pyplot as plt


def simulate_trajectory(d, mu, p_absorb, trace=False):
    """
    Симулирует одну траекторию нейтрона в пластине толщиной d.

    :param d: толщина пластинки
    :param mu: средняя длина свободного пробега
    :param p_absorb: вероятность поглощения при столкновении
    :return: "pass", "reflect", or "absorb"
    """
    x = random.uniform(0, d)  # начальная абсцисса внутри пластины
    cos_theta = random.uniform(-1, 1)  # направление движения

    if trace:
        xs = [x]

    while True:
        # 1. Случайная длина свободного пробега по экспоненциальному закону
        lmbd = -mu * math.log(random.random())

        # 2. Вычисляем следующую абсциссу
        x_new = x + lmbd * cos_theta

        if trace:
            xs.append(x_new)

        # 3. Проверка выхода из пластинки
        if x_new >= d:
            return "pass", xs if trace else "pass"
        elif x_new <= 0:
            return "reflect", xs if trace else "reflect"

        # 4. Проверка поглощения
        gamma = random.random()
        if gamma < p_absorb:
            return "absorb", xs if trace else "absorb"

        # 5. Нейтрон остался внутри и рассеивается
        x = x_new
        cos_theta = random.uniform(-1, 1)  # новое направление


def simulate_many(N, d, mu, p_absorb):
    """
    Запускает моделирование N нейтронов и считает количество прошедших, отражённых и поглощённых частиц.

    :return: словарь с оценками вероятностей и абсолютными числами
    """
    passed = 0
    reflected = 0
    absorbed = 0

    for _ in range(N):
        result = simulate_trajectory(d, mu, p_absorb)[0]
        if result == "pass":
            passed += 1
        elif result == "reflect":
            reflected += 1
        elif result == "absorb":
            absorbed += 1

    return {
        "P_pass": passed / N,
        "P_reflect": reflected / N,
        "P_absorb": absorbed / N,
        "N_pass": passed,
        "N_reflect": reflected,
        "N_absorb": absorbed,
    }


def visualize_trajectories(M, d, mu, p_absorb):
    plt.figure(figsize=(10, 6))
    for _ in range(M):
        result, xs = simulate_trajectory(d, mu, p_absorb, trace=True)
        ys = list(range(len(xs)))  # номер столкновения по оси Y

        color = {"pass": "green", "reflect": "red", "absorb": "black"}[result]

        plt.plot(xs, ys, marker="o", color=color, alpha=0.7)

    plt.axvline(0, color="blue", linestyle="--", linewidth=1)
    plt.axvline(d, color="blue", linestyle="--", linewidth=1)
    plt.xlabel("Положение по оси X")
    plt.ylabel("Номер столкновения")
    plt.title(f"Визуализация {M} траекторий нейтронов в пластине (толщина = {d})")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    d = 10.0
    mu = 1.0
    p_absorb = 0.2
    N = 10000

    result = simulate_many(N, d, mu, p_absorb)

    print("Оценки вероятностей:")
    print(
        f"  Пройти сквозь пластину (P+): {result['P_pass']:.4f} ({result['N_pass']} частиц)"
    )
    print(
        f"  Отразиться (P-):             {result['P_reflect']:.4f} ({result['N_reflect']} частиц)"
    )
    print(
        f"  Быть поглощённым (P0):       {result['P_absorb']:.4f} ({result['N_absorb']} частиц)"
    )

    # Визуализация 30 траекторий
    visualize_trajectories(M=30, d=d, mu=mu, p_absorb=p_absorb)
