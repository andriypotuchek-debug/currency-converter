# Приклад використання конвертера валют у коді

from currency_converter import CurrencyConverter

# Приклад 1: Базова конвертація
print("=== Приклад 1: Базова конвертація ===")
converter = CurrencyConverter(base_currency="USD")

# Завантажуємо курси
if converter.fetch_rates():
    # Конвертуємо 100 USD у UAH
    result, message = converter.convert(100, "USD", "UAH")
    print(message)
    
    # Конвертуємо 50 EUR у GBP
    result, message = converter.convert(50, "EUR", "GBP")
    print(message)

# Приклад 2: Зміна базової валюти
print("\n=== Приклад 2: Зміна базової валюти ===")
if converter.fetch_rates("EUR"):
    result, message = converter.convert(100, "EUR", "USD")
    print(message)

# Приклад 3: Переглядання курсів
print("\n=== Приклад 3: Переглядання курсів ===")
converter.display_rates(limit=5)

# Приклад 4: Отримання списку валют
print("\n=== Приклад 4: Список доступних валют ===")
currencies = converter.get_available_currencies()
print(f"Кількість доступних валют: {len(currencies)}")
print(f"Перші 10 валют: {', '.join(currencies[:10])}")

# Приклад 5: Обробка помилок
print("\n=== Приклад 5: Обробка помилок ===")
result, message = converter.convert(100, "XYZ", "USD")
print(message)

result, message = converter.convert(-50, "USD", "EUR")
print(message)

result, message = converter.convert("abc", "USD", "EUR")
print(message)
