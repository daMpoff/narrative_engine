<template>
  <div class="quest-graph">
    <div class="graph-header">
      <h3 class="mb-3">
        <i class="fas fa-project-diagram me-2"></i>
        Граф путей квеста
      </h3>
    </div>

    <div class="graph-container" ref="graphContainer">
      <div class="graph-nodes">
        <div
          v-for="scene in getParsedQuest()?.scenes || []"
          :key="scene.scene_id"
          class="graph-node"
          :class="getNodeClass(scene.scene_id)"
          :style="getNodeStyle(scene.scene_id)"
          @mousedown="startDrag(scene.scene_id, $event)"
          @click="selectNode(scene.scene_id)"
        >
          <div class="node-header">
            <div class="node-title">
              <span class="node-icon">{{ getSceneIcon(scene.scene_id) }}</span>
              <span class="node-name">{{
                formatSceneName(scene.scene_id)
              }}</span>
            </div>
            <span class="node-number">{{
              getSceneNumber(scene.scene_id)
            }}</span>
          </div>

          <!-- Краткое описание сцены -->
          <div class="node-description">
            {{ getShortDescription(scene.text) }}
          </div>

          <div class="node-choices">
            <div class="choices-header">
              <i class="fas fa-directions"></i>
              <span>Выборы ({{ (scene.choices || []).length }})</span>
            </div>
            <div
              v-for="(choice, index) in scene.choices || []"
              :key="index"
              class="choice-item"
              :class="{
                'active-path': isActivePath(scene.scene_id, choice.next_scene),
                'final-choice': choice.next_scene === 'quest_end',
              }"
            >
              <div class="choice-content">
                <span class="choice-number">{{ index + 1 }}</span>
                <span class="choice-text">{{ choice.text }}</span>
              </div>
              <div class="choice-arrow-container">
                <i class="fas fa-long-arrow-alt-right choice-arrow"></i>
                <span class="choice-target">{{
                  formatSceneName(choice.next_scene)
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Улучшенные соединительные линии -->
      <svg class="graph-lines" :width="graphWidth" :height="graphHeight">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="12"
            markerHeight="8"
            refX="10"
            refY="4"
            orient="auto"
          >
            <polygon points="0 0, 12 4, 0 8" fill="#667eea" />
          </marker>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path
          v-for="connection in connections"
          :key="connection.id"
          :d="connection.path"
          stroke="#667eea"
          stroke-width="3"
          fill="none"
          marker-end="url(#arrowhead)"
          :class="{ 'active-connection': connection.isActive }"
          filter="url(#glow)"
        />
      </svg>
    </div>

    <!-- Информация о путях -->
    <div class="paths-info mt-4">
      <h5 class="text-primary mb-3">
        <i class="fas fa-route me-2"></i>
        Анализ путей
      </h5>
      <div class="row">
        <div class="col-md-6">
          <div class="path-stat">
            <strong>Всего сцен:</strong>
            {{ getParsedQuest()?.scenes?.length || 0 }}
          </div>
          <div class="path-stat">
            <strong>Максимальная глубина:</strong> {{ maxDepth }}
          </div>
        </div>
        <div class="col-md-6">
          <div class="path-stat">
            <strong>Количество веток:</strong> {{ branchCount }}
          </div>
          <div class="path-stat">
            <strong>Средняя длина пути:</strong> {{ averagePathLength }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";

const props = defineProps({
  quest: {
    type: [Object, String],
    required: true,
  },
});

const graphContainer = ref(null);
const graphWidth = ref(1200);
const graphHeight = ref(800);
const selectedNode = ref(null);
const draggingNode = ref(null);
const nodePositions = ref({});
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });

// Получаем распарсенные данные квеста
const getParsedQuest = () => {
  if (!props.quest) return null;

  // Если quest - строка, парсим её
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

// Инициализируем позиции узлов
const initializeNodePositions = () => {
  const quest = getParsedQuest();
  if (!quest?.scenes) return;

  const positions = {};
  quest.scenes.forEach((scene, index) => {
    const row = Math.floor(index / 3);
    const col = index % 3;
    positions[scene.scene_id] = {
      x: 200 + col * 300,
      y: 150 + row * 200,
    };
  });
  nodePositions.value = positions;
};

// Получаем стиль узла
const getNodeStyle = (sceneId) => {
  const pos = nodePositions.value[sceneId];
  if (!pos) return {};

  return {
    position: "absolute",
    left: `${pos.x}px`,
    top: `${pos.y}px`,
    transform:
      isDragging.value && draggingNode.value === sceneId
        ? "scale(1.05)"
        : "scale(1)",
    zIndex: isDragging.value && draggingNode.value === sceneId ? 1000 : 1,
  };
};

// Начинаем перетаскивание
const startDrag = (sceneId, event) => {
  event.preventDefault();
  isDragging.value = true;
  draggingNode.value = sceneId;

  const pos = nodePositions.value[sceneId];
  if (pos) {
    dragOffset.value = {
      x: event.clientX - pos.x,
      y: event.clientY - pos.y,
    };
  }

  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", stopDrag);
};

// Перетаскивание
const onDrag = (event) => {
  if (!isDragging.value || !draggingNode.value) return;

  const newX = event.clientX - dragOffset.value.x;
  const newY = event.clientY - dragOffset.value.y;

  nodePositions.value[draggingNode.value] = {
    x: Math.max(0, Math.min(graphWidth.value - 280, newX)),
    y: Math.max(0, Math.min(graphHeight.value - 150, newY)),
  };
};

// Останавливаем перетаскивание
const stopDrag = () => {
  isDragging.value = false;
  draggingNode.value = null;
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopDrag);
};

// Вычисляем статистику путей
const maxDepth = computed(() => {
  return calculateMaxDepth("scene_1", new Set());
});

const branchCount = computed(() => {
  return countBranches();
});

const averagePathLength = computed(() => {
  const paths = getAllPaths();
  if (paths.length === 0) return 0;
  const totalLength = paths.reduce((sum, path) => sum + path.length, 0);
  return Math.round((totalLength / paths.length) * 10) / 10;
});

// Получаем номер сцены
const getSceneNumber = (sceneId) => {
  const match = sceneId.match(/scene_(\d+)/);
  return match ? match[1] : sceneId;
};

// Получаем CSS класс для узла
const getNodeClass = (sceneId) => {
  const classes = ["graph-node"];
  if (selectedNode.value === sceneId) {
    classes.push("selected");
  }
  if (sceneId === "start") {
    classes.push("start-node");
  }
  if (sceneId === "quest_end") {
    classes.push("end-node");
  }
  if (isDragging.value && draggingNode.value === sceneId) {
    classes.push("dragging");
  }
  return classes.join(" ");
};

// Форматируем название сцены для отображения
const formatSceneName = (sceneId) => {
  if (!sceneId) return "";

  // Заменяем подчеркивания на пробелы и делаем первую букву заглавной
  return sceneId
    .replace(/_/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase())
    .replace(/Quest End/i, "Конец квеста")
    .replace(/Start/i, "Начало");
};

// Получаем иконку для сцены
const getSceneIcon = (sceneId) => {
  if (sceneId === "start") return "🚀";
  if (sceneId === "quest_end") return "🏁";

  // Иконки по ключевым словам
  const iconMap = {
    forest: "🌲",
    dark: "🌙",
    ancient: "🏛️",
    temple: "⛩️",
    battle: "⚔️",
    fight: "⚔️",
    combat: "⚔️",
    attack: "⚔️",
    search: "🔍",
    find: "🔍",
    explore: "🗺️",
    investigate: "🕵️",
    treasure: "💰",
    artifact: "💎",
    magic: "✨",
    spell: "🔮",
    dragon: "🐉",
    boss: "👹",
    enemy: "👾",
    monster: "👹",
    castle: "🏰",
    tower: "🗼",
    cave: "🏔️",
    dungeon: "⚫",
    river: "🌊",
    bridge: "🌉",
    mountain: "⛰️",
    village: "🏘️",
    wizard: "🧙",
    guard: "💂",
    merchant: "🤵",
    ally: "🤝",
    door: "🚪",
    key: "🗝️",
    lock: "🔒",
    trap: "🕳️",
    heal: "💚",
    poison: "☠️",
    wound: "🩸",
    rest: "😴",
  };

  for (const [keyword, icon] of Object.entries(iconMap)) {
    if (sceneId.toLowerCase().includes(keyword)) {
      return icon;
    }
  }

  return "📍"; // Иконка по умолчанию
};

// Получаем краткое описание сцены
const getShortDescription = (text) => {
  if (!text) return "Без описания";

  // Берем первые 100 символов и добавляем многоточие
  if (text.length <= 100) return text;

  const truncated = text.substring(0, 100);
  const lastSpace = truncated.lastIndexOf(" ");

  return lastSpace > 50
    ? truncated.substring(0, lastSpace) + "..."
    : truncated + "...";
};

// Выбираем узел
const selectNode = (sceneId) => {
  if (isDragging.value) return;
  selectedNode.value = selectedNode.value === sceneId ? null : sceneId;
};

// Проверяем активный путь
const isActivePath = (fromScene, toScene) => {
  return selectedNode.value === fromScene;
};

// Вычисляем максимальную глубину
const calculateMaxDepth = (sceneId, visited) => {
  if (visited.has(sceneId) || sceneId === "quest_end") {
    return 0;
  }

  visited.add(sceneId);
  const quest = getParsedQuest();
  if (!quest) return 0;

  const scene = quest.scenes?.find((s) => s.scene_id === sceneId);

  if (!scene) {
    return 0;
  }

  let maxDepth = 0;
  for (const choice of scene.choices || []) {
    if (choice.next_scene !== "quest_end") {
      const depth = calculateMaxDepth(choice.next_scene, new Set(visited));
      maxDepth = Math.max(maxDepth, depth);
    }
  }

  return maxDepth + 1;
};

// Подсчитываем количество веток
const countBranches = () => {
  const quest = getParsedQuest();
  if (!quest?.scenes) return 0;

  let branches = 0;
  for (const scene of quest.scenes) {
    if (scene.choices && scene.choices.length > 1) {
      branches++;
    }
  }
  return branches;
};

// Получаем все пути
const getAllPaths = () => {
  const quest = getParsedQuest();
  if (!quest?.scenes) return [];

  const paths = [];

  const findPaths = (currentPath, sceneId) => {
    if (sceneId === "quest_end") {
      paths.push([...currentPath]);
      return;
    }

    const scene = quest.scenes.find((s) => s.scene_id === sceneId);
    if (!scene) return;

    currentPath.push(sceneId);

    for (const choice of scene.choices || []) {
      findPaths([...currentPath], choice.next_scene);
    }
  };

  findPaths([], "scene_1");
  return paths;
};

// Вычисляем соединения для графа
const connections = computed(() => {
  const quest = getParsedQuest();
  if (!quest?.scenes) return [];

  const connections = [];

  for (const scene of quest.scenes) {
    const fromNode = getNodePosition(scene.scene_id);

    for (const choice of scene.choices || []) {
      const toNode = getNodePosition(choice.next_scene);

      if (fromNode && toNode) {
        connections.push({
          id: `${scene.scene_id}-${choice.next_scene}`,
          path: createPath(fromNode, toNode),
          isActive: selectedNode.value === scene.scene_id,
        });
      }
    }
  }

  return connections;
});

// Получаем позицию узла
const getNodePosition = (sceneId) => {
  const pos = nodePositions.value[sceneId];
  if (!pos) return null;

  return {
    x: pos.x + 140, // центр узла
    y: pos.y + 75,
  };
};

// Создаем путь между узлами с улучшенной кривизной
const createPath = (from, to) => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Создаем более плавную кривую
  const controlPoint1 = {
    x: from.x + dx * 0.25,
    y: from.y,
  };
  const controlPoint2 = {
    x: to.x - dx * 0.25,
    y: to.y,
  };

  return `M ${from.x} ${from.y} C ${controlPoint1.x} ${controlPoint1.y}, ${controlPoint2.x} ${controlPoint2.y}, ${to.x} ${to.y}`;
};

