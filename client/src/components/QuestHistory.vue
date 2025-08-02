<template>
  <div class="quest-history">
    <div class="history-header">
      <h3 class="mb-3">
        <i class="fas fa-history me-2"></i>
        История созданных квестов
      </h3>
    </div>

    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-2">Загружаем историю квестов...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <div v-else-if="quests.length === 0" class="text-center py-4">
      <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
      <h5 class="text-muted">История пуста</h5>
      <p class="text-muted">Создайте свой первый квест!</p>
    </div>

    <div v-else class="quests-list">
      <div
        v-for="quest in quests"
        :key="quest.id"
        class="quest-item"
        @click="selectQuest(quest)"
      >
        <div class="quest-header">
          <div class="quest-info">
            <h5 class="quest-title">
              {{ quest.quest_input.genre }} - {{ quest.quest_input.hero }}
            </h5>
            <p class="quest-goal">{{ quest.quest_input.goal }}</p>
          </div>
          <div class="quest-meta">
            <span class="quest-date">
              {{ formatDate(quest.created_at) }}
            </span>
            <span class="quest-id">#{{ quest.id }}</span>
          </div>
        </div>

        <div class="quest-stats">
          <div class="stat-item">
            <i class="fas fa-film me-1"></i>
            <span>{{ getSceneCount(quest.quest_data) }} сцен</span>
          </div>
          <div class="stat-item">
            <i class="fas fa-code-branch me-1"></i>
            <span>{{ getBranchCount(quest.quest_data) }} веток</span>
          </div>
          <div class="stat-item">
            <i class="fas fa-route me-1"></i>
            <span>Глубина: {{ getMaxDepth(quest.quest_data) }}</span>
          </div>
        </div>

        <div class="quest-actions">
          <button
            class="btn btn-sm btn-outline-primary"
            @click.stop="viewQuest(quest)"
          >
            <i class="fas fa-eye me-1"></i>
            Просмотр
          </button>
          <button
            class="btn btn-sm btn-outline-success"
            @click.stop="downloadQuest(quest)"
          >
            <i class="fas fa-download me-1"></i>
            Скачать
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для просмотра квеста -->
    <div
      v-if="selectedQuest"
      class="modal fade show d-block"
      tabindex="-1"
      style="background: rgba(0, 0, 0, 0.5)"
    >
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-eye me-2"></i>
              Просмотр квеста
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="selectedQuest = null"
            ></button>
          </div>
          <div class="modal-body">
            <div class="quest-details">
              <div class="quest-info-card mb-4">
                <h6>Информация о квесте</h6>
                <div class="row">
                  <div class="col-md-4">
                    <strong>Жанр:</strong> {{ selectedQuest.quest_input.genre }}
                  </div>
                  <div class="col-md-4">
                    <strong>Герой:</strong> {{ selectedQuest.quest_input.hero }}
                  </div>
                  <div class="col-md-4">
                    <strong>Цель:</strong> {{ selectedQuest.quest_input.goal }}
                  </div>
                </div>
                <div class="row mt-2">
                  <div class="col-md-6">
                    <strong>Создан:</strong>
                    {{ formatDate(selectedQuest.created_at) }}
                  </div>
                  <div class="col-md-6">
                    <strong>Файл:</strong>
                    {{ selectedQuest.saved_file || "Не сохранен" }}
                  </div>
                </div>
              </div>

              <!-- Граф квеста -->
              <QuestGraph
                :quest="getParsedQuestData(selectedQuest.quest_data)"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="selectedQuest = null"
            >
              Закрыть
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="downloadQuest(selectedQuest)"
            >
              <i class="fas fa-download me-1"></i>
              Скачать JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import QuestGraph from "./QuestGraph.vue";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const quests = ref([]);
const loading = ref(false);
const error = ref(null);
const selectedQuest = ref(null);

// Загружаем историю квестов
const loadQuests = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await axios.get(`${API_BASE_URL}/quests/`);
    quests.value = response.data;
  } catch (err) {
    error.value = "Ошибка загрузки истории квестов";
    console.error("Error loading quests:", err);
  } finally {
    loading.value = false;
  }
};

