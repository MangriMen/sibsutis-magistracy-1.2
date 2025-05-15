import numpy as np
import matplotlib.pyplot as plt


# Определяем функции
def f(x):
    return x**2 + 2 * x


def g(x):
    return 3 * (x - 2) ** 2


# Генерируем n точек, равномерно заполняющих область
def generate_points_on_boundary(n):
    """Генерация точек на границах области (на f(x) и g(x))."""
    points = []
    for _ in range(n):
        if np.random.rand() < 0.5:
            # Точка на f(x): x ∈ [0, 1]
            x = np.random.uniform(0, 1)
            y = f(x)
        else:
            # Точка на g(x): x ∈ [1, 2]
            x = np.random.uniform(1, 2)
            y = g(x)
        points.append((x, y))
    return np.array(points)


# Рисуем график
def plot_boundary_points(n):
    points = generate_points_on_boundary(n)
    x = np.linspace(0, 2, 500)
    y_f = [f(xi) if xi <= 1 else np.nan for xi in x]
    y_g = [g(xi) if xi >= 1 else np.nan for xi in x]

    plt.figure(figsize=(10, 6))
    plt.plot(x, y_f, "r-", label="$f(x) = x^2 + 2x$")
    plt.plot(x, y_g, "b-", label="$g(x) = 3(x - 2)^2$")
    plt.scatter(
        points[:, 0],
        points[:, 1],
        s=10,
        c="purple",
        alpha=0.7,
        label=f"{n} точек на границе",
    )
    plt.axhline(0, color="black", linewidth=0.5)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.title("Точки на границах области (f и g)")
    plt.grid(True)
    plt.show()


# Пример вызова
plot_boundary_points(n=1000)
