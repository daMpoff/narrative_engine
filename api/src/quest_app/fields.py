from django.db import models
import json

class UnicodeJSONField(models.JSONField):
    """Кастомное JSON поле с поддержкой Unicode"""
    
    def get_prep_value(self, value):
        """Подготовка значения для сохранения в БД"""
        if value is None:
            return value
        return json.dumps(value, ensure_ascii=False)
    
    def from_db_value(self, value, expression, connection):
        """Извлечение значения из БД"""
        if value is None:
            return value
        if isinstance(value, str):
            return json.loads(value)
        return value
    
    def to_python(self, value):
        """Преобразование в Python объект"""
        if value is None:
            return value
        if isinstance(value, str):
            return json.loads(value)
        return value 