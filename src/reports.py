import functools
import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def report_to_file(filename_or_func=None):
    """Декоратор для функций-отчетов. Записывает возвращаемый DataFrame в Excel-файл.

    Поддерживает вызов как без параметров @report_to_file, так и с ними @report_to_file("name.xlsx").
    """
    default_filename = "report_default.xlsx"

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(filename_or_func, str):
                target_filename = filename_or_func
            else:
                target_filename = default_filename

            # Вызываем саму функцию отчета
            result_df = func(*args, **kwargs)

            # Если функция вернула DataFrame, сохраняем его в файл Excel
            if isinstance(result_df, pd.DataFrame):
                try:
                    os.makedirs("reports", exist_ok=True)
                    filepath = os.path.join("reports", target_filename)
                    result_df.to_excel(filepath, index=False, engine="openpyxl")
                    logger.info(f"Отчет успешно сохранен в файл: {filepath}")
                except Exception as e:
                    logger.error(f"Ошибка при сохранении отчета в файл {target_filename}: {e}")
            else:
                logger.warning("Функция отчета вернула объект, отличный от pandas.DataFrame. Файл не сохранен.")

            return result_df

        return wrapper

    # Проверяем, как был вызван декоратор
    if callable(filename_or_func):
        func_to_return = filename_or_func
        filename_or_func = default_filename
        return decorator(func_to_return)

    return decorator


@report_to_file("spending_by_category.xlsx")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца от переданной даты."""
    logger.info(f"Генерация отчета по категории '{category}'")

    if date:
        try:
            target_date = pd.to_datetime(date, format="mixed")
        except Exception:
            logger.warning(f"Не удалось распарсить дату '{date}', используется текущее время.")
            target_date = datetime.now()
    else:
        target_date = datetime.now()

    # Вычисляем дату начала периода (3 месяца назад)
    start_date = target_date - pd.DateOffset(months=3)

    df = transactions.copy()
    if "Дата операции" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["Дата операции"]):
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="mixed")

    # Фильтруем по датам, категории (регистронезависимо) и берем только расходы (Сумма платежа < 0)
    filtered_df = df[
        (df["Дата операции"] >= start_date)
        & (df["Дата операции"] <= target_date)
        & (df["Категория"].str.lower() == category.lower())
        & (df["Сумма платежа"] < 0)
    ]

    return filtered_df


@report_to_file("spending_by_weekday.xlsx")
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает средние траты в каждый из дней недели за последние три месяца от переданной даты."""
    logger.info("Генерация отчета 'Траты по дням недели'")

    if date:
        try:
            target_date = pd.to_datetime(date, format="mixed")
        except Exception:
            logger.warning(f"Не удалось распарсить дату '{date}', используется текущее время.")
            target_date = datetime.now()
    else:
        target_date = datetime.now()

    start_date = target_date - pd.DateOffset(months=3)

    df = transactions.copy()
    if "Дата операции" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["Дата операции"]):
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="mixed")

    # Фильтруем: период 3 месяца и только расходы
    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= target_date) & (df["Сумма платежа"] < 0)
    ].copy()

    if filtered_df.empty:
        logger.warning("Нет данных для формирования отчета за указанный период.")
        return pd.DataFrame(columns=["День недели", "Средние траты"])

    # Переводим расходы в положительные числа для расчета среднего чека
    filtered_df["Сумма платежа"] = filtered_df["Сумма платежа"].abs()

    # Выделяем день недели (0 = Понедельник, 6 = Воскресенье)
    filtered_df["День недели номер"] = filtered_df["Дата операции"].dt.weekday

    weekday_map = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    }
    filtered_df["День недели"] = filtered_df["День недели номер"].map(weekday_map)

    # Группируем по дням недели и считаем среднее арифметическое трат
    report_df = filtered_df.groupby(["День недели номер", "День недели"])["Сумма платежа"].mean().reset_index()
    report_df = report_df.sort_values(by="День недели номер")

    # Формируем финальную структуру
    report_df = report_df[["День недели", "Сумма платежа"]].rename(columns={"Сумма платежа": "Средние траты"})
    report_df["Средние траты"] = report_df["Средние траты"].round(2)

    return report_df
