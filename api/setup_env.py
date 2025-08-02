#!/usr/bin/env python3
"""
Скрипт для настройки переменных окружения для Narrative Engine
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Создает .env файл с настройками"""
    
    # Путь к .env файлу
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        print("Файл .env уже существует!")
        response = input("Хотите перезаписать его? (y/n): ")
        if response.lower() != 'y':
            print("Настройка отменена.")
            return
    
    print("Настройка переменных окружения для Narrative Engine")
    print("=" * 50)
    
    # Запрашиваем API ключ
    print("\n1. Настройка Mistral AI API")
    print("Получите API ключ на https://console.mistral.ai/")
    mistral_key = input("Введите ваш Mistral API ключ: ").strip()
    
    if not mistral_key:
        print("API ключ не введен. Используется значение по умолчанию.")
        mistral_key = "your_mistral_api_key_here"
    
    # Запрашиваем Django секретный ключ
    print("\n2. Настройка Django")
    django_secret = input("Введите Django SECRET_KEY (или нажмите Enter для автогенерации): ").strip()
    
    if not django_secret:
        import secrets
        django_secret = secrets.token_urlsafe(50)
        print(f"Сгенерирован SECRET_KEY: {django_secret[:20]}...")
    
    # Создаем содержимое .env файла
    env_content = f"""# Mistral AI API Configuration
MISTRAL_API_KEY={mistral_key}

# Django Settings
DEBUG=True
SECRET_KEY={django_secret}

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Optional: Model configuration
MISTRAL_MODEL=mistral-large-latest
"""
    
    # Записываем файл
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"\n✅ Файл .env успешно создан: {env_path}")
        print("\nСледующие шаги:")
        print("1. Убедитесь, что у вас есть действующий Mistral API ключ")
        print("2. Запустите сервер: python manage.py runserver")
        print("3. Проверьте работу генерации квестов")
        
    except Exception as e:
        print(f"❌ Ошибка создания файла .env: {e}")

def check_env():
    """Проверяет текущие настройки окружения"""
    print("Проверка текущих настроек окружения")
    print("=" * 40)
    
    # Проверяем .env файл
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        print(f"✅ Файл .env найден: {env_path}")
        
        # Читаем и показываем настройки
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    if 'API_KEY' in line:
                        key, value = line.split('=', 1)
                        if len(value) > 10:
                            masked_value = value[:10] + '...' + value[-4:]
                        else:
                            masked_value = '***'
                        print(f"  {key}={masked_value}")
                    else:
                        print(f"  {line}")
                        
        except Exception as e:
            print(f"❌ Ошибка чтения .env файла: {e}")
    else:
        print("❌ Файл .env не найден")
    
    # Проверяем переменные окружения
    print("\nПеременные окружения:")
    mistral_key = os.getenv('MISTRAL_API_KEY')
    if mistral_key:
        if len(mistral_key) > 10:
            masked_key = mistral_key[:10] + '...' + mistral_key[-4:]
        else:
            masked_key = '***'
        print(f"  MISTRAL_API_KEY={masked_key}")
    else:
        print("  MISTRAL_API_KEY=не установлен")
    
    django_secret = os.getenv('SECRET_KEY')
    if django_secret:
        print(f"  SECRET_KEY={django_secret[:20]}...")
    else:
        print("  SECRET_KEY=не установлен")

def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'check':
            check_env()
        elif command == 'setup':
            create_env_file()
        else:
            print("Использование:")
            print("  python setup_env.py setup  - создать .env файл")
            print("  python setup_env.py check  - проверить настройки")
    else:
        print("Настройка переменных окружения для Narrative Engine")
        print("=" * 50)
        print("1. setup - создать .env файл")
        print("2. check - проверить текущие настройки")
        
        choice = input("\nВыберите действие (1/2): ").strip()
        
        if choice == '1':
            create_env_file()
        elif choice == '2':
            check_env()
        else:
            print("Неверный выбор")

if __name__ == '__main__':
    main() 