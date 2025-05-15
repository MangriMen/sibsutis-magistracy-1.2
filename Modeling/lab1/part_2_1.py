import numpy as np
import matplotlib.pyplot as plt


# Определяем функции
def f(x):
    return x**2 + 2 * x


def g(x):
    return 3 * (x - 2) ** 2


# Генерируем n точек, равномерно заполняющих область
def generate_points(n):
    points = []
    while len(points) < n:
        x = np.random.uniform(0, 2)
        y = np.random.uniform(0, 3)
        if (x <= 1 and y <= f(x)) or (x > 1 and y <= g(x)):
            points.append((x, y))
    return np.array(points)


# Рисуем график
def plot_points(n):
    points = generate_points(n)
    x = np.linspace(0, 2, 500)
    y_f = [f(xi) if xi <= 1 else 0 for xi in x]
    y_g = [g(xi) if xi >= 1 else 0 for xi in x]

    plt.figure(figsize=(10, 6))
    plt.plot(x, y_f, "r-", label="$f(x) = x^2 + 2x$")
    plt.plot(x, y_g, "b-", label="$g(x) = 3(x-2)^2$")
    plt.scatter(
        points[:, 0], points[:, 1], s=5, c="green", alpha=0.5, label=f"{n} точек"
    )
    plt.fill_between(x, y_f, color="red", alpha=0.1)
    plt.fill_between(x, y_g, color="blue", alpha=0.1)
    plt.axhline(0, color="black", linewidth=0.5)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.title("Равномерное распределение точек в заданной области")
    plt.grid(True)
    plt.show()


# Пример вызова
plot_points(n=1000)
