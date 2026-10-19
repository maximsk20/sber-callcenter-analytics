import os
import pandas as pd
import numpy as np

# Определяем пути к данным
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(base_dir, ".."))
data_dir = os.path.join(project_root, "data")

calls_path = os.path.join(data_dir, "calls_log.csv")
operators_path = os.path.join(data_dir, "operators.csv")

print("1. Загрузка и объединение данных (merge)...")
calls = pd.read_csv(calls_path)
operators = pd.read_csv(operators_path)

# merge - объединяем звонки с операторами
df = pd.merge(calls, operators, on="operator_id", how="left")
df["call_start"] = pd.to_datetime(df["call_start"])
df = df.sort_values(by=["operator_id", "call_start"]).reset_index(drop=True)

print("2. Расчет отклонений по длительности (transform)...")
# transform - считаем среднее по теме звонка без сжатия строк
df["topic_mean_sec"] = df.groupby("call_topic")["duration_sec"].transform("mean")
df["duration_diff"] = df["duration_sec"] - df["topic_mean_sec"]

print("3. Разметка аномалий и сбросов (np.where)...")
# np.where - помечаем подозрительно короткие звонки со статусом 'Resolved'
df["is_fraud_short"] = np.where((df["duration_sec"] < 15) & (df["status"] == "Resolved"), 1, 0)
df["is_overlong"] = np.where((df["duration_sec"] > 1800) & (df["status"] != "Escalated"), 1, 0)
df["has_error"] = np.where((df["is_fraud_short"] == 1) | (df["is_overlong"] == 1), 1, 0)

print("4. Накопительные итоги по операторам (cumsum)...")
# cumsum - накопительное рабочее время оператора за смену
df["cumulative_work_sec"] = df.groupby("operator_id")["duration_sec"].cumsum()
df["cumulative_calls"] = df.groupby("operator_id").cumcount() + 1

print("5. Сводная матрица статусов по отделам (groupby + unstack):")
# unstack - разворачиваем группировку в двумерную матрицу
status_matrix = df.groupby(["department", "status"]).size().unstack(fill_value=0)
print(status_matrix)

print("\n6. Фильтрация и склеивание тегов (str.split + str.join)...")
# str.split и str.join - парсинг логов тегов
tags_list = df["tags"].str.split(";")
df["complaint_tags"] = tags_list.apply(
lambda items: " | ".join([t for t in items if t in ["жалоба", "претензия", "сбой_системы"]])
)

print("\n7. Топ-5 операторов с наибольшим процентом ошибок (срезы .iloc и .loc):")
# Группировка и срезы
op_summary = df.groupby(["operator_id", "department", "grade"]).agg(
total_calls=("call_id", "count"),
errors=("has_error", "sum"),
avg_csat=("csat_score", "mean")
).reset_index()

op_summary["error_pct"] = (op_summary["errors"] / op_summary["total_calls"] * 100).round(2)
worst_operators = op_summary.sort_values(by="error_pct", ascending=False).reset_index(drop=True)

# Срез .iloc - берем первые 5 строк
print(worst_operators.iloc[:5, [0, 1, 2, 3, 4, 6]])

# Срез .loc - операторы Junior с рейтингом ниже 3.8
risk_group = worst_operators.loc[(worst_operators["grade"] == "Junior") & (worst_operators["avg_csat"] < 3.8)]
print(f"\nОператоров в группе риска: {len(risk_group)}")
print("\nВСЕ АНАЛИТИЧЕСКИЕ ШАГИ ВЫПОЛНЕНЫ УСПЕШНО!")