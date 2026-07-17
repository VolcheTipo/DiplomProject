"""
Генератор синтетических примеров сетевого трафика для тестирования.

Запуск: python data/generate_samples.py

Создаёт:
  - data/dataset.csv         — датасет с меткой label (0=нормальный, 1=аномалия)
  - data/normal_traffic.csv  — только нормальный трафик (для теста UI)
  - data/attack_traffic.csv  — смешанный трафик с атаками (для теста UI)
"""

import os
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.dirname(__file__)


# ───────────────────────────────────────────────
# Генераторы трафика
# ───────────────────────────────────────────────

NORMAL_PORTS = [80, 443, 53, 8080, 22, 25, 110, 143, 21, 3389]
PROTOCOLS = ["TCP", "UDP", "OTHER"]
INTERNAL_NETS = ["192.168.1.", "192.168.0.", "10.0.0.", "172.16.0."]


def random_ip(internal=True):
    if internal:
        net = random.choice(INTERNAL_NETS)
        return net + str(random.randint(1, 254))
    else:
        return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def generate_normal_flow():
    """Нормальный трафик: умеренный объём, стандартные порты."""
    proto = random.choices(PROTOCOLS, weights=[0.6, 0.35, 0.05])[0]
    return {
        "src_ip": random_ip(internal=True),
        "dst_ip": random_ip(internal=random.random() > 0.4),
        "src_port": random.randint(1024, 65535),
        "dst_port": random.choice(NORMAL_PORTS),
        "protocol": proto,
        "bytes": int(np.random.lognormal(mean=8, sigma=1.5)),   # ~3KB среднее
        "packets": int(np.random.lognormal(mean=3, sigma=1.0)),  # ~20 пакетов
        "label": 0,
    }


def generate_portscan_flow():
    """Сканирование портов: много потоков на разные порты, маленький объём."""
    return {
        "src_ip": random_ip(internal=False),
        "dst_ip": random_ip(internal=True),
        "src_port": random.randint(1024, 65535),
        "dst_port": random.randint(1, 65535),   # случайные порты
        "protocol": "TCP",
        "bytes": random.randint(40, 200),        # очень мало байт
        "packets": random.randint(1, 3),
        "label": 1,
    }


def generate_ddos_flow():
    """DDoS атака: огромный объём трафика с одного IP на один порт."""
    victim_ip = random_ip(internal=True)
    attacker = random_ip(internal=False)
    return {
        "src_ip": attacker,
        "dst_ip": victim_ip,
        "src_port": random.randint(1024, 65535),
        "dst_port": random.choice([80, 443, 53]),
        "protocol": random.choice(["TCP", "UDP"]),
        "bytes": int(np.random.lognormal(mean=14, sigma=0.5)),   # ~1MB+
        "packets": int(np.random.lognormal(mean=10, sigma=0.5)), # тысячи
        "label": 1,
    }


def generate_data_exfiltration_flow():
    """Утечка данных: большой исходящий трафик на нестандартный внешний порт."""
    return {
        "src_ip": random_ip(internal=True),
        "dst_ip": random_ip(internal=False),
        "src_port": random.randint(1024, 65535),
        "dst_port": random.choice([4444, 5555, 9999, 31337, 12345]),
        "protocol": "TCP",
        "bytes": int(np.random.lognormal(mean=13, sigma=1.0)),
        "packets": int(np.random.lognormal(mean=7, sigma=0.8)),
        "label": 1,
    }


def generate_bruteforce_flow():
    """Брутфорс SSH/RDP: много попыток подключения на стандартные порты."""
    return {
        "src_ip": random_ip(internal=False),
        "dst_ip": random_ip(internal=True),
        "src_port": random.randint(1024, 65535),
        "dst_port": random.choice([22, 3389, 23, 21]),
        "protocol": "TCP",
        "bytes": random.randint(200, 2000),
        "packets": random.randint(5, 30),
        "label": 1,
    }


# ───────────────────────────────────────────────
# Основная генерация
# ───────────────────────────────────────────────

def generate_dataset(n_normal=800, n_anomaly=200):
    rows = []

    # Нормальный трафик
    for _ in range(n_normal):
        rows.append(generate_normal_flow())

    # Аномальный трафик (разные типы атак)
    attack_generators = [
        generate_portscan_flow,
        generate_ddos_flow,
        generate_data_exfiltration_flow,
        generate_bruteforce_flow,
    ]
    for i in range(n_anomaly):
        gen = attack_generators[i % len(attack_generators)]
        rows.append(gen())

    random.shuffle(rows)
    return pd.DataFrame(rows)


def generate_test_csv(n_normal=150, n_anomaly=50, filename="attack_traffic.csv"):
    """Смешанный файл для демонстрации в UI."""
    rows = []
    for _ in range(n_normal):
        rows.append(generate_normal_flow())
    attack_gens = [generate_portscan_flow, generate_ddos_flow,
                   generate_data_exfiltration_flow, generate_bruteforce_flow]
    for i in range(n_anomaly):
        rows.append(attack_gens[i % len(attack_gens)]())
    random.shuffle(rows)
    df = pd.DataFrame(rows)
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Полный датасет для обучения модели (с метками)
    print("Генерация датасета для обучения...")
    df_full = generate_dataset(n_normal=800, n_anomaly=200)
    path_full = os.path.join(OUTPUT_DIR, "dataset.csv")
    df_full.to_csv(path_full, index=False)
    print(f"  ✓ {path_full}  ({len(df_full)} строк, "
          f"{df_full['label'].sum()} аномалий)")

    # 2. Только нормальный трафик (без метки, для UI)
    print("Генерация нормального трафика...")
    df_normal = pd.DataFrame([generate_normal_flow() for _ in range(200)])
    df_normal = df_normal.drop(columns=["label"])
    path_normal = os.path.join(OUTPUT_DIR, "normal_traffic.csv")
    df_normal.to_csv(path_normal, index=False)
    print(f"  ✓ {path_normal}  ({len(df_normal)} строк)")

    # 3. Смешанный трафик с атаками (без метки, для UI)
    print("Генерация трафика с атаками...")
    path_attack = generate_test_csv(n_normal=150, n_anomaly=50)
    df_attack = pd.read_csv(path_attack).drop(columns=["label"], errors="ignore")
    df_attack.to_csv(path_attack, index=False)
    print(f"  ✓ {path_attack}  ({len(df_attack)} строк)")

    print("\nГотово! Теперь обучите модель:")
    print("  python -m app.train_ml_model")
