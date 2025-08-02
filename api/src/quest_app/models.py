from django.db import models
from .fields import UnicodeJSONField
import json

class QuestInput(models.Model):
    """Модель для хранения входных данных квеста"""
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    hero = models.CharField(max_length=200, verbose_name="Главный герой")
    goal = models.TextField(verbose_name="Цель квеста")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Квест: {self.genre} - {self.hero}"

class Quest(models.Model):
    """Модель для хранения сгенерированного квеста"""
    quest_input = models.ForeignKey(QuestInput, on_delete=models.CASCADE, related_name='quests')
    quest_data = UnicodeJSONField(verbose_name="Данные квеста в JSON")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Квест {self.id} - {self.quest_input.genre}"
    
    def get_scenes(self):
        """Возвращает список сцен из JSON данных"""
        return self.quest_data.get('scenes', [])
