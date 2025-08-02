from rest_framework import serializers
from .models import QuestInput, Quest
import json

class QuestInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestInput
        fields = ['id', 'genre', 'hero', 'goal', 'created_at']

class QuestSerializer(serializers.ModelSerializer):
    quest_input = QuestInputSerializer(read_only=True)
    
    class Meta:
        model = Quest
        fields = ['id', 'quest_input', 'quest_data', 'created_at']
    
    def to_representation(self, instance):
        """Кастомное представление для правильной кодировки JSON"""
        data = super().to_representation(instance)
        return data 