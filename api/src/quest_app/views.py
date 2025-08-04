import json
import os
import re
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import QuestInput, Quest
from .serializers import QuestInputSerializer, QuestSerializer
from .llm_generator import QuestGenerator


def parse_txt_file(file_content):
    """Парсит содержимое txt файла и извлекает жанр, героя и цель"""
    try:
        # Разбиваем содержимое на строки
        lines = file_content.split('\n')
        
        parsed_data = {
            'genre': '',
            'hero': '',
            'goal': ''
        }
        
        # Паттерны для поиска данных (используем более точные регулярки)
        genre_patterns = [
            r'жанр\s*[:\s]\s*([^:\n]+?)(?:\s*главный|\s*герой|\s*персонаж|\s*цель|\s*задача|\s*миссия|$)',
            r'genre\s*[:\s]\s*([^:\n]+?)(?:\s*hero|\s*protagonist|\s*goal|\s*objective|$)',
            r'стиль\s*[:\s]\s*([^:\n]+?)(?:\s*главный|\s*герой|\s*персонаж|\s*цель|\s*задача|$)',
        ]
        
        hero_patterns = [
            r'главный\s+герой\s*[:\s]\s*([^:\n]+?)(?:\s*цель|\s*задача|\s*миссия|\s*goal|$)',
            r'герой\s*[:\s]\s*([^:\n]+?)(?:\s*цель|\s*задача|\s*миссия|\s*goal|$)',
            r'персонаж\s*[:\s]\s*([^:\n]+?)(?:\s*цель|\s*задача|\s*миссия|\s*goal|$)',
            r'protagonist\s*[:\s]\s*([^:\n]+?)(?:\s*goal|\s*objective|$)',
            r'hero\s*[:\s]\s*([^:\n]+?)(?:\s*goal|\s*objective|$)',
        ]
        
        goal_patterns = [
            r'цель\s*[:\s]\s*([^:\n]+?)(?:\s*$)',
            r'задача\s*[:\s]\s*([^:\n]+?)(?:\s*$)',
            r'миссия\s*[:\s]\s*([^:\n]+?)(?:\s*$)',
            r'goal\s*[:\s]\s*([^:\n]+?)(?:\s*$)',
            r'objective\s*[:\s]\s*([^:\n]+?)(?:\s*$)',
        ]
        
        # Обрабатываем каждую строку отдельно
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            
            # Ищем жанр в этой строке
            if not parsed_data['genre']:
                for pattern in genre_patterns:
                    match = re.search(pattern, line_lower, re.IGNORECASE)
                    if match:
                        parsed_data['genre'] = match.group(1).strip(' .,()«»"')
                        break
            
            # Ищем героя в этой строке
            if not parsed_data['hero']:
                for pattern in hero_patterns:
                    match = re.search(pattern, line_lower, re.IGNORECASE)
                    if match:
                        parsed_data['hero'] = match.group(1).strip(' .,()«»"')
                        break
            
            # Ищем цель в этой строке
            if not parsed_data['goal']:
                for pattern in goal_patterns:
                    match = re.search(pattern, line_lower, re.IGNORECASE)
                    if match:
                        parsed_data['goal'] = match.group(1).strip(' .,()«»"')
                        break
        
        # Если не нашли через регулярки, пробуем простой подход
        if not all([parsed_data['genre'], parsed_data['hero'], parsed_data['goal']]):
            # Удаляем пустые строки и ищем по порядку
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            # Простая эвристика: первые 3 непустые строки
            if len(non_empty_lines) >= 3:
                if not parsed_data['genre']:
                    # Если первая строка содержит только одно слово (жанр)
                    first_line = non_empty_lines[0]
                    if ':' not in first_line:
                        parsed_data['genre'] = first_line
                    else:
                        # Извлекаем часть после двоеточия
                        parts = first_line.split(':', 1)
                        if len(parts) > 1:
                            parsed_data['genre'] = parts[1].strip()
                
                if not parsed_data['hero']:
                    second_line = non_empty_lines[1]
                    if ':' not in second_line:
                        parsed_data['hero'] = second_line
                    else:
                        parts = second_line.split(':', 1)
                        if len(parts) > 1:
                            parsed_data['hero'] = parts[1].strip()
                
                if not parsed_data['goal']:
                    third_line = non_empty_lines[2]
                    if ':' not in third_line:
                        parsed_data['goal'] = third_line
                    else:
                        parts = third_line.split(':', 1)
                        if len(parts) > 1:
                            parsed_data['goal'] = parts[1].strip()
        
        return parsed_data
        
    except Exception as e:
        print(f"Ошибка парсинга файла: {e}")
        return None


def save_quest_to_file(quest_data, genre, hero, goal):
    """Сохраняет квест в JSON файл"""
    try:
        # Создаем папку output если её нет
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Создаем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quest_{genre}_{hero}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Подготавливаем данные для сохранения
        quest_info = {
            "metadata": {
                "genre": genre,
                "hero": hero,
                "goal": goal,
                "generated_at": datetime.now().isoformat(),
                "model": "mistral-large-latest"
            },
            "quest_data": quest_data
        }
        
        # Сохраняем в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(quest_info, f, ensure_ascii=False, indent=2)
        
        return filename
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")
        import traceback
        traceback.print_exc()
        return None


