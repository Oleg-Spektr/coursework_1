import json
import os
from datetime import datetime

import pandas as pd


def load_user_settings(filepath: str = "user_settings.json") -> dict:
    """Загружает пользовательские настройки из файла JSON."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Дефолтные значения, если файл еще не создан
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}


def load_transactions(filepath: str = os.path.join("data", "operations.xls")) -> pd.DataFrame:
    """Читает транзакции из Excel-файла (работает с .xls и .xlsx) и возвращает DataFrame."""
    try:
        df = pd.read_excel(filepath)
    except Exception:
        # На случай, если у файла расширение .xlsx
        alt_path = filepath + "x" if filepath.endswith(".xls") else filepath
        df = pd.read_excel(alt_path)

    # Приводим ключевую колонку дат к формату datetime для фильтрации
    if "Дата операции" in df.columns:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    return df


def filter_transactions_by_date(df: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """Фильтрует транзакции с начала месяца до указанной даты включительно."""
    try:
        # Убираем dayfirst=True и добавляем format="mixed", чтобы pandas сам автоматически
        # и без предупреждений распознавал любые форматы дат (и '2020-05-20', и '20.05.2020')
        target_date = pd.to_datetime(date_str, format="mixed")
    except Exception:
        target_date = datetime.now()

    # Начало месяца для переданной даты
    start_date = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Оставляем строки, попадающие в этот диапазон
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= target_date)]
    return filtered_df
