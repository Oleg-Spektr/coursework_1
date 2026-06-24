import json

import pandas as pd

from src.utils import filter_transactions_by_date, load_user_settings


def test_load_user_settings_success(tmp_path):
    """Тест успешной загрузки настроек из JSON."""
    settings_data = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    file_path = tmp_path / "test_settings.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(settings_data, f)

    result = load_user_settings(str(file_path))
    assert result == settings_data


def test_load_user_settings_file_not_found():
    """Тест возврата дефолтных настроек, если файл отсутствует."""
    result = load_user_settings("non_existent_file.json")
    assert "user_currencies" in result
    assert "user_stocks" in result


def test_filter_transactions_by_date():
    """Тест фильтрации транзакций от начала месяца до указанной даты."""
    # Создаем тестовый DataFrame
    data = {
        "Дата операции": [
            pd.Timestamp("2020-05-01 10:00:00"),
            pd.Timestamp("2020-05-15 12:00:00"),
            pd.Timestamp("2020-05-25 15:00:00"),  # Выходит за рамки target_date
            pd.Timestamp("2020-04-30 23:00:00"),  # Прошлый месяц
        ],
        "Сумма платежа": [-100, -200, -300, -400],
    }
    df = pd.DataFrame(data)

    # Фильтруем по 20 мая 2020 года
    result_df = filter_transactions_by_date(df, "2020-05-20 23:59:59")

    # Должны остаться только первые две транзакции
    assert len(result_df) == 2
    assert -100 in result_df["Сумма платежа"].values
    assert -200 in result_df["Сумма платежа"].values
    assert -300 not in result_df["Сумма платежа"].values