@api_view(['POST'])
def generate_quest(request):
    """Генерирует новый квест"""
    try:
        # Получаем данные из запроса
        genre = request.data.get('genre')
        hero = request.data.get('hero')
        goal = request.data.get('goal')
        
        # Получаем новые параметры генерации
        scene_count = request.data.get('scene_count', 10)
        max_depth = request.data.get('max_depth', 5)
        complexity = request.data.get('complexity', 'medium')
        ending_type = request.data.get('ending_type', 'single')

        # Проверяем обязательные поля
        if not all([genre, hero, goal]):
            return Response(
                {"error": "Необходимо указать genre, hero и goal"},
                status=400
            )

        print(f"Генерируем квест с параметрами:")
        print(f"- Жанр: {genre}")
        print(f"- Герой: {hero}")
        print(f"- Цель: {goal}")
        print(f"- Количество сцен: {scene_count}")
        print(f"- Максимальная глубина: {max_depth}")
        print(f"- Сложность: {complexity}")
        print(f"- Тип концовок: {ending_type}")

        # Создаем генератор квестов
        generator = QuestGenerator()
        
        # Генерируем квест с новыми параметрами
        quest_data = generator.generate_quest(
            genre=genre,
            hero=hero,
            goal=goal,
            scene_count=scene_count,
            max_depth=max_depth,
            complexity=complexity,
            ending_type=ending_type
        )

        # Проверяем на ошибки
        if 'error' in quest_data:
            print(f"Ошибка генерации: {quest_data['error']}")
            return Response(
                {"error": quest_data['error']},
                status=500
            )

        # Создаем запись в базе данных
        quest_input = QuestInput.objects.create(
            genre=genre,
            hero=hero,
            goal=goal
        )

        # Сохраняем квест
        quest = Quest.objects.create(
            quest_input=quest_input,
            quest_data=quest_data
        )

        # Сохраняем в файл
        saved_file = save_quest_to_file(quest_data, genre, hero, goal)

        print(f"Квест успешно создан с ID: {quest.id}")
        if saved_file:
            print(f"Сохранен в файл: {saved_file}")
        else:
            print("Предупреждение: Не удалось сохранить в файл")

        # Возвращаем результат
        response_data = {
            "id": quest.id,
            "quest_data": quest_data,
            "saved_file": saved_file or "Не удалось сохранить",
            "message": "Квест успешно сгенерирован"
        }

        return Response(response_data)

    except Exception as e:
        print(f"Ошибка в generate_quest: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"Внутренняя ошибка сервера: {str(e)}"},
            status=500
        )


@api_view(['GET'])
def get_quests(request):
    """Получает список всех квестов"""
    try:
        quests = Quest.objects.all().order_by('-created_at')
        serializer = QuestSerializer(quests, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": f"Ошибка получения квестов: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_quest_detail(request, quest_id):
    """Получает детали конкретного квеста"""
    try:
        quest = Quest.objects.get(id=quest_id)
        serializer = QuestSerializer(quest)
        return Response(serializer.data)
    except Quest.DoesNotExist:
        return Response(
            {"error": "Квест не найден"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Ошибка получения квеста: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def parse_txt_quest(request):
    """Парсит загруженный txt файл и извлекает данные квеста"""
    try:
        # Проверяем, что файл был загружен
        if 'file' not in request.FILES:
            return Response(
                {"error": "Файл не найден. Убедитесь, что вы загружаете файл в поле 'file'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Проверяем расширение файла
        if not uploaded_file.name.lower().endswith('.txt'):
            return Response(
                {"error": "Поддерживаются только txt файлы"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Читаем содержимое файла
        try:
            file_content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            # Пробуем другую кодировку
            try:
                uploaded_file.seek(0)
                file_content = uploaded_file.read().decode('cp1251')
            except UnicodeDecodeError:
                return Response(
                    {"error": "Не удалось прочитать файл. Проверьте кодировку (поддерживается UTF-8 и Windows-1251)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Парсим содержимое
        parsed_data = parse_txt_file(file_content)
        
        if parsed_data is None:
            return Response(
                {"error": "Ошибка парсинга файла"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Проверяем, что удалось извлечь данные
        missing_fields = []
        if not parsed_data['genre']:
            missing_fields.append('жанр')
        if not parsed_data['hero']:
            missing_fields.append('героя')
        if not parsed_data['goal']:
            missing_fields.append('цель')
        
        if missing_fields:
            return Response(
                {
                    "warning": f"Не удалось извлечь: {', '.join(missing_fields)}",
                    "data": parsed_data,
                    "file_content": file_content[:500] + "..." if len(file_content) > 500 else file_content
                },
                status=status.HTTP_206_PARTIAL_CONTENT
            )
        
        return Response(
            {
                "success": True,
                "message": "Файл успешно обработан",
                "data": parsed_data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        print(f"Ошибка в parse_txt_quest: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"Внутренняя ошибка сервера: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
