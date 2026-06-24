import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import get_greeting, main_page_view


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (1, "Доброй ночи"),
    ],
)
def test_get_greeting(hour, expected_greeting):
    """Тест соответствия приветствий временным интервалам из ТЗ."""
    dt = datetime(2020, 5, 20, hour, 0, 0)
    assert get_greeting(dt) == expected_greeting


@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.load_transactions")
@patch("src.views.load_user_settings")
def test_main_page_view_success(mock_settings, mock_load_tx, mock_stocks, mock_currencies):
    """Комплексный тест формирования JSON для главной страницы."""

    # Мокаем настройки пользователя
    mock_settings.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    # Мокаем ответы внешних API
    mock_currencies.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

    # Мокаем тестовые транзакции в Excel
    tx_data = {
        "Дата операции": [pd.Timestamp("2020-05-10 10:00:00"), pd.Timestamp("2020-05-11 11:00:00")],
        "Номер карты": ["*1234", "*1234"],
        "Сумма платежа": [-1500.0, -2500.0],  # Общие траты 4000, кэшбэк 40
        "Категория": ["Супермаркеты", "Фастфуд"],
        "Описание": ["Покупка 1", "Покупка 2"],
    }
    mock_load_tx.return_value = pd.DataFrame(tx_data)

    # Вызываем тестирование главной страницы для 20 мая (день, 14:00)
    response_json = main_page_view("2020-05-20 14:00:00")
    response = json.loads(response_json)

    # Проверяем структуру и значения ответа
    assert response["greeting"] == "Добрый день"
    assert response["currency_rates"][0]["currency"] == "USD"
    assert response["stock_prices"][0]["stock"] == "AAPL"

    # Проверяем расчет по картам
    assert response["cards"][0]["last_4"] == "1234"
    assert response["cards"][0]["total_spent"] == 4000.0
    assert response["cards"][0]["cashback"] == 40

    # Проверяем наличие топ-транзакций (отсортированных по убыванию)
    assert len(response["top_transactions"]) == 2
    assert response["top_transactions"][0]["amount"] == 2500.0  # Сначала самая крупная трата


def test_main_page_view_invalid_date():
    """Тест обработки ошибки при передаче некорректного формата даты."""
    response_json = main_page_view("неправильная-дата")
    response = json.loads(response_json)
    assert "error" in response
