import json
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """Осуществляет поиск по подстроке в полях 'Описание' или 'Категория'.

    Нечувствителен к регистру (согласно критериям оценки).
    Реализовано с использованием filter() и lambda.
    """
    logger.info(f"Запуск простого поиска по запросу: {query}")
    if not query:
        return json.dumps([], ensure_ascii=False)

    query_lower = query.lower()

    # Фильтруем транзакции в функциональном стиле
    filtered_tx = filter(
        lambda tx: (
            (isinstance(tx.get("Описание"), str) and query_lower in tx["Описание"].lower())
            or (isinstance(tx.get("Категория"), str) and query_lower in tx["Категория"].lower())
        ),
        transactions,
    )

    result_list = list(filtered_tx)

    # Приводим даты к строкам для корректной сериализации в JSON
    for tx in result_list:
        if "Дата операции" in tx and not isinstance(tx["Дата операции"], str):
            tx["Дата операции"] = str(tx["Дата операции"])

    return json.dumps(result_list, ensure_ascii=False, indent=4)


def search_by_phone_number(transactions: List[Dict[str, Any]]) -> str:
    """Возвращает JSON со всеми транзакциями, содержащими мобильные номера в описании.

    Соответствует критериям: +7 (900) 000-00-00, 89000000000 и др.
    Реализовано с использованием регулярных выражений (regex) и filter().
    """
    logger.info("Запуск сервиса: Поиск по телефонным номерам")

    # Регулярное выражение, покрывающее форматы слитной записи, скобок, дефисов и пробелов
    phone_pattern = re.compile(r"(?:\+7|7|8)\s*\(?\d{3}\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}")

    filtered_tx = filter(
        lambda tx: isinstance(tx.get("Описание"), str) and bool(phone_pattern.search(tx["Описание"])),
        transactions,
    )

    result_list = list(filtered_tx)
    for tx in result_list:
        if "Дата операции" in tx and not isinstance(tx["Дата операции"], str):
            tx["Дата операции"] = str(tx["Дата операции"])

    return json.dumps(result_list, ensure_ascii=False, indent=4)


def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> str:
    """Возвращает JSON со всеми транзакциями переводов физлицам.

    Критерии: Категория — 'Переводы', в Описании содержится имя и инициал (Валерий А.).
    Реализовано с использованием regex и filter().
    """
    logger.info("Запуск сервиса: Поиск переводов физлицам")

    # Слово с заглавной буквы (Имя), пробел, заглавная буква и точка (Инициал)
    name_initial_pattern = re.compile(r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.")

    filtered_tx = filter(
        lambda tx: (
            tx.get("Категория") == "Переводы"
            and isinstance(tx.get("Описание"), str)
            and bool(name_initial_pattern.search(tx["Описание"]))
        ),
        transactions,
    )

    result_list = list(filtered_tx)
    for tx in result_list:
        if "Дата операции" in tx and not isinstance(tx["Дата операции"], str):
            tx["Дата операции"] = str(tx["Дата операции"])

    return json.dumps(result_list, ensure_ascii=False, indent=4)
