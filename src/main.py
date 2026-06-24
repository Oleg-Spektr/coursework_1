import logging
from src.utils import load_transactions
from src.views import main_page_view
from src.services import simple_search, search_by_phone_number, search_transfers_to_individuals
from src.reports import spending_by_category, spending_by_weekday

# Настраиваем базовое логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    print("=== ЗАПУСК АНАЛИЗА РЕАЛЬНЫХ ДАННЫХ ИЗ EXCEL ===")

    # 1. Загружаем ваш настоящий файл из папки data
    df = load_transactions()
    print(f"Успешно загружено транзакций из исходного файла: {len(df)}")

    # Константы для тестов на реальных данных
    target_date = "2020-05-20"
    target_date_time = "2020-05-20 14:30:00"
    target_category = "Супермаркеты"

    print("\n=== ЧАСТЬ 1: ВЕБ-СТРАНИЦЫ ===")
    print(f"Генерация JSON для страницы 'Главная' на дату: {target_date_time}")
    main_json = main_page_view(target_date_time)
    print(main_json)

    print("\n=== ЧАСТЬ 2: СЕРВИСЫ (Функциональное программирование) ===")
    # Преобразуем DataFrame в список словарей, как требуют интерфейсы сервисов
    transactions_list = df.to_dict(orient="records")

    # 2.1 Простой поиск
    print(f"Простой поиск по подстроке '{target_category}':")
    search_res = simple_search(transactions_list, target_category)
    # Выведем только количество найденных, чтобы не засорять консоль
    print(f"Найдено транзакций: {len(search_res.split('}')) - 1}")

    # 2.2 Поиск по телефонным номерам
    print("\nПоиск транзакций, содержащих телефонные номера в описании:")
    phone_res = search_by_phone_number(transactions_list)
    print(f"Найдено транзакций: {len(phone_res.split('}')) - 1}")

    # 2.3 Поиск переводов физлицам
    print("\nПоиск переводов физическим лицам (Имя И.):")
    transfers_res = search_transfers_to_individuals(transactions_list)
    print(f"Найдено транзакций: {len(transfers_res.split('}')) - 1}")

    print("\n=== ЧАСТЬ 3: ОТЧЕТЫ (Excel) ===")
    print(f"Генерация отчетов относительно даты: {target_date}")

    # Вызываем отчеты на реальном DataFrame.
    # Декоратор перезапишет файлы в папке reports/ настоящими данными!
    spending_by_category(df, category=target_category, date=target_date)
    spending_by_weekday(df, date=target_date)

    print("\n[Успех] Реальные отчёты обновлены и сохранены в папке 'reports/'!")


if __name__ == "__main__":
    main()
