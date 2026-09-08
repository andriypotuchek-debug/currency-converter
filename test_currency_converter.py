"""
Модульні тести для конвертера валют.
Тестує основний функціонал без залежності від інтернету.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import datetime, timedelta
import sys

# Імпортуємо основну програму
from currency_converter import CurrencyConverter


class TestCurrencyConverter(unittest.TestCase):
    """Тести для класу CurrencyConverter."""
    
    def setUp(self):
        """Підготовка до кожного тесту."""
        self.converter = CurrencyConverter(base_currency="USD")
        # Мок-дані для тестування
        self.mock_rates = {
            "EUR": 0.92,
            "GBP": 0.79,
            "UAH": 36.50,
            "JPY": 110.5,
            "CAD": 1.35
        }
    
    def tearDown(self):
        """Очищення після кожного тесту."""
        # Видаляємо тестовий кеш-файл
        if os.path.exists("rates_cache.json"):
            os.remove("rates_cache.json")
    
    def test_converter_initialization(self):
        """Тест ініціалізації конвертера."""
        self.assertEqual(self.converter.base_currency, "USD")
        self.assertEqual(self.converter.rates, {})
    
    def test_save_cache(self):
        """Тест збереження кешу."""
        self.converter._save_cache(self.mock_rates, "USD")
        self.assertTrue(os.path.exists("rates_cache.json"))
        
        with open("rates_cache.json", 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(cache_data["base"], "USD")
        self.assertEqual(cache_data["rates"], self.mock_rates)
        self.assertIn("timestamp", cache_data)
    
    def test_load_cache(self):
        """Тест завантаження кешу."""
        # Спочатку зберігаємо дані
        self.converter._save_cache(self.mock_rates, "USD")
        
        # Тепер завантажуємо
        cache_data = self.converter._load_cache()
        self.assertIsNotNone(cache_data)
        self.assertEqual(cache_data["base"], "USD")
        self.assertEqual(cache_data["rates"], self.mock_rates)
    
    def test_is_cache_valid(self):
        """Тест перевірки актуальності кешу."""
        # Кеш менше 1 години - актуальний
        current_time = datetime.now()
        cache_data = {
            "timestamp": current_time.isoformat(),
            "base": "USD",
            "rates": self.mock_rates
        }
        self.assertTrue(self.converter._is_cache_valid(cache_data))
        
        # Кеш більше 1 години - застарів
        old_time = (current_time - timedelta(hours=2)).isoformat()
        old_cache = {
            "timestamp": old_time,
            "base": "USD",
            "rates": self.mock_rates
        }
        self.assertFalse(self.converter._is_cache_valid(old_cache))
    
    def test_convert_same_currency(self):
        """Тест конвертації однієї валюти в себе."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert(100, "USD", "USD")
        self.assertEqual(result, 100)
        self.assertIn("100 USD = 100 USD", message)
    
    def test_convert_to_other_currency(self):
        """Тест конвертації на іншу валюту."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert(100, "USD", "EUR")
        expected = 100 * 0.92
        self.assertAlmostEqual(result, expected, places=2)
    
    def test_convert_from_non_base_currency(self):
        """Тест конвертації з не-базової валюти."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert(92, "EUR", "USD")
        expected = 92 / 0.92  # 100
        self.assertAlmostEqual(result, expected, places=2)
    
    def test_convert_between_non_base_currencies(self):
        """Тест конвертації між двома не-базовими валютами."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert(92, "EUR", "UAH")
        # EUR -> USD -> UAH
        to_usd = 92 / 0.92  # 100
        to_uah = to_usd * 36.50  # 3650
        self.assertAlmostEqual(result, to_uah, places=1)
    
    def test_convert_invalid_currency(self):
        """Тест конвертації з невірним кодом валюти."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert(100, "XYZ", "USD")
        self.assertIsNone(result)
        self.assertIn("не знайдена", message)
    
    def test_convert_negative_amount(self):
        """Тест конвертації від'ємної суми."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert(-100, "USD", "EUR")
        self.assertIsNone(result)
        self.assertIn("не може бути від'ємною", message)
    
    def test_convert_invalid_amount(self):
        """Тест конвертації з неправильною сумою."""
        self.converter.rates = self.mock_rates
        result, message = self.converter.convert("abc", "USD", "EUR")
        self.assertIsNone(result)
        self.assertIn("не число", message)
    
    def test_get_available_currencies(self):
        """Тест отримання списку доступних валют."""
        self.converter.rates = self.mock_rates
        currencies = self.converter.get_available_currencies()
        self.assertEqual(currencies[0], "USD")
        self.assertIn("EUR", currencies)
        self.assertEqual(len(currencies), 6)  # USD + 5 інших
    
    @patch('requests.get')
    def test_fetch_rates_success(self, mock_get):
        """Тест успішного завантаження курсів з API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "rates": self.mock_rates
        }
        mock_get.return_value = mock_response
        
        result = self.converter.fetch_rates("USD")
        self.assertTrue(result)
        self.assertEqual(self.converter.rates, self.mock_rates)
    
    @patch('requests.get')
    def test_fetch_rates_connection_error(self, mock_get):
        """Тест обробки помилки з'єднання."""
        mock_get.side_effect = Exception("Connection error")
        
        # Спочатку зберігаємо кеш
        self.converter._save_cache(self.mock_rates, "USD")
        
        # Тепер робимо запит без з'єднання
        result = self.converter.fetch_rates("USD")
        # Повинен повернути True, тому що використав кеш
        self.assertTrue(result)
        self.assertEqual(self.converter.rates, self.mock_rates)
    
    def test_case_insensitive_currencies(self):
        """Тест нечутливості до регістру кодів валют."""
        self.converter.rates = self.mock_rates
        result1, _ = self.converter.convert(100, "usd", "eur")
        result2, _ = self.converter.convert(100, "USD", "EUR")
        result3, _ = self.converter.convert(100, "UsD", "EuR")
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)


class TestCacheIntegration(unittest.TestCase):
    """Інтеграційні тести для кешування."""
    
    def setUp(self):
        """Підготовка до кожного тесту."""
        self.converter = CurrencyConverter()
    
    def tearDown(self):
        """Очищення після кожного тесту."""
        if os.path.exists("rates_cache.json"):
            os.remove("rates_cache.json")
    
    def test_cache_workflow(self):
        """Тест повного циклу роботи з кешем."""
        mock_rates = {"EUR": 0.92, "UAH": 36.50}
        
        # 1. Зберігаємо дані
        self.converter._save_cache(mock_rates, "USD")
        self.assertTrue(os.path.exists("rates_cache.json"))
        
        # 2. Завантажуємо дані
        cache_data = self.converter._load_cache()
        self.assertIsNotNone(cache_data)
        
        # 3. Перевіряємо актуальність
        is_valid = self.converter._is_cache_valid(cache_data)
        self.assertTrue(is_valid)
        
        # 4. Використовуємо дані
        self.converter.rates = cache_data["rates"]
        result, _ = self.converter.convert(100, "USD", "EUR")
        self.assertEqual(result, 92)


def run_tests():
    """Запуск всіх тестів."""
    # Створюємо набір тестів
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Додаємо тести
    suite.addTests(loader.loadTestsFromTestCase(TestCurrencyConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheIntegration))
    
    # Запускаємо з детальним виводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Повертаємо код виходу
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
