import json
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import QuestInput, Quest
from .serializers import QuestInputSerializer, QuestSerializer
from .llm_generator import QuestGenerator


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
