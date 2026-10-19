import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

np.random.seed(42)
random.seed(42)


def generate_call_center_data(num_calls=25000):
    print("Генерация данных контактного центра Сбера...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    operator_ids = [f"OP_{100 + i}" for i in range(40)]
    departments = ["Кредитование", "Дебетовые карты", "Техподдержка СберОнлайн", "Претензии"]
    grades = ["Junior", "Middle", "Senior"]

    operators_df = pd.DataFrame({
        "operator_id": operator_ids,
        "department": [random.choice(departments) for _ in operator_ids],
        "grade": [random.choices(grades, weights=[0.5, 0.35, 0.15])[0] for _ in operator_ids],
        "shift": [random.choice(["Day", "Night"]) for _ in operator_ids]
    })

    call_topics = [
        "Блокировка перевода",
        "Оформление кредита",
        "Сбой мобильного банка",
        "Комиссия за обслуживание",
        "Перевыпуск карты",
        "Консультация по вкладам"
    ]

    possible_tags = [
        "жалоба", "повторный_звонок", "ошибка_клиента", "сбой_системы",
        "грубость", "эскалация", "решено_быстро", "претензия", "vip_клиент"
    ]

    statuses = ["Resolved", "Escalated", "Dropped"]
    start_time_base = datetime(2024, 1, 1, 8, 0, 0)

    records = []
    for i in range(1, num_calls + 1):
        op_id = random.choice(operator_ids)
        client_id = f"CL_{random.randint(10000, 99999)}"
        topic = random.choice(call_topics)

        rand_val = random.random()
        if rand_val < 0.05:
            duration = random.randint(3, 15)
            status = "Dropped" if random.random() < 0.7 else "Resolved"
        elif rand_val > 0.96:
            duration = random.randint(1200, 3600)
            status = random.choice(["Escalated", "Resolved"])
        else:
            duration = int(np.random.normal(loc=240, scale=80))
            duration = max(30, duration)
            status = random.choices(statuses, weights=[0.8, 0.15, 0.05])[0]

        call_start = start_time_base + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 11),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        call_end = call_start + timedelta(seconds=duration)

        tags_sample = random.sample(possible_tags, k=random.randint(1, 3))
        tags_str = ";".join(tags_sample)

        csat = random.choices([1, 2, 3, 4, 5, None], weights=[0.05, 0.05, 0.1, 0.3, 0.4, 0.1])[0]

        records.append({
            "call_id": f"CALL_{i:06d}",
            "operator_id": op_id,
            "client_id": client_id,
            "call_topic": topic,
            "call_start": call_start.strftime("%Y-%m-%d %H:%M:%S"),
            "call_end": call_end.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_sec": duration,
            "status": status,
            "tags": tags_str,
            "csat_score": csat
        })

    calls_df = pd.DataFrame(records)

    calls_file = os.path.join(data_dir, "calls_log.csv")
    operators_file = os.path.join(data_dir, "operators.csv")

    calls_df.to_csv(calls_file, index=False, encoding="utf-8")
    operators_df.to_csv(operators_file, index=False, encoding="utf-8")
    print("УСПЕХ! Созданы файлы звонков и операторов!")


if __name__ == "__main__":
    generate_call_center_data()
