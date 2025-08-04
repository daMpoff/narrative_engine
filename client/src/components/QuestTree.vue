<template>
  <div class="quest-tree">
    <div class="tree-header">
      <h3 class="mb-3">
        <i class="fas fa-sitemap me-2"></i>
        Дерево квеста
      </h3>
      <p class="text-muted mb-4">Нажмите на узел для просмотра деталей сцены</p>
    </div>

    <div class="tree-container">
      <!-- Навигация по дереву -->
      <div class="tree-navigation">
        <div class="row">
          <div class="col-md-8">
            <!-- Дерево узлов -->
            <div class="tree-nodes">
              <div
                v-for="scene in getTreeData()"
                :key="scene.scene_id"
                class="tree-node"
                :class="{
                  selected: selectedNode === scene.scene_id,
                  'start-node': scene.scene_id === 'start',
                  'end-node': scene.scene_id === 'quest_end',
                }"
                @click="selectNode(scene.scene_id)"
              >
                <div class="node-content">
                  <div class="node-header">
                    <span class="node-icon">{{
                      getSceneIcon(scene.scene_id)
                    }}</span>
                    <span class="node-title">{{
                      formatSceneName(scene.scene_id)
                    }}</span>
                    <span class="node-badge">{{
                      scene.choices?.length || 0
                    }}</span>
                  </div>

                  <!-- Краткое описание -->
                  <div class="node-summary">
                    {{ getShortText(scene.text) }}
                  </div>

                  <!-- Связи -->
                  <div
                    v-if="scene.choices && scene.choices.length > 0"
                    class="node-connections"
                  >
                    <div class="connections-header">
                      <i class="fas fa-arrow-right me-1"></i>
                      <span>Ведет к:</span>
                    </div>
                    <div class="connections-list">
                      <span
                        v-for="choice in scene.choices"
                        :key="choice.next_scene"
                        class="connection-item"
                        @click.stop="selectNode(choice.next_scene)"
                      >
                        {{ formatSceneName(choice.next_scene) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <!-- Панель деталей -->
            <div class="details-panel">
              <div v-if="selectedNode" class="node-details">
                <div class="details-header">
                  <h5>
                    <span class="me-2">{{ getSceneIcon(selectedNode) }}</span>
                    {{ formatSceneName(selectedNode) }}
                  </h5>
                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="selectedNode = null"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>

                <div class="details-content">
                  <!-- Вкладки для разных видов отображения -->
                  <div class="details-tabs">
                    <ul class="nav nav-pills nav-sm">
                      <li class="nav-item">
                        <a
                          class="nav-link"
                          :class="{ active: detailsTab === 'formatted' }"
                          @click="detailsTab = 'formatted'"
                        >
                          <i class="fas fa-eye me-1"></i>
                          Читаемый вид
                        </a>
                      </li>
                      <li class="nav-item">
                        <a
                          class="nav-link"
                          :class="{ active: detailsTab === 'json' }"
                          @click="detailsTab = 'json'"
                        >
                          <i class="fas fa-code me-1"></i>
                          JSON
                        </a>
                      </li>
                    </ul>
                  </div>

                  <!-- Содержимое вкладок -->
                  <div class="tab-content mt-3">
                    <!-- Читаемый вид -->
                    <div
                      v-if="detailsTab === 'formatted'"
                      class="formatted-view"
                    >
                      <div class="scene-info">
                        <div class="info-item">
                          <strong>ID сцены:</strong>
                          <span class="scene-id">{{
                            selectedSceneData?.scene_id
                          }}</span>
                        </div>

                        <div class="info-item">
                          <strong>Описание:</strong>
                          <div class="scene-text">
                            {{ selectedSceneData?.text }}
                          </div>
                        </div>

                        <div
                          v-if="selectedSceneData?.choices?.length"
                          class="info-item"
                        >
                          <strong>Варианты выбора:</strong>
                          <div class="choices-list">
                            <div
                              v-for="(
                                choice, index
                              ) in selectedSceneData.choices"
                              :key="index"
                              class="choice-card"
                            >
                              <div class="choice-header">
                                <span class="choice-number">{{
                                  index + 1
                                }}</span>
                                <span class="choice-text">{{
                                  choice.text
                                }}</span>
                              </div>
                              <div class="choice-target">
                                <i class="fas fa-arrow-right me-1"></i>
                                <span
                                  @click="selectNode(choice.next_scene)"
                                  class="target-link"
                                >
                                  {{ formatSceneName(choice.next_scene) }}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- JSON вид -->
                    <div v-if="detailsTab === 'json'" class="json-view">
                      <div class="json-header">
                        <button
                          class="btn btn-sm btn-outline-primary"
                          @click="copyToClipboard"
                        >
                          <i class="fas fa-copy me-1"></i>
                          Копировать
                        </button>
                      </div>
                      <pre class="json-code">{{
                        formatJson(selectedSceneData)
                      }}</pre>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Пустое состояние -->
              <div v-else class="empty-details">
                <div class="empty-icon">
                  <i class="fas fa-mouse-pointer fa-3x"></i>
                </div>
                <h6>Выберите узел</h6>
                <p class="text-muted">
                  Нажмите на любой узел слева, чтобы увидеть детали сцены
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Статистика -->
    <div class="tree-stats mt-4">
      <div class="row">
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-list"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ totalScenes }}</div>
              <div class="stat-label">Всего сцен</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-route"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ totalChoices }}</div>
              <div class="stat-label">Всего выборов</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-code-branch"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ branchingNodes }}</div>
              <div class="stat-label">Узлов с ветвлением</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-flag-checkered"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ endNodes }}</div>
              <div class="stat-label">Финальных узлов</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
  quest: {
    type: [Object, String],
    required: true,
  },
});

