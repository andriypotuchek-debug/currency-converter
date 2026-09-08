import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import requests

# Constants
CACHE_FILE = "rates_cache.json"
CACHE_EXPIRY_HOURS = 1
API_URL = "https://api.exchangerate-api.com/v4/latest"


class CurrencyConverter:
    """
    Консольний конвертер валют із кешуванням та live-курсами.
    
    Функціонал:
    - Отримання актуальних курсів валют з API
    - Локальне кешування з перевіркою часу
    - Конвертація валют
    - Обробка помилок та винятків
    """
    
    def __init__(self, base_currency: str = "USD"):
        """
        Ініціалізація конвертера.
        
        Args:
            base_currency: Базова валюта для отримання курсів (за замовчуванням USD)
        """
        self.base_currency = base_currency.upper()
        self.rates = {}
        self.last_update = None
    
    def _load_cache(self) -> Optional[Dict]:
        """
        Завантажує кешовані курси з локального файлу.
        
        Returns:
            Словник з кешованими курсами або None, якщо файл не існує
        """
        if not os.path.exists(CACHE_FILE):
            return None
        
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return cache_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Помилка при завантаженні кешу: {e}")
            return None
    
    def _save_cache(self, rates: Dict, base: str) -> None:
        """
        Зберігає курси у локальний файл з позначкою часу.
        
        Args:
            rates: Словник курсів валют
            base: Базова валюта
        """
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "base": base,
            "rates": rates
        }
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Кеш оновлено: {datetime.now().strftime('%H:%M:%S')}")
        except IOError as e:
            print(f"⚠️  Помилка при збереженні кешу: {e}")
    
    def _is_cache_valid(self, cache_data: Dict) -> bool:
        """
        Перевіряє, чи є кеш ще актуальним (менше 1 години).
        
        Args:
            cache_data: Дані з кешу
            
        Returns:
            True, якщо кеш актуальний, False - якщо потрібне оновлення
        """
        if cache_data is None:
            return False
        
        try:
            timestamp_str = cache_data.get("timestamp")
            if not timestamp_str:
                return False
            
            cache_time = datetime.fromisoformat(timestamp_str)
            current_time = datetime.now()
            time_diff = current_time - cache_time
            
            is_valid = time_diff < timedelta(hours=CACHE_EXPIRY_HOURS)
            
            if is_valid:
                print(f"📦 Використовується кеш від {cache_time.strftime('%H:%M:%S')}")
            else:
                print(f"⏰ Кеш застарів ({time_diff.seconds // 60} хв назад). Оновлюємо...")
            
            return is_valid
        except (ValueError, TypeError) as e:
            print(f"⚠️  Помилка при перевірці часу кешу: {e}")
            return False
    
    def fetch_rates(self, base_currency: str = None) -> bool:
        """
        Отримує курси валют з API або з кешу.
        
        Args:
            base_currency: Валюта, відносно якої отримувати курси
            
        Returns:
            True, якщо курси успішно отримані, False - якщо помилка
        """
        if base_currency:
            self.base_currency = base_currency.upper()
        
        # Спробуємо завантажити з кешу
        cache_data = self._load_cache()
        
        if cache_data and cache_data.get("base") == self.base_currency and self._is_cache_valid(cache_data):
            self.rates = cache_data.get("rates", {})
            self.last_update = cache_data.get("timestamp")
            return True
        
        # Якщо кеш не валідний, робимо запит до API
        try:
            print(f"🔄 Завантажуємо курси для {self.base_currency}...")
            response = requests.get(
                f"{API_URL}/{self.base_currency}",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            self.rates = data.get("rates", {})
            self.last_update = datetime.now().isoformat()
            
            # Зберігаємо у кеш
            self._save_cache(self.rates, self.base_currency)
            print(f"✅ Курси оновлено успішно!")
            return True
            
        except requests.exceptions.ConnectionError:
            print("❌ Помилка: Немає з'єднання з інтернетом!")
            print("   Спробую використати останні збережені дані...")
            
            # Спробуємо завантажити будь-які дані з кешу
            if cache_data:
                self.rates = cache_data.get("rates", {})
                self.last_update = cache_data.get("timestamp")
                print(f"   Використовуюю дані з кешу від {self.last_update}")
                return True
            else:
                print("   У кешу немає збережених даних!")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Помилка: Час очікування запиту вийшов!")
            
            if cache_data:
                self.rates = cache_data.get("rates", {})
                self.last_update = cache_data.get("timestamp")
                print(f"   Використовуюю дані з кешу від {self.last_update}")
                return True
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Помилка при запиті до API: {e}")
            
            if cache_data:
                self.rates = cache_data.get("rates", {})
                self.last_update = cache_data.get("timestamp")
                print(f"   Використовуюю дані з кешу від {self.last_update}")
                return True
            return False
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[Tuple[float, str]]:
        """
        Конвертує суму з однієї валюти в іншу.
        
        Args:
            amount: Сума для конвертації
            from_currency: Початкова валюта
            to_currency: Цільова валюта
            
        Returns:
            Кортеж (результат, повідомлення) або None, якщо помилка
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Перевіряємо, чи валюти існують
        if from_currency not in self.rates and from_currency != self.base_currency:
            return None, f"❌ Валюта '{from_currency}' не знайдена!"
        
        if to_currency not in self.rates and to_currency != self.base_currency:
            return None, f"❌ Валюта '{to_currency}' не знайдена!"
        
        try:
            amount = float(amount)
            if amount < 0:
                return None, "❌ Сума не може бути від'ємною!"
            
            # Якщо обидві валюти - це базова валюта
            if from_currency == self.base_currency and to_currency == self.base_currency:
                return amount, f"✅ {amount} {from_currency} = {amount} {to_currency}"
            
            # Якщо початкова валюта - базова
            if from_currency == self.base_currency:
                result = amount * self.rates[to_currency]
                return result, f"✅ {amount} {from_currency} = {result:.2f} {to_currency}"
            
            # Якщо цільова валюта - базова
            if to_currency == self.base_currency:
                result = amount / self.rates[from_currency]
                return result, f"✅ {amount} {from_currency} = {result:.2f} {to_currency}"
            
            # Обидві валюти не базові - конвертуємо через базову
            to_base = amount / self.rates[from_currency]
            result = to_base * self.rates[to_currency]
            return result, f"✅ {amount} {from_currency} = {result:.2f} {to_currency}"
            
        except ValueError:
            return None, f"❌ Неправильна сума: '{amount}' не число!"
        except ZeroDivisionError:
            return None, "❌ Помилка: Курс рівний нулю!"
    
    def get_available_currencies(self) -> list:
        """
        Повертає список доступних валют.
        
        Returns:
            Список кодів валют
        """
        currencies = [self.base_currency] + sorted(list(self.rates.keys()))
        return currencies
    
    def display_rates(self, limit: int = 10) -> None:
        """
        Виводить таблицю курсів валют.
        
        Args:
            limit: Кількість валют для відображення
        """
        print(f"\n📊 Курси валют відносно {self.base_currency}:")
        print("-" * 50)
        print(f"{'Валюта':<10} {'Курс':<15} {'На 100':<15}")
        print("-" * 50)
        
        # Базова валюта
        print(f"{self.base_currency:<10} {'1.0000':<15} {'100.00':<15}")
        
        # Інші валюти (перші 'limit' штук)
        for i, (currency, rate) in enumerate(sorted(self.rates.items())[:limit]):
            print(f"{currency:<10} {rate:<15.4f} {rate * 100:<15.2f}")
        
        if len(self.rates) > limit:
            print(f"... та ще {len(self.rates) - limit} валют")
        print()


def display_menu():
    """Виводить меню програми."""
    print("\n" + "="*50)
    print("💱 КОНСОЛЬНИЙ КОНВЕРТЕР ВАЛЮТ")
    print("="*50)
    print("1. Конвертувати валюту")
    print("2. Переглянути курси")
    print("3. Змінити базову валюту")
    print("4. Оновити курси з API")
    print("5. Список доступних валют")
    print("0. Вихід")
    print("="*50)


def main():
    """Основна функція програми."""
    converter = CurrencyConverter(base_currency="USD")
    
    # Завантажуємо курси при запуску
    if not converter.fetch_rates():
        print("⚠️  Програма не змогла завантажити курси. Спробуйте пізніше.")
        return
    
    while True:
        display_menu()
        choice = input("Виберіть операцію: ").strip()
        
        if choice == "1":
            print("\n--- Конвертація валюти ---")
            try:
                amount = input("Введіть суму: ").strip()
                from_curr = input(f"З якої валюти конвертувати? (базова: {converter.base_currency}): ").strip()
                to_curr = input("У яку валюту конвертувати?: ").strip()
                
                if not from_curr:
                    from_curr = converter.base_currency
                
                result, message = converter.convert(amount, from_curr, to_curr)
                print(message)
            except KeyboardInterrupt:
                print("\n⚠️  Операція скасована.")
            except Exception as e:
                print(f"❌ Помилка: {e}")
        
        elif choice == "2":
            converter.display_rates()
        
        elif choice == "3":
            print("\n--- Зміна базової валюти ---")
            new_base = input("Введіть код валюти (наприклад, USD, EUR, UAH): ").strip().upper()
            if converter.fetch_rates(new_base):
                print(f"✅ Базова валюта змінена на {new_base}")
            else:
                print(f"❌ Не вдалося завантажити курси для {new_base}")
        
        elif choice == "4":
            converter.fetch_rates()
        
        elif choice == "5":
            currencies = converter.get_available_currencies()
            print(f"\n📋 Доступні валюти ({len(currencies)} штук):")
            print(", ".join(currencies))
        
        elif choice == "0":
            print("\n👋 До побачення!")
            break
        
        else:
            print("❌ Невідома операція. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
