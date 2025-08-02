#!/usr/bin/env python3
"""
Тест валидации квестов
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from quest_app.llm_generator import QuestGenerator

def test_valid_quest():
    """Тест валидного квеста"""
    generator = QuestGenerator()
    
    valid_quest = {
        "scenes": [
            {
                "scene_id": "start",
                "text": "Начальная сцена",
                "choices": [
                    {"text": "Путь 1", "next_scene": "path1"},
                    {"text": "Путь 2", "next_scene": "path2"}
                ]
            },
            {
                "scene_id": "path1",
                "text": "Путь 1",
                "choices": [
                    {"text": "Конец", "next_scene": "quest_end"}
                ]
            },
            {
                "scene_id": "path2",
                "text": "Путь 2",
                "choices": [
                    {"text": "Конец", "next_scene": "quest_end"}
                ]
            },
            {
                "scene_id": "quest_end",
                "text": "Квест завершен",
                "choices": [
                    {"text": "Завершить игру", "next_scene": "quest_end"}
                ]
            }
        ]
    }
    
    is_valid, message = generator.validate_quest(valid_quest)
    print(f"Валидный квест: {is_valid}, сообщение: {message}")
    assert is_valid, f"Валидный квест должен проходить проверку: {message}"

def test_invalid_quest_missing_quest_end():
    """Тест квеста без quest_end"""
    generator = QuestGenerator()
    
    invalid_quest = {
        "scenes": [
            {
                "scene_id": "start",
                "text": "Начальная сцена",
                "choices": [
                    {"text": "Путь 1", "next_scene": "path1"},
                    {"text": "Путь 2", "next_scene": "path2"}
                ]
            },
            {
                "scene_id": "path1",
                "text": "Путь 1",
                "choices": [
                    {"text": "Конец", "next_scene": "end"}
                ]
            },
            {
                "scene_id": "path2",
                "text": "Путь 2",
                "choices": [
                    {"text": "Конец", "next_scene": "end"}
                ]
            },
            {
                "scene_id": "end",
                "text": "Конец",
                "choices": [
                    {"text": "Завершить", "next_scene": "end"}
                ]
            }
        ]
    }
    
    is_valid, message = generator.validate_quest(invalid_quest)
    print(f"Квест без quest_end: {is_valid}, сообщение: {message}")
    assert not is_valid, "Квест без quest_end должен не проходить проверку"

def test_invalid_quest_dead_end():
    """Тест квеста с тупиковой веткой"""
    generator = QuestGenerator()
    
    invalid_quest = {
        "scenes": [
            {
                "scene_id": "start",
                "text": "Начальная сцена",
                "choices": [
                    {"text": "Путь 1", "next_scene": "path1"},
                    {"text": "Путь 2", "next_scene": "path2"}
                ]
            },
            {
                "scene_id": "path1",
                "text": "Путь 1",
                "choices": [
                    {"text": "Конец", "next_scene": "quest_end"}
                ]
            },
            {
                "scene_id": "path2",
                "text": "Путь 2",
                "choices": [
                    {"text": "Тупик", "next_scene": "dead_end"}
                ]
            },
            {
                "scene_id": "dead_end",
                "text": "Тупик",
                "choices": [
                    {"text": "Никуда", "next_scene": "dead_end"}
                ]
            },
            {
                "scene_id": "quest_end",
                "text": "Квест завершен",
                "choices": [
                    {"text": "Завершить игру", "next_scene": "quest_end"}
                ]
            }
        ]
    }
    
    is_valid, message = generator.validate_quest(invalid_quest)
    print(f"Квест с тупиком: {is_valid}, сообщение: {message}")
    assert not is_valid, "Квест с тупиковой веткой должен не проходить проверку"

def test_valid_quest_end_single_choice():
    """Тест валидного квеста с одним выбором в quest_end"""
    generator = QuestGenerator()
    
    valid_quest = {
        "scenes": [
            {
                "scene_id": "start",
                "text": "Начальная сцена",
                "choices": [
                    {"text": "Путь 1", "next_scene": "quest_end"}
                ]
            },
            {
                "scene_id": "quest_end",
                "text": "Квест завершен",
                "choices": [
                    {"text": "Завершить игру", "next_scene": "quest_end"}
                ]
            }
        ]
    }
    
    is_valid, message = generator.validate_quest(valid_quest)
    print(f"Квест с одним выбором в quest_end: {is_valid}, сообщение: {message}")
    assert is_valid, f"Квест с одним выбором в quest_end должен проходить проверку: {message}"

if __name__ == "__main__":
    print("Запуск тестов валидации...")
    
    try:
        test_valid_quest()
        print("✓ Тест валидного квеста прошел")
    except Exception as e:
        print(f"✗ Тест валидного квеста провалился: {e}")
    
    try:
        test_invalid_quest_missing_quest_end()
        print("✓ Тест квеста без quest_end прошел")
    except Exception as e:
        print(f"✗ Тест квеста без quest_end провалился: {e}")
    
    try:
        test_invalid_quest_dead_end()
        print("✓ Тест квеста с тупиком прошел")
    except Exception as e:
        print(f"✗ Тест квеста с тупиком провалился: {e}")
    
    try:
        test_valid_quest_end_single_choice()
        print("✓ Тест квеста с одним выбором в quest_end прошел")
    except Exception as e:
        print(f"✗ Тест квеста с одним выбором в quest_end провалился: {e}")
    
    print("Тесты завершены!") 