import os

import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовым DataFrame транзакций."""
    data = {
        "Дата операции": [
            pd.Timestamp("2020-05-15"),  # Входит в 3-месячный интервал
            pd.Timestamp("2020-05-16"),  # Входит в 3-месячный интервал
            pd.Timestamp("2020-01-01"),  # Слишком старая транзакция
        ],
        "Категория": ["Супермаркеты", "Фастфуд", "Супермаркеты"],
        "Сумма платежа": [-1500.0, -500.0, -2000.0],
    }
    return pd.DataFrame(data)


def test_spending_by_category(sample_transactions):
    """Тест фильтрации трат по конкретной категории за последние 3 месяца."""
    result_df = spending_by_category(sample_transactions, category="Супермаркеты", date="2020-05-20")

    assert len(result_df) == 1
    assert result_df["Сумма платежа"].iloc[0] == -1500.0
    # Проверяем, что декоратор создал файл в папке reports/
    assert os.path.exists(os.path.join("reports", "spending_by_category.xlsx"))


def test_spending_by_weekday(sample_transactions):
    """Тест расчета средних трат по дням недели."""
    result_df = spending_by_weekday(sample_transactions, date="2020-05-20")

    # 15.05.2020 — это Пятница, 16.05.2020 — это Суббота
    assert len(result_df) == 2
    assert "Пятница" in result_df["День недели"].values
    assert "Суббота" in result_df["День недели"].values
    assert os.path.exists(os.path.join("reports", "spending_by_weekday.xlsx"))