// Обновляем размеры графа
const updateGraphSize = () => {
  if (graphContainer.value) {
    const rect = graphContainer.value.getBoundingClientRect();
    graphWidth.value = Math.max(1200, rect.width);
    const quest = getParsedQuest();
    graphHeight.value = Math.max(800, (quest?.scenes?.length || 0) * 150);
  }
};

onMounted(() => {
  initializeNodePositions();
  updateGraphSize();
  window.addEventListener("resize", updateGraphSize);
});

watch(
  () => props.quest,
  () => {
    initializeNodePositions();
    updateGraphSize();
  },
  { deep: true }
);
</script>

<style scoped>
.quest-graph {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.graph-container {
  position: relative;
  overflow: auto;
  min-height: 600px;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  cursor: grab;
}

.graph-container:active {
  cursor: grabbing;
}

.graph-nodes {
  position: relative;
  z-index: 2;
  padding: 20px;
  min-height: 600px;
}

.graph-lines {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: none;
}

.graph-node {
  background: white;
  border: 3px solid #dee2e6;
  border-radius: 15px;
  padding: 20px;
  width: 320px;
  cursor: grab;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  user-select: none;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.graph-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.graph-node.selected {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}

.graph-node.dragging {
  cursor: grabbing;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.graph-node.start-node {
  border-color: #28a745;
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
}

.graph-node.end-node {
  border-color: #dc3545;
  background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.node-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-icon {
  font-size: 1.2em;
  width: 24px;
  text-align: center;
}

.node-name {
  font-weight: bold;
  color: #495057;
  font-size: 0.95em;
  line-height: 1.2;
}

.node-description {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 15px;
  font-size: 0.85em;
  color: #6c757d;
  line-height: 1.4;
  border-left: 3px solid #007bff;
}

.node-number {
  background: #667eea;
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.9em;
  font-weight: bold;
}

.node-choices {
  margin-top: 10px;
}

.choices-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #495057;
  font-weight: 600;
  font-size: 0.9em;
}

.choices-header i {
  color: #007bff;
}

.choice-item {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 12px;
  margin: 8px 0;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.choice-item:hover {
  background: #e9ecef;
  transform: translateX(3px);
  border-color: #007bff20;
}

.choice-item.active-path {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.choice-item.final-choice {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border-color: #28a745;
}

.choice-content {
  display: flex;
  align-items: center;
  gap: 10px;
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
  flex-shrink: 0;
}

.choice-item.active-path .choice-number,
.choice-item.final-choice .choice-number {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.choice-text {
  flex: 1;
  font-size: 0.9em;
  line-height: 1.4;
  font-weight: 500;
}

.choice-arrow-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 34px;
}

.choice-arrow {
  color: #6c757d;
  font-size: 1em;
  flex-shrink: 0;
}

.choice-item.active-path .choice-arrow,
.choice-item.final-choice .choice-arrow {
  color: rgba(255, 255, 255, 0.8);
}

.choice-target {
  font-size: 0.85em;
  color: #6c757d;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.05);
  padding: 4px 8px;
  border-radius: 6px;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.choice-item.active-path .choice-target,
.choice-item.final-choice .choice-target {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.2);
}

.paths-info {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.path-stat {
  margin-bottom: 10px;
  padding: 10px 15px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.active-connection {
  stroke: #2196f3;
  stroke-width: 4;
  filter: url(#glow);
}

@media (max-width: 768px) {
  .graph-node {
    width: 100%;
    margin: 5px 0;
  }

  .graph-container {
    overflow-x: auto;
  }
}
</style>
