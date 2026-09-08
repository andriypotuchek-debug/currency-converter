#!/usr/bin/env python3
"""
Скрипт для швидкої конвертації валют з командного рядка.

Приклади:
  python quick_convert.py 100 USD UAH
  python quick_convert.py 50 EUR GBP
  python quick_convert.py 1 BTC USD --base EUR
"""

import sys
import argparse
from currency_converter import CurrencyConverter


def main():
    parser = argparse.ArgumentParser(
        description="Швидка конвертація валют з командного рядка"
    )
    
    parser.add_argument(
        "amount",
        type=float,
        help="Сума для конвертації"
    )
    
    parser.add_argument(
        "from_currency",
        help="Початкова валюта (код, наприклад USD, EUR, UAH)"
    )
    
    parser.add_argument(
        "to_currency",
        help="Цільова валюта (код, наприклад USD, EUR, UAH)"
    )
    
    parser.add_argument(
        "--base",
        default="USD",
        help="Базова валюта для API (за замовчуванням USD)"
    )
    
    parser.add_argument(
        "--rates",
        action="store_true",
        help="Показати таблицю курсів після конвертації"
    )
    
    args = parser.parse_args()
    
    # Ініціалізуємо конвертер
    converter = CurrencyConverter(base_currency=args.base)
    
    # Завантажуємо курси
    if not converter.fetch_rates():
        print("❌ Помилка: Не вдалося завантажити курси валют")
        return 1
    
    # Виконуємо конвертацію
    result, message = converter.convert(
        args.amount,
        args.from_currency,
        args.to_currency
    )
    
    print(message)
    
    # Показуємо курси, якщо потрібно
    if args.rates:
        converter.display_rates()
    
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
