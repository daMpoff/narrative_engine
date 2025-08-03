"""
Улучшенный многоэтапный генератор квестов через LangChain
"""

import json
import os
from typing import Dict, Any, List, Optional

# Импорт Pydantic для валидации данных
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    print("Pydantic не найден, используем базовую валидацию")
    PYDANTIC_AVAILABLE = False
    BaseModel = object

# Импорт LangChain компонентов
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    print("langchain_core не найден")
    LANGCHAIN_CORE_AVAILABLE = False

# Импорт Mistral AI для LangChain
ChatMistralAI = None
try:
    from langchain_mistralai import ChatMistralAI
    MISTRAL_LANGCHAIN_AVAILABLE = True
    print("langchain_mistralai успешно импортирован")
except ImportError:
    try:
        from langchain.llms import ChatMistralAI
        MISTRAL_LANGCHAIN_AVAILABLE = True
        print("ChatMistralAI импортирован из langchain.llms")
    except ImportError:
        MISTRAL_LANGCHAIN_AVAILABLE = False
        print("Mistral AI для LangChain не найден")

# Модели данных для валидации
if PYDANTIC_AVAILABLE:
    class QuestScene(BaseModel):
        scene_id: str = Field(..., description="Уникальный ID сцены")
        text: str = Field(..., min_length=10, description="Описание сцены")
        choices: List[Dict[str, str]] = Field(..., description="Список выборов")

        @validator('text')
        def text_must_be_meaningful(cls, v):
            if len(v.strip()) < 10:
                raise ValueError('Текст сцены должен содержать минимум 10 символов')
            return v

    class Quest(BaseModel):
        scenes: List[QuestScene] = Field(..., description="Список сцен квеста")

