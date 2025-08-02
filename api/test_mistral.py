#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к Mistral AI API
"""

import os
import sys
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent / 'src'))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quest_project.settings')

import django
django.setup()

from quest_app.llm_generator import QuestGenerator

def test_mistral_connection():
    """Тестирует подключение к Mistral AI"""
    print("Тестирование подключения к Mistral AI")
    print("=" * 40)
    
    # Создаем генератор
    generator = QuestGenerator()
    
    # Проверяем настройку клиента
    if not generator.client:
        print("❌ Mistral AI клиент не настроен")
        print("\nВозможные причины:")
        print("1. API ключ не установлен в .env файле")
        print("2. Неправильный API ключ")
        print("3. Проблемы с подключением к интернету")
        print("\nДля настройки выполните:")
        print("  python setup_env.py setup")
        return False
    
    print("✅ Mistral AI клиент настроен")
    
    # Тестируем простой запрос
    try:
        print("\nОтправляем тестовый запрос...")
        
        from mistralai.models.chat_completion import ChatMessage
        
        messages = [
            ChatMessage(role="user", content="Привет! Ответь одним словом: 'Работает'")
        ]
        
        response = generator.client.chat(
            model="mistral-large-latest",
            messages=messages,
            max_tokens=10,
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        print(f"✅ Получен ответ: '{content}'")
        
        if "работает" in content.lower() or "работает" in content:
            print("✅ API работает корректно!")
            return True
        else:
            print("⚠️ API отвечает, но ответ неожиданный")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        print("\nВозможные причины:")
        print("1. Неправильный API ключ")
        print("2. Проблемы с подключением к интернету")
        print("3. Превышен лимит запросов")
        print("4. Проблемы с сервисом Mistral AI")
        return False

def test_quest_generation():
    """Тестирует генерацию квеста"""
    print("\nТестирование генерации квеста")
    print("=" * 40)
    
    generator = QuestGenerator()
    
    # Тестовые параметры
    test_params = {
        'genre': 'фэнтези',
        'hero': 'маг',
        'goal': 'найти древний артефакт',
        'scene_count': 5,
        'max_depth': 3,
        'complexity': 'simple',
        'ending_type': 'single'
    }
    
    print(f"Параметры теста:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    
    try:
        print("\nГенерируем квест...")
        quest_data = generator.generate_quest(**test_params)
        
        if 'error' in quest_data:
            print(f"❌ Ошибка генерации: {quest_data['error']}")
            return False
        
        if 'warning' in quest_data:
            print(f"⚠️ Предупреждение: {quest_data['warning']}")
        
        # Проверяем структуру квеста
        scenes = quest_data.get('scenes', [])
        print(f"✅ Квест сгенерирован успешно!")
        print(f"  Количество сцен: {len(scenes)}")
        
        if scenes:
            first_scene = scenes[0]
            print(f"  Первая сцена: {first_scene.get('scene_id', 'N/A')}")
            print(f"  Текст (первые 50 символов): {first_scene.get('text', '')[:50]}...")
            print(f"  Количество выборов: {len(first_scene.get('choices', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при генерации квеста: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print("Тестирование Narrative Engine")
    print("=" * 50)
    
    # Тестируем подключение
    connection_ok = test_mistral_connection()
    
    if connection_ok:
        # Тестируем генерацию
        generation_ok = test_quest_generation()
        
        if generation_ok:
            print("\n🎉 Все тесты пройдены успешно!")
            print("Система готова к работе.")
        else:
            print("\n⚠️ Есть проблемы с генерацией квестов")
            print("Проверьте логи для получения дополнительной информации.")
    else:
        print("\n❌ Проблемы с подключением к API")
        print("Настройте API ключ и повторите тест.")

if __name__ == '__main__':
    main() 