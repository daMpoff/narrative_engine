from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_quest, name='generate_quest'),
    path('quests/', views.get_quests, name='get_quests'),
    path('quests/<int:quest_id>/', views.get_quest_detail, name='get_quest_detail'),
] 