class LangChainQuestGenerator:
    """Многоэтапный генератор квестов с детальным планированием"""
    
    def __init__(self):
        self.llm = None
        self.step1_mapper = None     # Этап 1: Структурная карта
        self.step2_planner = None    # Этап 2: Детальное планирование
        self.step3_generator = None  # Этап 3: Генерация контента
        self.step4_validator = None  # Этап 4: Валидация и исправления
        self.setup_langchain()
    
    def is_available(self) -> bool:
        """Проверка доступности LangChain"""
        return (LANGCHAIN_CORE_AVAILABLE and 
                MISTRAL_LANGCHAIN_AVAILABLE and 
                self.llm is not None)
    
    def setup_langchain(self):
        """Настройка LangChain и создание цепочек"""
        if not LANGCHAIN_CORE_AVAILABLE or not MISTRAL_LANGCHAIN_AVAILABLE:
            print("❌ LangChain компоненты недоступны")
            return
            
        try:
            # Получаем API ключ
            api_key = os.getenv('MISTRAL_API_KEY')
            if not api_key:
                print("❌ MISTRAL_API_KEY не найден в переменных окружения")
                return
            
            # Инициализация Mistral AI
            self.llm = ChatMistralAI(
                model="mistral-large-latest",
                mistral_api_key=api_key,
                temperature=0.7
            )
            
            # Создание всех этапов
            self._create_step1_mapping()
            self._create_step2_planning()
            self._create_step3_generation()
            self._create_step4_validation()
            
            print("✅ LangChain Quest Generator настроен успешно")
            
        except Exception as e:
            print(f"❌ Ошибка настройки LangChain: {e}")
            self.llm = None
    
    def _create_step1_mapping(self):
        """Этап 1: Создание структурной карты квеста"""
        mapping_prompt = ChatPromptTemplate.from_messages([
            ("system", """ЭТАП 1: СТРУКТУРНАЯ КАРТА КВЕСТА

Ты - архитектор квестов. Создай ОБЩУЮ СТРУКТУРУ для жанра "{genre}", героя "{hero}", цели "{goal}".

ЗАДАЧА: Придумай {scene_count} уникальных локаций/ситуаций:

1. НАЗВАНИЯ СЦЕН по содержанию:
   - Места: "dark_forest", "ancient_temple", "dragon_lair"
   - Действия: "search_ruins", "battle_bandits", "solve_puzzle"
   - События: "meet_wizard", "find_artifact", "final_confrontation"

2. ЛОГИЧЕСКАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ:
   - start: всегда первая (точка входа)
   - 2-3 развилки: места выбора пути
   - quest_end: всегда последняя (финал)

3. СВЯЗИ между сценами (кто к кому ведет)

Формат ответа:
{{
  "quest_structure": {{
    "theme": "краткое описание темы квеста",
    "scenes": [
      {{
        "scene_id": "start",
        "type": "entry_point",
        "concept": "Начальная ситуация"
      }},
      {{
        "scene_id": "meaningful_name1",
        "type": "exploration/action/decision",
        "concept": "Что происходит в этой сцене"
      }},
      {{
        "scene_id": "quest_end",
        "type": "conclusion",
        "concept": "Финальная сцена"
      }}
    ],
    "flow": {{
      "start": ["scene1", "scene2"],
      "scene1": ["scene3"],
      "scene2": ["quest_end"],
      "scene3": ["quest_end"],
      "quest_end": ["quest_end"]
    }}
  }}
}}"""),
            ("human", "Создай структурную карту квеста.")
        ])
        
        self.step1_mapper = mapping_prompt | self.llm | JsonOutputParser()
    
    def _create_step2_planning(self):
        """Этап 2: Детальное планирование выборов"""
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """ЭТАП 2: ДЕТАЛЬНОЕ ПЛАНИРОВАНИЕ ВЫБОРОВ

Основа: {quest_structure}
Параметры: {genre}, {hero}, {goal}

ЗАДАЧА: Для КАЖДОЙ сцены спланируй КОНКРЕТНЫЕ ВЫБОРЫ:

1. ТИП ВЫБОРОВ для каждой сцены:
   - Действие vs Осторожность: "Атаковать" vs "Обойти"
   - Риск vs Безопасность: "Рискнуть" vs "Играть осторожно"
   - Помощь vs Самостоятельность: "Попросить помощи" vs "Справиться самому"
   - Исследование vs Продвижение: "Изучить детально" vs "Идти дальше"

2. КАЖДЫЙ ВЫБОР должен:
   - Соответствовать концепции сцены
   - Логично вести к следующей сцене
   - Быть интересным игроку

Формат ответа:
{{
  "detailed_plan": [
    {{
      "scene_id": "start",
      "situation": "Описание ситуации в сцене",
      "choice_strategy": "Тип выбора (развилка/действие/etc)",
      "planned_choices": [
        {{
          "choice_text": "Конкретный текст выбора",
          "choice_type": "action/caution/risk/etc",
          "next_scene": "куда ведет",
          "reasoning": "почему этот выбор логичен"
        }}
      ]
    }}
  ]
}}"""),
            ("human", "Создай детальный план выборов.")
        ])
        
        self.step2_planner = planning_prompt | self.llm | JsonOutputParser()
    
    def _create_step3_generation(self):
        """Этап 3: Генерация полного контента"""
        generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """ЭТАП 3: ГЕНЕРАЦИЯ ПОЛНОГО КОНТЕНТА

План: {detailed_plan}
Параметры: {genre}, {hero}, {goal}

ЗАДАЧА: Создай ПОЛНЫЕ тексты сцен и выборов по плану.

ТРЕБОВАНИЯ:
1. Текст сцены: минимум 50 слов, живое описание
2. Выборы: точно как в плане, интересные формулировки
3. next_scene: ТОЛЬКО из существующих scene_id
4. Стиль: соответствует жанру

ВАЖНО: НЕ меняй структуру из плана, только добавляй детали!

Формат ответа:
{{
  "scenes": [
    {{
      "scene_id": "точно как в плане",
      "text": "Полное описание ситуации (50+ слов)",
      "choices": [
        {{
          "text": "Текст выбора как в плане",
          "next_scene": "точно как указано в плане"
        }}
      ]
    }}
  ]
}}"""),
            ("human", "Сгенерируй полный контент по плану.")
        ])
        
        self.step3_generator = generation_prompt | self.llm | JsonOutputParser()
    
    def _create_step4_validation(self):
        """Этап 4: Валидация и автоисправления"""
        validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """ЭТАП 4: ВАЛИДАЦИЯ И ИСПРАВЛЕНИЯ

Квест: {quest}

ПРОВЕРЬ И ИСПРАВЬ:
1. Каждая сцена (кроме quest_end) имеет минимум 2 выбора
2. Все next_scene существуют в списке сцен
3. quest_end имеет выбор "Завершить квест" -> quest_end
4. Нет циклов (сцены не ведут назад)

ЕСЛИ НАХОДИШЬ ОШИБКИ - ИСПРАВЬ ИХ!

Формат ответа:
{{
  "validation_result": "passed/fixed",
  "issues_found": ["список найденных проблем"],
  "corrections_made": ["список исправлений"],
  "final_quest": {{
    "scenes": [...]
  }}
}}"""),
            ("human", "Проверь и исправь квест.")
        ])
        
        self.step4_validator = validation_prompt | self.llm | JsonOutputParser()
    
    def generate_quest(self, genre: str, hero: str, goal: str, scene_count: int = 10, 
                      max_depth: int = 5, complexity: str = "medium", 
                      ending_type: str = "single") -> Dict[str, Any]:
        """Многоэтапная генерация квеста"""
        
        if not self.is_available():
            return {"error": "LangChain генератор недоступен"}
        
        try:
            print("🗺️ Этап 1: Создание структурной карты...")
            
            # Этап 1: Структурная карта
            structure_params = {
                "genre": genre,
                "hero": hero,
                "goal": goal,
                "scene_count": scene_count
            }
            
            quest_structure = self.step1_mapper.invoke(structure_params)
            print(f"✅ Структура создана: {len(quest_structure.get('quest_structure', {}).get('scenes', []))} сцен")
            
            print("📋 Этап 2: Детальное планирование выборов...")
            
            # Этап 2: Детальное планирование
            planning_params = {
                "quest_structure": json.dumps(quest_structure, ensure_ascii=False),
                "genre": genre,
                "hero": hero,
                "goal": goal
            }
            
            detailed_plan = self.step2_planner.invoke(planning_params)
            planned_scenes = detailed_plan.get('detailed_plan', [])
            print(f"✅ План детализирован: {len(planned_scenes)} сцен с выборами")
            
            print("✍️ Этап 3: Генерация полного контента...")
            
            # Этап 3: Генерация контента
            generation_params = {
                "detailed_plan": json.dumps(detailed_plan, ensure_ascii=False),
                "genre": genre,
                "hero": hero,
                "goal": goal
            }
            
            quest_content = self.step3_generator.invoke(generation_params)
            generated_scenes = quest_content.get('scenes', [])
            print(f"✅ Контент сгенерирован: {len(generated_scenes)} сцен")
            
            print("🔍 Этап 4: Валидация и исправления...")
            
            # Этап 4: Валидация и исправления
            validation_params = {
                "quest": json.dumps(quest_content, ensure_ascii=False)
            }
            
            validation_result = self.step4_validator.invoke(validation_params)
            
            if validation_result.get('validation_result') == 'passed':
                print("✅ Квест прошел валидацию!")
                final_quest = validation_result.get('final_quest', quest_content)
            elif validation_result.get('validation_result') == 'fixed':
                print("🔧 Квест исправлен автоматически!")
                corrections = validation_result.get('corrections_made', [])
                for correction in corrections:
                    print(f"  - {correction}")
                final_quest = validation_result.get('final_quest', quest_content)
            else:
                issues = validation_result.get('issues_found', [])
                print(f"❌ Критические ошибки: {issues}")
                return {"error": f"Не удалось исправить ошибки: {', '.join(issues)}"}
            
            print("🎉 Квест успешно создан!")
            return final_quest
            
        except Exception as e:
            print(f"❌ Ошибка в многоэтапной генерации: {e}")
            return {"error": f"Ошибка генерации: {str(e)}"}