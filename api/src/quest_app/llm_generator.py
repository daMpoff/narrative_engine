import json
import os
from typing import Dict, List, Optional, Tuple, Set
from django.conf import settings

# Mistral AI imports
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    print("Warning: Mistral AI not available. Using stub generator.")


class QuestGenerator:
    """Генератор квестов с использованием Mistral AI"""
    
    def __init__(self):
        self.client = None
        self.setup_mistral()
    
    def setup_mistral(self):
        """Настройка Mistral AI"""
        if not MISTRAL_AVAILABLE:
            print("Mistral AI недоступен, используем заглушку")
            return
        
        api_key = settings.MISTRAL_API_KEY
        if not api_key:
            print("Mistral API ключ не найден в переменных окружения")
            print("Убедитесь, что MISTRAL_API_KEY установлен в .env файле")
            return
        
        if api_key == "your_mistral_api_key_here":
            print("Mistral API ключ не настроен (используется значение по умолчанию)")
            print("Пожалуйста, установите правильный API ключ в .env файле")
            return
        
        try:
            self.client = MistralClient(api_key=api_key)
            print(f"Mistral AI настроен: {settings.MISTRAL_MODEL}")
            print(f"API ключ: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
        except Exception as e:
            print(f"Ошибка настройки Mistral AI: {e}")
            print("Проверьте правильность API ключа и подключение к интернету")
    
    def create_prompt_template(self) -> str:
        """Создает промпт для генерации квеста"""
        return """Ты - опытный геймдизайнер, специализирующийся на создании увлекательных и разнообразных текстовых квестов. 

Создай уникальный и захватывающий текстовый квест в формате JSON со следующими требованиями:

Жанр: {genre}
Главный герой: {hero}
Цель: {goal}

КРИТИЧЕСКИ ВАЖНО: 
1. ВСЕ пути в квесте должны в конечном итоге вести к сцене с scene_id "quest_end"
2. ОБЯЗАТЕЛЬНО создай сцену с scene_id "quest_end" как финальную сцену
3. Никаких тупиковых веток или циклов!

ОСНОВНЫЕ ТРЕБОВАНИЯ:

1. СТРУКТУРА КВЕСТА:
   - Создай {scene_count} сцен (от 5 до 10)
   - Каждая сцена должна содержать текст ситуации или диалога
   - Каждая сцена должна иметь минимум 2 варианта выбора игрока
   - Создай минимум одну развилку с глубиной не менее {max_depth} сцен

2. СЛОЖНОСТЬ СЮЖЕТА ({complexity}):
   - Простой: линейный сюжет с простыми выборами, но интересными ситуациями
   - Средний: несколько веток с умеренной сложностью и разнообразными путями
   - Сложный: много веток, скрытые пути, неожиданные повороты, сложные моральные выборы
   - Эпический: сложная структура с множественными путями, глубокими последствиями и масштабными событиями

3. ТИП КОНЦОВОК ({ending_type}):
   - Одна концовка: все пути ведут к одному финалу, но разными способами
   - Множественные концовки: разные финалы в зависимости от выбора с уникальными исходами
   - Разветвленные концовки: сложная система финалов с множественными исходами и последствиями

4. ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ:
   - Создай {scene_count} сцен с уникальными описательными scene_id (например: village_gate, guard_dialogue, forest_path)
   - Каждая сцена должна содержать детальное описание ситуации (минимум 80 слов)
   - В КАЖДОЙ сцене должно быть минимум 2 варианта выбора игрока
   - ОБЯЗАТЕЛЬНО создай хотя бы одну ветку с глубиной минимум {max_depth} сцен
   - ОБЯЗАТЕЛЬНО создай сцену с scene_id "quest_end" как финальную сцену
   - Все ветки должны логически завершаться в quest_end

5. СТРУКТУРА ВЫБОРОВ:
   - ВСЕ сцены должны иметь минимум 2 выбора (кроме quest_end)
   - Сцена quest_end может иметь только 1 выбор, который ведет к quest_end
   - ВСЕ финальные сцены должны иметь ВСЕ выборы, ведущие к quest_end
   - Обычные сцены должны иметь 2-3 выбора для ветвления
   - НЕ создавай сцены с менее чем 2 выборами (кроме quest_end)
   - ВАЖНО: ВСЕ пути в квесте должны в конечном итоге вести к quest_end

6. КРЕАТИВНОСТЬ И УНИКАЛЬНОСТЬ:
   - Каждая сцена должна быть уникальной и запоминающейся
   - Используй неожиданные ситуации и нестандартные решения
   - Создавай атмосферные и эмоциональные моменты
   - Избегай клише и шаблонных сюжетных ходов
   - Добавляй уникальные детали и особенности в каждую сцену

ВАЖНО: Отвечай ТОЛЬКО валидный JSON без дополнительного текста, комментариев, объяснений или markdown блоков. НЕ используй ```json или ```. НЕ используй markdown вообще. Начинай ответ сразу с {{ и заканчивай }}. Убедись, что все кавычки закрыты и JSON синтаксически корректен. ОБЯЗАТЕЛЬНО создай ключ "scenes" с массивом сцен. НЕ создавай отдельные объекты сцен на верхнем уровне - все сцены должны быть внутри массива "scenes". ВАЖНО: НЕ ставь запятые после последнего элемента в объектах и массивах.

Формат ответа (ОБЯЗАТЕЛЬНО используй эту структуру):
{{
  "scenes": [
    {{
      "scene_id": "village_gate",
      "text": "Вы подходите к воротам деревни. Страж в броне пристально смотрит на вас.",
      "choices": [
        {{
          "text": "Поговорить со стражем",
          "next_scene": "guard_dialogue"
        }},
        {{
          "text": "Пойти обратно в лес", 
          "next_scene": "forest_path"
        }}
      ]
    }},
    {{
      "scene_id": "final_confrontation",
      "text": "Финальная сцена с завершением квеста...",
      "choices": [
        {{
          "text": "Завершить квест успешно",
          "next_scene": "quest_end"
        }},
        {{
          "text": "Попробовать альтернативный путь",
          "next_scene": "quest_end"
        }}
      ]
    }},
    {{
      "scene_id": "quest_end",
      "text": "Квест завершен!",
      "choices": [
        {{
          "text": "Завершить игру",
          "next_scene": "quest_end"
        }}
      ]
    }}
  ]
}}

ВАЖНО: НЕ создавай отдельные объекты сцен вне массива "scenes". ВСЕ сцены должны быть внутри массива "scenes".

ПРАВИЛА SCENE_ID:
- Используй описательные идентификаторы (например: village_gate, guard_dialogue, forest_path)
- НЕ используй числовые идентификаторы (scene_1, scene_2, etc.)
- Каждый scene_id должен отражать содержание сцены
- Используй snake_case формат (слова_разделены_подчеркиваниями)
- ОБЯЗАТЕЛЬНО создай сцену с scene_id "quest_end" как финальную сцену

ПРАВИЛА ВЫБОРОВ:
- ВСЕ сцены должны иметь минимум 2 выбора (кроме quest_end)
- Сцена quest_end может иметь только 1 выбор, который ведет к quest_end
- ВСЕ финальные сцены должны иметь ВСЕ выборы, ведущие к quest_end
- Обычные сцены должны иметь 2-3 выбора для ветвления
- ВАЖНО: ВСЕ пути в квесте должны в конечном итоге вести к quest_end

Создай квест, который будет ПОЛНОСТЬЮ НЕПОВТОРИМЫМ, ЗАХВАТЫВАЮЩИМ и соответствовать всем требованиям!

ПОСЛЕДНЕЕ НАПОМИНАНИЕ: Отвечай ТОЛЬКО валидный JSON. НЕ используй markdown блоки (```json). Начинай ответ сразу с {{ и заканчивай }}. ОБЯЗАТЕЛЬНО создай ключ "scenes" с массивом сцен. НЕ создавай отдельные объекты сцен - все сцены должны быть внутри массива "scenes". ВАЖНО: НЕ ставь запятые после последнего элемента в объектах и массивах. Проверь, что все кавычки закрыты, все скобки сбалансированы, и нет синтаксических ошибок."""

    def _clean_json_response(self, content: str) -> str:
        """Простая очистка JSON ответа от markdown блоков"""
        content = content.strip()
        
        # Удаляем markdown блоки
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()

    def generate_quest_with_mistral(self, genre: str, hero: str, goal: str) -> Dict:
        """Генерация квеста с использованием Mistral AI"""
        if not self.client:
            print("Mistral AI недоступен")
            return {"error": "Mistral AI не настроен. Проверьте API ключ и настройки."}
        
        try:
            prompt = self.create_prompt_template().format(
                genre=genre,
                hero=hero,
                goal=goal
            )
            
            print(f"Отправляем запрос к Mistral AI...")
            
            messages = [
                ChatMessage(role="system", content="Ты - эксперт по созданию текстовых квестов. Отвечай ТОЛЬКО валидный JSON без дополнительного текста, комментариев или markdown блоков. НЕ используй ```json или любые markdown блоки. Начинай ответ сразу с {{ и заканчивай }}. ОБЯЗАТЕЛЬНО создай ключ 'scenes' с массивом сцен. НЕ создавай отдельные объекты сцен на верхнем уровне - все сцены должны быть внутри массива 'scenes'. ВАЖНО: НЕ ставь запятые после последнего элемента в объектах и массивах."),
                ChatMessage(role="user", content=prompt)
            ]
            
            try:
                response = self.client.chat(
                    model=settings.MISTRAL_MODEL,
                    messages=messages,
                    temperature=settings.LLM_CONFIG.get('temperature', 0.7),
                    max_tokens=settings.LLM_CONFIG.get('max_tokens', 2000)
                )
            except Exception as e:
                print(f"Ошибка при запросе к Mistral AI: {e}")
                return {"error": f"Ошибка API Mistral AI: {e}"}
            
            content = response.choices[0].message.content
            print(f"Получен ответ от Mistral AI:")
            print(f"Длина ответа: {len(content)} символов")
            print(f"Первые 200 символов: {content[:200]}...")
            
            # Простая очистка от markdown блоков
            cleaned_content = self._clean_json_response(content)
            
            # Парсим JSON
            try:
                quest_data = json.loads(cleaned_content)
                print("JSON успешно распарсен!")
                return quest_data
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
                print(f"Полный ответ от Mistral AI:")
                print(content)
                return {"error": f"Ошибка парсинга ответа от Mistral AI: {e}"}
            
        except Exception as e:
            print(f"Ошибка генерации с Mistral AI: {e}")
            return {"error": f"Ошибка генерации с Mistral AI: {e}"}

    def validate_quest(self, quest_data: Dict) -> Tuple[bool, str]:
        """Валидирует сгенерированный квест"""
        try:
            if not isinstance(quest_data, dict):
                return False, "Квест должен быть объектом"

            scenes = quest_data.get('scenes', [])
            if not scenes:
                return False, "Квест должен содержать сцены"

            # Проверяем количество сцен
            if len(scenes) < 5:
                return False, f"Недостаточно сцен: {len(scenes)} (минимум 5)"

            # Проверяем каждую сцену
            scene_ids = set()
            has_quest_end = False
            for scene in scenes:
                scene_id = scene.get('scene_id')
                if not scene_id:
                    return False, "Каждая сцена должна иметь scene_id"
                
                if scene_id in scene_ids:
                    return False, f"Дублирующийся scene_id: {scene_id}"
                scene_ids.add(scene_id)
                
                if scene_id == "quest_end":
                    has_quest_end = True

                # Проверяем текст сцены
                scene_text = scene.get('text', '')
                if len(scene_text) < 50:
                    return False, f"Сцена {scene_id}: текст слишком короткий ({len(scene_text)} символов)"

                # Проверяем выборы
                choices = scene.get('choices', [])
                
                # ВСЕ сцены должны иметь минимум 2 выбора (кроме quest_end)
                if len(choices) < 2 and scene_id != "quest_end":
                    return False, f"Сцена {scene_id}: недостаточно выборов ({len(choices)}). Минимум 2 выбора в каждой сцене (кроме quest_end)."
                
                # Максимум 3 выбора для любой сцены (кроме quest_end)
                if len(choices) > 3 and scene_id != "quest_end":
                    return False, f"Сцена {scene_id}: слишком много выборов ({len(choices)}). Максимум 3 выбора в каждой сцене (кроме quest_end)."

                for choice in choices:
                    if not choice.get('text') or not choice.get('next_scene'):
                        return False, f"Сцена {scene_id}: неполный выбор"

            # Проверяем наличие сцены quest_end
            if not has_quest_end:
                return False, "Квест должен содержать сцену с scene_id 'quest_end'"

            # Проверяем структуру сцены quest_end
            quest_end_scene = None
            for scene in scenes:
                if scene.get('scene_id') == 'quest_end':
                    quest_end_scene = scene
                    break
            
            if quest_end_scene:
                quest_end_choices = quest_end_scene.get('choices', [])
                if len(quest_end_choices) < 1:
                    return False, "Сцена quest_end должна иметь минимум 1 выбор"
                for choice in quest_end_choices:
                    if choice.get('next_scene') != 'quest_end':
                        return False, "Все выборы в сцене quest_end должны вести к quest_end"

            # Проверяем, что все ссылки на сцены существуют
            for scene in scenes:
                scene_id = scene.get('scene_id')
                choices = scene.get('choices', [])
                for choice in choices:
                    next_scene = choice.get('next_scene')
                    if next_scene not in scene_ids:
                        return False, f"Сцена {scene_id} ссылается на несуществующую сцену: {next_scene}"

            # Проверяем структуру ветвления
            is_valid_branching, branching_error = self._validate_branching_structure(scenes)
            if not is_valid_branching:
                return False, branching_error

            return True, "Квест прошел валидацию"

        except Exception as e:
            return False, f"Ошибка валидации: {e}"

    def _validate_branching_structure(self, scenes: List[Dict]) -> Tuple[bool, str]:
        """Проверяет структуру ветвления квеста"""
        try:
            # Создаем граф сцен
            scene_graph = {}
            for scene in scenes:
                scene_id = scene['scene_id']
                choices = scene.get('choices', [])
                scene_graph[scene_id] = [choice['next_scene'] for choice in choices]

            # Находим начальную сцену (первая сцена в списке)
            if not scenes:
                return False, "Нет сцен для проверки"
            
            start_scene = scenes[0]['scene_id']
            
            # Проверяем, что есть хотя бы одна ветка с глубиной >= 3
            max_depth = self._calculate_max_depth(start_scene, scene_graph, set())
            
            if max_depth < 3:
                return False, f"Максимальная глубина слишком мала: {max_depth} (минимум 3)"

            # Проверяем, что все пути ведут к quest_end
            all_paths_valid, problematic_paths = self._all_paths_lead_to_end(start_scene, scene_graph, set())
            if not all_paths_valid:
                return False, f"Не все пути ведут к quest_end. Проблемные пути: {', '.join(problematic_paths)}"

            return True, "Структура ветвления корректна"

        except Exception as e:
            return False, f"Ошибка проверки ветвления: {e}"

    def _calculate_max_depth(self, scene_id: str, scene_graph: Dict, visited: Set) -> int:
        """Вычисляет максимальную глубину от заданной сцены"""
        if scene_id in visited or scene_id == "quest_end":
            return 0

        visited.add(scene_id)
        if scene_id not in scene_graph:
            return 0

        max_depth = 0
        for next_scene in scene_graph[scene_id]:
            if next_scene != "quest_end":
                depth = self._calculate_max_depth(next_scene, scene_graph, set(visited))
                max_depth = max(max_depth, depth)

        return max_depth + 1

    def _all_paths_lead_to_end(self, scene_id: str, scene_graph: Dict, visited: Set) -> Tuple[bool, List[str]]:
        """Проверяет, что все пути ведут к quest_end. Возвращает (успех, список проблемных путей)"""
        if scene_id in visited:
            return False, [f"Цикл обнаружен в {scene_id}"]

        if scene_id == "quest_end":
            return True, []

        visited.add(scene_id)
        if scene_id not in scene_graph:
            return False, [f"Сцена {scene_id} не найдена в графе"]

        problematic_paths = []
        all_paths_valid = True

        for next_scene in scene_graph[scene_id]:
            is_valid, problems = self._all_paths_lead_to_end(next_scene, scene_graph, set(visited))
            if not is_valid:
                all_paths_valid = False
                problematic_paths.extend([f"{scene_id} -> {problem}" for problem in problems])

        return all_paths_valid, problematic_paths

    def generate_quest(self, genre: str, hero: str, goal: str, scene_count: int = 10, max_depth: int = 5, complexity: str = "medium", ending_type: str = "single") -> Dict:
        """Генерирует квест с использованием Mistral AI"""
        try:
            if not self.client:
                print("Mistral AI не настроен")
                return {"error": "Mistral AI не настроен. Проверьте API ключ и настройки."}

            # Создаем промпт с новыми параметрами
            prompt = self.create_prompt_template().format(
                genre=genre,
                hero=hero,
                goal=goal,
                scene_count=scene_count,
                max_depth=max_depth,
                complexity=complexity,
                ending_type=ending_type
            )

            print(f"Отправляем запрос к Mistral AI с параметрами:")
            print(f"- Количество сцен: {scene_count}")
            print(f"- Максимальная глубина: {max_depth}")
            print(f"- Сложность: {complexity}")
            print(f"- Тип концовок: {ending_type}")

            # Генерируем ответ от Mistral AI
            try:
                response = self.client.chat(
                    model=settings.MISTRAL_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=settings.LLM_CONFIG.get('max_tokens', 2000),
                    temperature=settings.LLM_CONFIG.get('temperature', 0.7)
                )
            except Exception as e:
                print(f"Ошибка при запросе к Mistral AI: {e}")
                return {"error": f"Ошибка API Mistral AI: {e}"}

            # Получаем текст ответа
            response_text = response.choices[0].message.content
            print(f"Получен ответ от Mistral AI (первые 200 символов): {response_text[:200]}...")

            # Проверяем, что ответ не пустой
            if not response_text or response_text.strip() == "":
                print("Получен пустой ответ от Mistral AI")
                return {"error": "Получен пустой ответ от ИИ. Проверьте API ключ и настройки."}

            # Простая очистка от markdown блоков
            cleaned_text = self._clean_json_response(response_text)
            
            print(f"Очищенный текст для парсинга JSON:")
            print(f"Первые 200 символов: {cleaned_text[:200]}...")
            
            # Проверяем, что очищенный текст не пустой
            if not cleaned_text:
                print("После очистки текст пустой")
                return {"error": "Не удалось извлечь JSON из ответа ИИ"}
            
            # Парсим JSON
            try:
                quest_data = json.loads(cleaned_text)
                print("JSON успешно распарсен!")
            except json.JSONDecodeError as json_error:
                print(f"Ошибка парсинга JSON: {json_error}")
                print(f"Полный ответ от Mistral AI:")
                print(response_text)
                return {"error": f"Ошибка парсинга ответа от ИИ: {json_error}. Полученный ответ: {response_text[:500]}..."}
            
            # Проверяем структуру JSON
            if not isinstance(quest_data, dict):
                return {"error": "Получен неверный формат JSON - ожидается объект"}
            
            if 'scenes' not in quest_data:
                return {"error": f"JSON не содержит ключ 'scenes'. Доступные ключи: {list(quest_data.keys())}"}
            
            if not isinstance(quest_data['scenes'], list):
                return {"error": f"Ключ 'scenes' должен быть массивом, получен: {type(quest_data['scenes'])}"}
            
            # Валидируем квест
            is_valid, validation_message = self.validate_quest(quest_data)
            if not is_valid:
                print(f"Квест не прошел валидацию: {validation_message}")
                return {"error": f"Сгенерированный квест не соответствует требованиям: {validation_message}"}

            print("Квест успешно сгенерирован и прошел валидацию")
            return quest_data

        except Exception as e:
            print(f"Ошибка генерации квеста: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Ошибка генерации квеста: {e}"} 