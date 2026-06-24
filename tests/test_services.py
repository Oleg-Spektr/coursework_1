import json

from src.services import search_by_phone_number, search_transfers_to_individuals, simple_search


def test_simple_search():
    """Тест регистронезависимого простого поиска по подстроке."""
    transactions = [
        {"Описание": "Покупка в Супермаркете", "Категория": "Траты"},
        {"Описание": "Оплата ЖКХ", "Категория": "Коммуналка"},
    ]
    # Ищем "супер" в разном регистре
    result = json.loads(simple_search(transactions, "СУПЕР"))
    assert len(result) == 1
    assert result[0]["Описание"] == "Покупка в Супермаркете"


def test_search_by_phone_number():
    """Тест поиска транзакций с номерами телефонов различных форматов."""
    transactions = [
        {"Описание": "Перевод +7 (999) 123-45-67 на карту"},
        {"Описание": "Оплата по номеру 89991234567"},
        {"Описание": "Обычная покупка без номера"},
    ]
    result = json.loads(search_by_phone_number(transactions))
    assert len(result) == 2
    assert "89991234567" in result[1]["Описание"]


def test_search_transfers_to_individuals():
    """Тест поиска переводов физическим лицам по имени и инициалу."""
    transactions = [
        {"Категория": "Переводы", "Описание": "Валерий А."},
        {"Категория": "Переводы", "Описание": "Перевод на карту мир"},  # Нет имени с инициалом
        {"Категория": "Супермаркеты", "Описание": "Сергей Б."},  # Не та категория
    ]
    result = json.loads(search_transfers_to_individuals(transactions))
    assert len(result) == 1
    assert result[0]["Описание"] == "Валерий А."
