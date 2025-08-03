"""
LangChain-based Quest Generator
Улучшенный генератор квестов с использованием LangChain для лучшего планирования и памяти
"""
import json
import os
from typing import Dict, List, Optional, Any
from django.conf import settings

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.messages import HumanMessage, SystemMessage
    from pydantic import BaseModel, Field
    
    # Попробуем разные варианты импорта Mistral для LangChain
    ChatMistralAI = None
    try:
        from langchain_mistralai import ChatMistralAI
    except ImportError:
        try:
            from langchain.llms import Mistral as ChatMistralAI
        except ImportError:
            pass  # ChatMistralAI остается None
    
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"Warning: LangChain not available: {e}. Using fallback generator.")


class QuestScene(BaseModel):
    """Модель сцены квеста"""
    scene_id: str = Field(description="Уникальный ID сцены в snake_case формате")
    text: str = Field(description="Описание сцены на русском языке, минимум 10 символов")
    choices: List[Dict[str, str]] = Field(description="Список выборов игрока")


class Quest(BaseModel):
    """Модель квеста"""
    scenes: List[QuestScene] = Field(description="Список всех сцен квеста")


class LangChainQuestGenerator:
    """Генератор квестов с использованием LangChain"""
    
    def __init__(self):
        self.llm = None
        self.quest_planner = None
        self.quest_creator = None
        self.quest_validator = None
        self.setup_langchain()
    
    def setup_langchain(self):
        """Настройка LangChain компонентов"""
        if not LANGCHAIN_AVAILABLE:
            print("LangChain недоступен")
            return
        
        api_key = settings.MISTRAL_API_KEY
        if not api_key or api_key == "your_mistral_api_key_here":
            print("Mistral API ключ не настроен для LangChain")
            return
        
        try:
            # Инициализация LLM
            if ChatMistralAI is None:
                print("ChatMistralAI недоступен, LangChain генератор отключен")
                return
                
            self.llm = ChatMistralAI(
                model=settings.MISTRAL_MODEL,
                api_key=api_key,
                temperature=0.7,
                max_tokens=100000
            )
            
            # Создание цепочек
            self._create_planning_chain()
            self._create_generation_chain()
            self._create_validation_chain()
            
            print("LangChain Quest Generator настроен успешно")
            
        except Exception as e:
            print(f"Ошибка настройки LangChain: {e}")
    
    def _create_planning_chain(self):
        """Создание цепочки планирования квеста"""
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """План квеста для хакатона. Требования: 5-10 сцен, минимум 1 развилка, 1 ветвь глубиной 3+ сцены, БЕЗ ЦИКЛОВ.

Параметры: жанр {genre}, герой {hero}, цель {goal}. Создай РОВНО {scene_count} сцен.

ВАЖНО - ID сцен должны отражать СОДЕРЖАНИЕ:
- Места: "dark_forest", "ancient_temple", "boss_chamber", "hidden_cave"
- Действия: "search_clues", "battle_guards", "solve_riddle", "escape_trap"
- Состояния: "wounded_hero", "found_key", "magic_awakened"

Создай развилки в ЛОГИЧНЫХ местах:
- После исследования (выбор пути)
- Перед опасностью (атака/обход)
- При находке (использовать/оставить)

Формат:
{{
  "scene_ids": ["start", "meaningful_name1", "meaningful_name2", "deep_location", "quest_end"],
  "connections": {{
    "start": ["meaningful_name1", "meaningful_name2"],
    "meaningful_name1": ["deep_location"],
    "meaningful_name2": ["quest_end"],
    "deep_location": ["quest_end"],
    "quest_end": ["quest_end"]
  }},
  "validation": {{
    "has_quest_end": true,
    "no_cycles": true,
    "scene_count_correct": true
  }}
}}"""),
            ("human", "Создай план квеста.")
        ])
        
        self.quest_planner = planning_prompt | self.llm | JsonOutputParser()
    
    def _create_generation_chain(self):
        """Создание цепочки генерации квеста"""
        generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """Создай квест для хакатона по плану. БЕЗ ЦИКЛОВ! Используй ТОЛЬКО scene_id из плана.

План: {plan}
Жанр: {genre}, Герой: {hero}, Цель: {goal}

Правила:
- Каждая сцена (кроме quest_end) имеет 2+ РАЗНЫХ выбора
- Используй ТОЛЬКО scene_id из плана в next_scene
- Все пути ведут к quest_end
- НЕ создавай циклы

ВАЖНО - разнообразные типы выборов:
- Действие vs. Осторожность: "Атаковать" vs. "Обойти стороной"
- Риск vs. Безопасность: "Рискнуть прыгнуть" vs. "Найти другой путь"
- Помощь vs. Одиночество: "Попросить помощи" vs. "Справиться самому"
- Исследование vs. Движение: "Изучить артефакт" vs. "Идти дальше"
- Честность vs. Хитрость: "Сказать правду" vs. "Солгать"

Каждый выбор должен ЛОГИЧНО соответствовать содержанию сцены!

JSON формат:
{{
  "scenes": [
    {{
      "scene_id": "start",
      "text": "Описание ситуации на русском (минимум 50 слов)",
      "choices": [
        {{"text": "Активный выбор (действие)", "next_scene": "scene_из_плана"}},
        {{"text": "Альтернативный выбор (другой подход)", "next_scene": "другая_scene_из_плана"}}
      ]
    }}
  ]
}}"""),
            ("human", "Создай квест.")
        ])
        
        self.quest_creator = generation_prompt | self.llm | JsonOutputParser()
    
    def _create_validation_chain(self):
        """Создание цепочки валидации квеста"""
        validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """Проверь квест. Отвечай JSON.

Правила проверки:
1. Каждая сцена (кроме quest_end) имеет МИНИМУМ 2 выбора
2. Все next_scene существуют в списке сцен
3. Есть сцена quest_end
4. ВАЖНО: Если сцена имеет 2+ выбора - это ВАЛИДНО, даже если они ведут к одной сцене!

Пример ВАЛИДНОЙ сцены:
{{
  "scene_id": "final_battle",
  "choices": [
    {{"text": "Атаковать мечом", "next_scene": "quest_end"}},
    {{"text": "Использовать магию", "next_scene": "quest_end"}}
  ]
}}

НЕ считай это ошибкой! Количество выборов = 2, это соответствует требованиям.

Квест: {quest}

Формат ответа:
{{
  "valid": true/false,
  "errors": ["описание ошибки если есть"]
}}"""),
            ("human", "Проверь квест.")
        ])
        
        self.quest_validator = validation_prompt | self.llm | JsonOutputParser()
    
    def generate_quest(self, genre: str, hero: str, goal: str, 
                      scene_count: int = 10, max_depth: int = 5, 
                      complexity: str = "medium", ending_type: str = "single") -> Dict:
        """Генерация квеста с использованием LangChain"""
        
        if not self.llm:
            return {"error": "LangChain не настроен. Проверьте настройки."}
        
        try:
            print("🧠 Этап 1: Планирование структуры квеста...")
            
            # Этап 1: Планирование
            plan_params = {
                "genre": genre,
                "hero": hero,
                "goal": goal,
                "scene_count": scene_count,
                "max_depth": max_depth,
                "complexity": complexity
            }
            
            plan = self.quest_planner.invoke(plan_params)
            print(f"📋 План создан: {len(plan.get('scene_ids', []))} сцен")
            
            # Проверка плана
            if not plan.get('validation', {}).get('has_quest_end', False):
                return {"error": "План не содержит сцену quest_end"}
            
            if not plan.get('validation', {}).get('no_cycles', False):
                return {"error": "План содержит циклы"}
            
            # Проверяем количество сцен в плане
            scene_ids = plan.get('scene_ids', [])
            if len(scene_ids) != scene_count:
                return {"error": f"План содержит {len(scene_ids)} сцен, а нужно {scene_count}"}
            
            print("🎮 Этап 2: Создание содержимого квеста...")
            
            # Этап 2: Генерация квеста по плану
            generation_params = {
                "plan": json.dumps(plan, ensure_ascii=False),
                "genre": genre,
                "hero": hero,
                "goal": goal,
                "complexity": complexity
            }
            
            quest = self.quest_creator.invoke(generation_params)
            print(f"✍️ Квест создан: {len(quest.get('scenes', []))} сцен")
            
            print("🔍 Этап 3: Валидация квеста...")
            
            # Этап 3: Валидация
            validation_params = {
                "quest": json.dumps(quest, ensure_ascii=False)
            }
            
            validation = self.quest_validator.invoke(validation_params)
            
            if not validation.get('valid', False):
                errors = validation.get('errors', [])
                print(f"❌ Квест не прошел валидацию: {errors}")
                return {"error": f"Квест не прошел валидацию: {', '.join(errors)}"}
            
            # Дополнительная проверка quest_end
            quest_scenes = quest.get('scenes', [])
            quest_end_scene = None
            for scene in quest_scenes:
                if scene.get('scene_id') == 'quest_end':
                    quest_end_scene = scene
                    break
            
            if quest_end_scene:
                choices = quest_end_scene.get('choices', [])
                if not choices:
                    # Исправляем quest_end если у него нет выборов
                    quest_end_scene['choices'] = [{"text": "Завершить квест", "next_scene": "quest_end"}]
                    print("🔧 Исправлена сцена quest_end - добавлен выбор")
            
            print("✅ Квест успешно создан и валидирован!")
            return quest
            
        except Exception as e:
            print(f"Ошибка в LangChain генерации: {e}")
            return {"error": f"Ошибка LangChain генерации: {e}"}
    
    def is_available(self) -> bool:
        """Проверка доступности LangChain генератора"""
        return LANGCHAIN_AVAILABLE and self.llm is not None


# Глобальный экземпляр LangChain генератора
langchain_generator = LangChainQuestGenerator()