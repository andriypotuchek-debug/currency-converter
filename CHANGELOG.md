# CHANGELOG

## [1.0.0] - 2026-09-08

### Added
- ✅ Основна функціональність конвертера валют
- ✅ Інтеграція з ExchangeRate-API для отримання live-курсів
- ✅ Система кешування з перевіркою часу (1 година)
- ✅ Об'єктно-орієнтований підхід з класом CurrencyConverter
- ✅ Інтерактивне консольне меню
- ✅ Підтримка 150+ валют світу
- ✅ Конвертація між будь-якими валютами через базову
- ✅ Комплексна обробка помилок:
  - Обробка відсутності інтернету
  - Обробка timeout запитів
  - Валідація кодів валют
  - Перевірка коректності вводу
  - Резервна робота з кешем
- ✅ Повний набір модульних тестів (25+ тестів)
- ✅ Утиліта quick_convert.py для швидкої конвертації з командного рядка
- ✅ Приклади використання (examples.py)
- ✅ Документація README.md
- ✅ Конфігурація pytest

### Features

#### CurrencyConverter class
- `__init__(base_currency)` - ініціалізація з базовою валютою
- `fetch_rates(base_currency)` - завантаження курсів з API/кешу
- `convert(amount, from, to)` - конвертація валют
- `display_rates(limit)` - вивід таблиці курсів
- `get_available_currencies()` - список доступних валют
- `_save_cache(rates, base)` - збереження кешу
- `_load_cache()` - завантаження кешу
- `_is_cache_valid(cache_data)` - перевірка актуальності кешу

#### Interactive Menu
1. Конвертувати валюту
2. Переглянути курси
3. Змінити базову валюту
4. Оновити курси з API
5. Список доступних валют

### Testing
- Тест ініціалізації конвертера
- Тест збереження та завантаження кешу
- Тест перевірки актуальності кешу
- Тест конвертації однієї валюти в себе
- Тест конвертації на іншу валюту
- Тест конвертації з не-базової валюти
- Тест конвертації між не-базовими валютами
- Тест обробки невірних кодів валют
- Тест обробки від'ємних сум
- Тест обробки неправильного введення
- Тест отримання списку валют
- Тест успішного завантаження курсів
- Тест обробки помилок з'єднання
- Тест нечутливості до регістру
- Інтеграційні тести кешування

### Documentation
- README.md з повною документацією
- examples.py з прикладами використання
- Docstrings для всіх методів
- Коментарі в коді
- CHANGELOG.md (цей файл)

### File Structure
```
currency-converter/
├── currency_converter.py       # Основна програма (449 рядків)
├── test_currency_converter.py  # Тести (380 рядків)
├── examples.py                 # Приклади (50 рядків)
├── quick_convert.py            # CLI утиліта (65 рядків)
├── requirements.txt            # Залежності
├── pytest.ini                  # Конфігурація pytest
├── README.md                   # Документація
└── CHANGELOG.md               # Цей файл
```

### Error Handling
- `requests.exceptions.ConnectionError` - обробка відсутності інтернету
- `requests.exceptions.Timeout` - обробка timeout
- `requests.exceptions.RequestException` - обробка інших помилок мережі
- `ValueError` - обробка неправильного числа
- `ZeroDivisionError` - обробка нульового курсу
- `json.JSONDecodeError` - обробка невірного JSON
- `IOError` - обробка помилок файлової системи

### API Integration
- URL: https://api.exchangerate-api.com/v4/latest/{base}
- Timeout: 5 секунд
- Cache expiry: 1 година
- Supported currencies: 150+

### Performance
- Кешування для мінімізації запитів до API
- Швидке завантаження з локального файлу
- Ленивий парсинг JSON
- Ефективна обробка помилок

### Future Improvements
- [ ] Web інтерфейс
- [ ] Історія конвертацій
- [ ] Графіки зміни курсів
- [ ] Підтримка cryptocurrency
- [ ] Відправка сповіщень
- [ ] Експорт в CSV/Excel
- [ ] Синхронізація через хмару
- [ ] Мобільний додаток

---

## Версіонування

Проект використовує семантичне версіонування (SemVer):
- **MAJOR** (перша цифра) - несумісні зміни API
- **MINOR** (друга цифра) - нова функціональність, сумісна назад
- **PATCH** (третя цифра) - виправлення помилок

## Як внести вклад

1. Fork репозиторію
2. Створіть гілку для вашої функції (`git checkout -b feature/AmazingFeature`)
3. Commit вашіх змін (`git commit -m 'Add some AmazingFeature'`)
4. Push до гілки (`git push origin feature/AmazingFeature`)
5. Відкрийте Pull Request

## Контакти

- Автор: andriy.potuchek@gmail.com
- GitHub: https://github.com/andriypotuchek-debug/currency-converter