const selectedNode = ref(null);
const detailsTab = ref("formatted");

// Получаем распарсенные данные квеста
const getParsedQuest = () => {
  if (!props.quest) return null;

  if (typeof props.quest === "string") {
    try {
      return JSON.parse(props.quest);
    } catch (e) {
      console.error("Error parsing quest data:", e);
      return null;
    }
  }

  return props.quest;
};

// Получаем данные для дерева
const getTreeData = () => {
  const quest = getParsedQuest();
  return quest?.scenes || [];
};

// Получаем данные выбранной сцены
const selectedSceneData = computed(() => {
  if (!selectedNode.value) return null;
  const scenes = getTreeData();
  return scenes.find((scene) => scene.scene_id === selectedNode.value);
});

// Выбираем узел
const selectNode = (sceneId) => {
  selectedNode.value = sceneId;
  detailsTab.value = "formatted";
};

// Форматируем название сцены
const formatSceneName = (sceneId) => {
  if (!sceneId) return "";

  if (sceneId === "start") return "Начало";
  if (sceneId === "quest_end") return "Конец квеста";

  return sceneId
    .replace(/_/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
};

// Получаем иконку для сцены
const getSceneIcon = (sceneId) => {
  if (sceneId === "start") return "🚀";
  if (sceneId === "quest_end") return "🏁";

  const iconMap = {
    neon: "🌃",
    city: "🏙️",
    street: "🛣️",
    underground: "🚇",
    market: "🛒",
    hack: "💻",
    security: "🔒",
    system: "⚙️",
    informant: "🕵️",
    meet: "🤝",
    escape: "🏃",
    chase: "🏃‍♂️",
    danger: "⚠️",
    success: "✅",
    failure: "❌",
    choice: "🤔",
    battle: "⚔️",
    stealth: "🥷",
    corporate: "🏢",
    data: "💾",
    network: "🌐",
    server: "🖥️",
  };

  for (const [keyword, icon] of Object.entries(iconMap)) {
    if (sceneId.toLowerCase().includes(keyword)) {
      return icon;
    }
  }

  return "📍";
};

// Получаем краткий текст
const getShortText = (text) => {
  if (!text) return "Без описания";
  return text.length > 80 ? text.substring(0, 80) + "..." : text;
};

// Форматируем JSON для отображения
const formatJson = (data) => {
  return JSON.stringify(data, null, 2);
};

// Копируем в буфер обмена
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(formatJson(selectedSceneData.value));
    // Можно добавить уведомление об успешном копировании
  } catch (err) {
    console.error("Failed to copy: ", err);
  }
};