// Форматируем дату
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Подсчитываем количество веток
const getBranchCount = (questData) => {
  if (!questData) return 0;

  // Если questData - строка, парсим её
  let parsedData = questData;
  if (typeof questData === "string") {
    try {
      parsedData = JSON.parse(questData);
    } catch (e) {
      console.error("Error parsing quest data:", e);
      return 0;
    }
  }

  if (!parsedData || !parsedData.scenes) return 0;

  let branches = 0;
  for (const scene of parsedData.scenes) {
    if (scene.choices && scene.choices.length > 1) {
      branches++;
    }
  }
  return branches;
};

// Вычисляем максимальную глубину
const getMaxDepth = (questData) => {
  if (!questData) return 0;

  // Если questData - строка, парсим её
  let parsedData = questData;
  if (typeof questData === "string") {
    try {
      parsedData = JSON.parse(questData);
    } catch (e) {
      console.error("Error parsing quest data:", e);
      return 0;
    }
  }

  if (!parsedData || !parsedData.scenes) return 0;

  const calculateDepth = (sceneId, visited = new Set()) => {
    if (visited.has(sceneId) || sceneId === "quest_end") {
      return 0;
    }

    visited.add(sceneId);
    const scene = parsedData.scenes.find((s) => s.scene_id === sceneId);

    if (!scene) {
      return 0;
    }

    let maxDepth = 0;
    for (const choice of scene.choices || []) {
      if (choice.next_scene !== "quest_end") {
        const depth = calculateDepth(choice.next_scene, new Set(visited));
        maxDepth = Math.max(maxDepth, depth);
      }
    }

    return maxDepth + 1;
  };

  return calculateDepth("scene_1");
};

// Получаем количество сцен
const getSceneCount = (questData) => {
  if (!questData) return 0;

  // Если questData - строка, парсим её
  let parsedData = questData;
  if (typeof questData === "string") {
    try {
      parsedData = JSON.parse(questData);
    } catch (e) {
      console.error("Error parsing quest data:", e);
      return 0;
    }
  }

  return parsedData?.scenes?.length || 0;
};

// Получаем распарсенные данные квеста для QuestGraph
const getParsedQuestData = (questData) => {
  if (!questData) return null;

  // Если questData - строка, парсим её
  if (typeof questData === "string") {
    try {
      return JSON.parse(questData);
    } catch (e) {
      console.error("Error parsing quest data:", e);
      return null;
    }
  }

  return questData;
};

// Выбираем квест для просмотра
const selectQuest = (quest) => {
  selectedQuest.value = quest;
};

// Просматриваем квест
const viewQuest = (quest) => {
  selectedQuest.value = quest;
};

// Скачиваем квест
const downloadQuest = (quest) => {
  const questData = {
    metadata: {
      id: quest.id,
      genre: quest.quest_input.genre,
      hero: quest.quest_input.hero,
      goal: quest.quest_input.goal,
      created_at: quest.created_at,
      saved_file: quest.saved_file,
    },
    quest_data: getParsedQuestData(quest.quest_data),
  };

  const blob = new Blob([JSON.stringify(questData, null, 2)], {
    type: "application/json",
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `quest_${quest.id}_${quest.quest_input.genre}_${quest.quest_input.hero}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

onMounted(() => {
  loadQuests();
});
</script>

<style scoped>
.quest-history {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.quests-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quest-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quest-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.quest-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.quest-title {
  margin: 0;
  color: #495057;
  font-size: 1.1em;
}

.quest-goal {
  margin: 5px 0 0 0;
  color: #6c757d;
  font-size: 0.9em;
}

.quest-meta {
  text-align: right;
  font-size: 0.8em;
}

.quest-date {
  display: block;
  color: #6c757d;
  margin-bottom: 5px;
}

.quest-id {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: bold;
}

.quest-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  font-size: 0.9em;
  color: #6c757d;
}

.quest-actions {
  display: flex;
  gap: 10px;
}

.quest-info-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #667eea;
}

.modal {
  z-index: 1050;
}

.modal-dialog {
  max-width: 90%;
}

@media (max-width: 768px) {
  .quest-header {
    flex-direction: column;
    gap: 10px;
  }

  .quest-meta {
    text-align: left;
  }

  .quest-stats {
    flex-direction: column;
    gap: 10px;
  }

  .quest-actions {
    flex-direction: column;
  }
}
</style>
