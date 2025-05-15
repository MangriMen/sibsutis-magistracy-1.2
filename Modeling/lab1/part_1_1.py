import numpy as np
import matplotlib.pyplot as plt


# Константа для экспоненциальной части
def exp_part(x):
    return 0.25 * np.exp(-(x + 0.25))


# Находим значение f(1) из экспоненциальной части
f1 = exp_part(1)

# Находим коэффициент k так, чтобы f(x) была непрерывна в точке x = 1
# f1 = k * (1 - 1.5) => k = -f1 / 0.5
k = -2 * f1


# Функция плотности вероятности
def pdf(x):
    if -0.25 < x < 1:
        return exp_part(x)
    elif 1 < x < 1.5:
        return k * (x - 1.5)
    else:
        return 0.0


# Простейшая численная интеграция для приближённой CDF
def cdf(x):
    if x <= -0.25:
        return 0.0
    elif x >= 1.5:
        return 1.0
    else:
        xs = np.linspace(-0.25, x, 1000)
        dx = xs[1] - xs[0]
        return np.sum([pdf(xi) for xi in xs]) * dx


# Векторизация
pdf_vec = np.vectorize(pdf)
cdf_vec = np.vectorize(cdf)

# Графики
x_vals = np.linspace(-0.5, 2, 500)
pdf_vals = pdf_vec(x_vals)
cdf_vals = cdf_vec(x_vals)

plt.figure(figsize=(12, 6))

# PDF
plt.subplot(1, 2, 1)
plt.plot(x_vals, pdf_vals)
plt.title("Плотность вероятности (PDF)")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.grid(True)

# CDF
plt.subplot(1, 2, 2)
plt.plot(x_vals, cdf_vals)
plt.title("Функция распределения (CDF)")
plt.xlabel("x")
plt.ylabel("F(x)")
plt.grid(True)

plt.tight_layout()
plt.show()

# Печать коэффициента
k