// Статистика
const totalScenes = computed(() => getTreeData().length);

const totalChoices = computed(() => {
  return getTreeData().reduce((total, scene) => {
    return total + (scene.choices?.length || 0);
  }, 0);
});

const branchingNodes = computed(() => {
  return getTreeData().filter(
    (scene) => scene.choices && scene.choices.length > 1
  ).length;
});

const endNodes = computed(() => {
  const scenes = getTreeData();
  return scenes.filter(
    (scene) =>
      !scene.choices ||
      scene.choices.length === 0 ||
      scene.choices.some((choice) => choice.next_scene === "quest_end")
  ).length;
});

// Сброс выбора при изменении квеста
watch(
  () => props.quest,
  () => {
    selectedNode.value = null;
  }
);
</script>

<style scoped>
.quest-tree {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tree-container {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  min-height: 600px;
}

.tree-nodes {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.tree-node {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  margin-bottom: 15px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tree-node:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tree-node.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.tree-node.start-node {
  border-color: #28a745;
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
}

.tree-node.end-node {
  border-color: #dc3545;
  background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
}

.tree-node.selected.start-node,
.tree-node.selected.end-node {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.node-content {
  width: 100%;
}

.node-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.node-icon {
  font-size: 1.2em;
  margin-right: 8px;
}

.node-title {
  font-weight: 600;
  flex: 1;
}

.node-badge {
  background: #007bff;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: bold;
}

.tree-node.selected .node-badge {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.node-summary {
  font-size: 0.9em;
  color: #6c757d;
  margin-bottom: 10px;
  line-height: 1.4;
}

.tree-node.selected .node-summary {
  color: rgba(255, 255, 255, 0.9);
}

.node-connections {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e9ecef;
}

.tree-node.selected .node-connections {
  border-color: rgba(255, 255, 255, 0.3);
}

.connections-header {
  font-size: 0.8em;
  color: #6c757d;
  margin-bottom: 5px;
  font-weight: 600;
}

.tree-node.selected .connections-header {
  color: rgba(255, 255, 255, 0.8);
}

.connections-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.connection-item {
  background: #e9ecef;
  color: #495057;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.2s ease;
}

.connection-item:hover {
  background: #667eea;
  color: white;
}

.tree-node.selected .connection-item {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.tree-node.selected .connection-item:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.details-panel {
  background: white;
  border-radius: 10px;
  padding: 20px;
  height: 500px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e9ecef;
}

.details-header h5 {
  margin: 0;
  color: #495057;
  font-weight: 600;
}

.details-tabs .nav-link {
  font-size: 0.9em;
  padding: 8px 12px;
  border-radius: 6px;
  margin-right: 5px;
}

.formatted-view {
  padding: 10px 0;
}

.info-item {
  margin-bottom: 20px;
}

.info-item strong {
  color: #495057;
  display: block;
  margin-bottom: 8px;
}

.scene-id {
  font-family: "Courier New", monospace;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  color: #495057;
}

.scene-text {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  line-height: 1.6;
  color: #495057;
}

.choices-list {
  margin-top: 10px;
}

.choice-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}

.choice-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.choice-number {
  background: #007bff;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: bold;
  margin-right: 10px;
}

.choice-text {
  flex: 1;
  font-weight: 500;
  color: #495057;
}

.choice-target {
  display: flex;
  align-items: center;
  font-size: 0.9em;
  color: #6c757d;
}

.target-link {
  color: #007bff;
  cursor: pointer;
  text-decoration: underline;
}

.target-link:hover {
  color: #0056b3;
}

.json-view {
  padding: 10px 0;
}

.json-header {
  margin-bottom: 15px;
}

.json-code {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  font-size: 0.85em;
  line-height: 1.4;
  max-height: 350px;
  overflow-y: auto;
  color: #495057;
}

.empty-details {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-icon {
  margin-bottom: 20px;
  opacity: 0.5;
}

.tree-stats {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 1.2em;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.8em;
  font-weight: bold;
  color: #495057;
  line-height: 1;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9em;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .tree-container .row {
    flex-direction: column;
  }

  .details-panel {
    margin-top: 20px;
    height: auto;
  }
}
</style>
