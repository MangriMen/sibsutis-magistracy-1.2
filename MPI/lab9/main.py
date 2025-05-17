import numpy as np
import matplotlib.pyplot as plt
import random

# Параметры моделирования
arrival_rate = 1.0
mu1 = 0.9
mu2 = 0.3
num_servers_2 = 3

simulation_steps = 10000
dt = 0.01  # шаг времени
print_interval = 1.0  # интервал времени для периодического вывода в секундах


def poisson_event(rate):
    return random.random() < rate * dt


class SMO1:
    def __init__(self, service_rate):
        self.queue = []
        self.current = None
        self.remaining_time = 0.0
        self.service_rate = service_rate
        self.queue_lengths = []

    def step(self):
        if poisson_event(arrival_rate):
            self.queue.append(1)

        if self.current is not None:
            self.remaining_time -= dt
            if self.remaining_time <= 0:
                self.current = None

        if self.current is None and self.queue:
            self.queue.pop(0)
            self.current = 1
            self.remaining_time = np.random.exponential(1 / self.service_rate)

        self.queue_lengths.append(len(self.queue))


class SMO2:
    def __init__(self, service_rate, num_servers):
        self.queue = []
        self.servers = [None] * num_servers
        self.remaining_times = [0.0] * num_servers
        self.service_rate = service_rate
        self.num_servers = num_servers
        self.queue_lengths = []

    def step(self):
        if poisson_event(arrival_rate):
            self.queue.append(1)

        for i in range(self.num_servers):
            if self.servers[i] is not None:
                self.remaining_times[i] -= dt
                if self.remaining_times[i] <= 0:
                    self.servers[i] = None

        for i in range(self.num_servers):
            if self.servers[i] is None and self.queue:
                self.queue.pop(0)
                self.servers[i] = 1
                self.remaining_times[i] = np.random.exponential(1 / self.service_rate)

        self.queue_lengths.append(len(self.queue))


# Создание СМО
smo1 = SMO1(mu1)
smo2 = SMO2(mu2, num_servers_2)

# Запуск симуляции
for step in range(simulation_steps):
    smo1.step()
    smo2.step()

# Вычисления
time = np.linspace(0, simulation_steps * dt, simulation_steps)


def print_stats(label, queue_lengths):
    avg_len = np.mean(queue_lengths)
    max_len = np.max(queue_lengths)
    final_len = queue_lengths[-1]
    print(f"\n--- {label} ---")
    print(f"Средняя длина очереди: {avg_len:.3f}")
    print(f"Максимальная длина очереди: {max_len}")
    print(f"Длина очереди в конце: {final_len}")

    interval = int(print_interval / dt)
    print(f"\nДлина очереди каждые {print_interval} секунд:")
    for i in range(0, len(queue_lengths), interval):
        t = i * dt
        qlen = queue_lengths[i]
        print(f"t = {t:.2f}s: очередь = {qlen}")


# Вывод статистик
print_stats("СМО-1 (1 прибор, μ=0.9)", smo1.queue_lengths)
print_stats("СМО-2 (3 прибора, μ=0.3)", smo2.queue_lengths)

# График
plt.figure(figsize=(12, 6))
plt.plot(time, smo1.queue_lengths, label="СМО-1 (1 прибор, μ=0.9)")
plt.plot(time, smo2.queue_lengths, label="СМО-2 (3 прибора, μ=0.3)", alpha=0.7)
plt.xlabel("Время")
plt.ylabel("Длина очереди")
plt.title("Зависимость длины очереди от времени")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
