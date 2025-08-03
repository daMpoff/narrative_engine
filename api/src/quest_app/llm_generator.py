"""
Упрощенный генератор квестов через LangChain
"""

from . import langchain_generator

class QuestGenerator:
    """Упрощенная обертка для LangChain генератора"""
    
    def __init__(self):
        self.langchain_gen = langchain_generator.LangChainQuestGenerator()
    
    def generate_quest(self, genre: str, hero: str, goal: str, scene_count: int = 10, 
                      max_depth: int = 5, complexity: str = "medium", 
                      ending_type: str = "single", max_retries: int = 3):
        """Генерирует квест используя только LangChain"""
        
        if not self.langchain_gen.is_available():
            return {"error": "LangChain генератор недоступен. Проверьте установку langchain-mistralai."}
        
        try:
            result = self.langchain_gen.generate_quest(
                genre=genre,
                hero=hero,
                goal=goal,
                scene_count=scene_count,
                max_depth=max_depth,
                complexity=complexity,
                ending_type=ending_type
            )
            return result
        except Exception as e:
            return {"error": f"Ошибка генерации: {str(e)}"}