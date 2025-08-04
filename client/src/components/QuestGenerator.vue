<template>
  <div class="quest-generator">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8 text-center">
            <h1 class="display-3 fw-bold text-white mb-4">
              🎮 Генератор квестов
            </h1>
            <p class="lead text-white-50 mb-5">
              Создавайте увлекательные текстовые квесты с помощью ИИ
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-lg-12">
          <!-- Navigation Tabs -->
          <ul class="nav nav-tabs mb-4" id="questTabs" role="tablist">
            <li class="nav-item" role="presentation">
              <button
                class="nav-link active"
                id="generator-tab"
                data-bs-toggle="tab"
                data-bs-target="#generator"
                type="button"
                role="tab"
              >
                <i class="fas fa-magic me-2"></i>
                Создать квест
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="tree-tab"
                data-bs-toggle="tab"
                data-bs-target="#tree"
                type="button"
                role="tab"
                :disabled="!quest"
              >
                <i class="fas fa-sitemap me-2"></i>
                Дерево
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="graph-tab"
                data-bs-toggle="tab"
                data-bs-target="#graph"
                type="button"
                role="tab"
                :disabled="!quest"
              >
                <i class="fas fa-project-diagram me-2"></i>
                Граф путей
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="history-tab"
                data-bs-toggle="tab"
                data-bs-target="#history"
                type="button"
                role="tab"
              >
                <i class="fas fa-history me-2"></i>
                История
              </button>
            </li>
          </ul>

          <!-- Tab Content -->
          <div class="tab-content" id="questTabsContent">
            <!-- Generator Tab -->
            <div
              class="tab-pane fade show active"
              id="generator"
              role="tabpanel"
            >
              <!-- Form Card -->
              <div class="card shadow-lg border-0">
                <div class="card-header bg-primary text-white">
                  <h2 class="mb-0">
                    <i class="fas fa-magic me-2"></i>
                    Создать новый квест
                  </h2>
                </div>
                <div class="card-body p-4">
                  <!-- Загрузка файла -->
                  <div class="mb-4">
                    <div class="card border-success">
                      <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                          <i class="fas fa-file-upload me-2"></i>
                          Загрузить данные из файла
                        </h5>
                      </div>
                      <div class="card-body">
                        <div class="row">
                          <div class="col-md-8 mb-3">
                            <label for="txtFile" class="form-label">
                              <i class="fas fa-file-alt me-2"></i>
                              Выберите .txt файл с описанием квеста
                            </label>
                            <input
                              id="txtFile"
                              ref="fileInput"
                              type="file"
                              accept=".txt"
                              class="form-control"
                              @change="handleFileUpload"
                            />
                            <small class="text-muted">
                              Файл должен содержать: жанр, главного героя и цель
                              квеста
                            </small>
                          </div>
                          <div class="col-md-4 d-flex align-items-end">
                            <button
                              type="button"
                              :disabled="!selectedFile || parseLoading"
                              class="btn btn-success w-100"
                              @click="parseFile"
                            >
                              <span
                                v-if="parseLoading"
                                class="spinner-border spinner-border-sm me-2"
                              ></span>
                              <i v-else class="fas fa-upload me-2"></i>
                              {{
                                parseLoading
                                  ? "Обрабатываем..."
                                  : "Загрузить данные"
                              }}
                            </button>
                          </div>
                        </div>

                        <!-- Результат парсинга -->
                        <div v-if="parseResult" class="mt-3">
                          <div
                            :class="[
                              'alert',
                              parseResult.success
                                ? 'alert-success'
                                : 'alert-warning',
                            ]"
                            role="alert"
                          >
                            <div class="d-flex align-items-center">
                              <i
                                :class="[
                                  'me-2',
                                  parseResult.success
                                    ? 'fas fa-check-circle'
                                    : 'fas fa-exclamation-triangle',
                                ]"
                              ></i>
                              <div>
                                <strong>{{
                                  parseResult.message || parseResult.warning
                                }}</strong>
                                <div v-if="parseResult.data" class="mt-2 small">
                                  <strong>Извлечено:</strong>
                                  Жанр: "{{
                                    parseResult.data.genre || "не найден"
                                  }}", Герой: "{{
                                    parseResult.data.hero || "не найден"
                                  }}", Цель: "{{
                                    parseResult.data.goal || "не найдена"
                                  }}"
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        <!-- Ошибка парсинга -->
                        <div v-if="parseError" class="mt-3">
                          <div class="alert alert-danger" role="alert">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            <strong>Ошибка:</strong> {{ parseError }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <form @submit.prevent="generateQuest">
                    <div class="row">
                      <div class="col-md-4 mb-3">
                        <label for="genre" class="form-label fw-bold">
                          <i class="fas fa-theater-masks me-2"></i>Жанр
                        </label>
                        <input
                          id="genre"
                          v-model="formData.genre"
                          type="text"
                          class="form-control form-control-lg"
                          placeholder="киберпанк, фэнтези, детектив"
                          required
                        />
                      </div>

                      <div class="col-md-4 mb-3">
                        <label for="hero" class="form-label fw-bold">
                          <i class="fas fa-user me-2"></i>Главный герой
                        </label>
                        <input
                          id="hero"
                          v-model="formData.hero"
                          type="text"
                          class="form-control form-control-lg"
                          placeholder="хакер-одиночка, рыцарь"
                          required
                        />
                      </div>

                      <div class="col-md-4 mb-3">
                        <label for="goal" class="form-label fw-bold">
                          <i class="fas fa-bullseye me-2"></i>Цель квеста
                        </label>
                        <input
                          id="goal"
                          v-model="formData.goal"
                          type="text"
                          class="form-control form-control-lg"
                          placeholder="взломать систему"
                          required
                        />
                      </div>
                    </div>

                    <!-- Настройки генерации -->
                    <div class="row mb-4">
                      <div class="col-12">
                        <div class="card border-info">
                          <div class="card-header bg-info text-white">
                            <h5 class="mb-0">
                              <i class="fas fa-cogs me-2"></i>
                              Настройки генерации
                            </h5>
                          </div>
                          <div class="card-body">
                            <div class="row">
                              <div class="col-md-6 mb-3">
                                <label
                                  for="sceneCount"
                                  class="form-label fw-bold"
                                >
                                  <i class="fas fa-film me-2"></i>Количество
                                  сцен
                                </label>
                                <div class="d-flex align-items-center">
                                  <input
                                    id="sceneCount"
                                    v-model.number="formData.sceneCount"
                                    type="range"
                                    class="form-range me-3"
                                    min="5"
                                    max="10"
                                    step="1"
                                  />
                                  <span class="badge bg-primary fs-6">{{
                                    formData.sceneCount
                                  }}</span>
                                </div>
                                <small class="text-muted"
                                  >От 5 до 10 сцен</small
                                >
                              </div>

                              <div class="col-md-6 mb-3">
                                <label
                                  for="maxDepth"
                                  class="form-label fw-bold"
                                >
                                  <i class="fas fa-route me-2"></i>Максимальная
                                  глубина
                                </label>
                                <div class="d-flex align-items-center">
                                  <input
                                    id="maxDepth"
                                    v-model.number="formData.maxDepth"
                                    type="range"
                                    class="form-range me-3"
                                    min="3"
                                    max="8"
                                    step="1"
                                  />
                                  <span class="badge bg-success fs-6">{{
                                    formData.maxDepth
                                  }}</span>
                                </div>
                                <small class="text-muted"
                                  >От 3 до 8 уровней</small
                                >
                              </div>
                            </div>

                            <div class="row">
                              <div class="col-md-6 mb-3">
                                <label
                                  for="complexity"
                                  class="form-label fw-bold"
                                >
                                  <i class="fas fa-brain me-2"></i>Сложность
                                  сюжета
                                </label>
                                <select
                                  id="complexity"
                                  v-model="formData.complexity"
                                  class="form-select"
                                >
                                  <option value="simple">Простой</option>
                                  <option value="medium">Средний</option>
                                  <option value="complex">Сложный</option>
                                  <option value="epic">Эпический</option>
                                </select>
                                <small class="text-muted"
                                  >Влияет на разнообразие сюжета</small
                                >
                              </div>

                              <div class="col-md-6 mb-3">
                                <label
                                  for="endingType"
                                  class="form-label fw-bold"
                                >
                                  <i class="fas fa-flag-checkered me-2"></i>Тип
                                  концовок
                                </label>
                                <select
                                  id="endingType"
                                  v-model="formData.endingType"
                                  class="form-select"
                                >
                                  <option value="single">Одна концовка</option>
                                  <option value="multiple">
                                    Множественные концовки
                                  </option>
                                  <option value="branching">
                                    Разветвленные концовки
                                  </option>
                                </select>
                                <small class="text-muted"
                                  >Структура финалов</small
                                >
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="text-center">
                      <button
                        type="submit"
                        :disabled="loading"
                        class="btn btn-primary btn-lg px-5 py-3"
                      >
                        <span
                          v-if="loading"
                          class="spinner-border spinner-border-sm me-2"
                        ></span>
                        <i v-else class="fas fa-dice me-2"></i>
                        {{
                          loading
                            ? "Генерируем квест..."
                            : "🎲 Генерировать квест"
                        }}
                      </button>
                    </div>
                  </form>
                </div>
              </div>

              <!-- Result Section -->
              <div v-if="quest" class="mt-5">
                <!-- Success Alert -->
                <div
                  class="alert alert-success d-flex align-items-center"
                  role="alert"
                >
                  <i class="fas fa-check-circle me-2"></i>
                  <div>
                    <h4 class="alert-heading mb-1">✅ Квест успешно создан!</h4>
                    <p class="mb-0">
                      <strong>Файл:</strong>
                      {{ quest?.saved_file || "Не сохранен" }} |
                      <strong>Папка:</strong> output/
                    </p>
                  </div>
                </div>

                <!-- Quest Display -->
                <div class="card shadow-lg border-0">
                  <div class="card-header bg-success text-white">
                    <h3 class="mb-0">
                      <i class="fas fa-book-open me-2"></i>
                      Сгенерированный квест
                    </h3>
                  </div>
                  <div class="card-body p-4">
                    <div class="row">
                      <div
                        v-for="(scene, index) in quest?.quest_data?.scenes ||
                        []"
                        :key="scene.scene_id"
                        class="col-12 mb-4"
                      >
                        <div class="card border-primary">
                          <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">
                              <i class="fas fa-play-circle me-2"></i>
                              Сцена {{ index + 1 }}: {{ scene.scene_id }}
                            </h4>
                          </div>
                          <div class="card-body">
                            <div class="scene-description mb-3">
                              <p class="lead">{{ scene.text }}</p>
                            </div>

                            <div class="choices-section">
                              <h5 class="text-primary mb-3">
                                <i class="fas fa-list me-2"></i>
                                Варианты выбора:
                              </h5>
                              <div class="row">
                                <div
                                  v-for="(
                                    choice, choiceIndex
                                  ) in scene.choices || []"
                                  :key="choiceIndex"
                                  class="col-md-6 mb-2"
                                >
                                  <div class="card border-info">
                                    <div class="card-body p-3">
                                      <div class="d-flex align-items-center">
                                        <span class="badge bg-info me-2">{{
                                          choiceIndex + 1
                                        }}</span>
                                        <span class="flex-grow-1">{{
                                          choice.text
                                        }}</span>
                                        <i
                                          class="fas fa-arrow-right text-muted"
                                        ></i>
                                        <span class="badge bg-secondary ms-2">{{
                                          choice.next_scene
                                        }}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Error Alert -->
              <div v-if="error" class="mt-4">
                <div
                  class="alert alert-danger d-flex align-items-center"
                  role="alert"
                >
                  <i class="fas fa-exclamation-triangle me-2"></i>
                  <div>
                    <h4 class="alert-heading mb-1">❌ Ошибка</h4>
                    <p class="mb-0">{{ error }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tree Tab -->
            <div class="tab-pane fade" id="tree" role="tabpanel">
              <div v-if="quest">
                <QuestTree :quest="quest.quest_data" />
              </div>
              <div v-else class="text-center py-5">
                <i class="fas fa-sitemap fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">Дерево недоступно</h5>
                <p class="text-muted">
                  Сначала создайте квест, чтобы увидеть дерево структуры
                </p>
              </div>
            </div>

            <!-- Graph Tab -->
            <div class="tab-pane fade" id="graph" role="tabpanel">
              <div v-if="quest">
                <QuestGraph :quest="quest.quest_data" />
              </div>
              <div v-else class="text-center py-5">
                <i class="fas fa-project-diagram fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">Граф недоступен</h5>
                <p class="text-muted">
                  Сначала создайте квест, чтобы увидеть граф путей
                </p>
              </div>
            </div>

            <!-- History Tab -->
            <div class="tab-pane fade" id="history" role="tabpanel">
              <QuestHistory />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import axios from "axios";
import QuestGraph from "./QuestGraph.vue";
import QuestTree from "./QuestTree.vue";
import QuestHistory from "./QuestHistory.vue";

// Ссылка на элемент загрузки файла
const fileInput = ref(null);

const API_BASE_URL = "http://127.0.0.1:8000/api";

const formData = reactive({
  genre: "киберпанк",
  hero: "хакер-одиночка",
  goal: "взломать систему безопасности",
  sceneCount: 10, // Добавляем настройки генерации
  maxDepth: 5,
  complexity: "medium",
  endingType: "single",
});

const quest = ref(null);
const loading = ref(false);
const error = ref(null);

// Переменные для работы с файлами
const selectedFile = ref(null);
const parseLoading = ref(false);
const parseResult = ref(null);
const parseError = ref(null);

// Обработка выбора файла
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  selectedFile.value = file;
  parseResult.value = null;
  parseError.value = null;

  if (file && !file.name.toLowerCase().endsWith(".txt")) {
    parseError.value = "Пожалуйста, выберите файл с расширением .txt";
    selectedFile.value = null;
    event.target.value = "";
  }
};

// Парсинг загруженного файла
const parseFile = async () => {
  if (!selectedFile.value) {
    parseError.value = "Пожалуйста, выберите файл";
    return;
  }

  parseLoading.value = true;
  parseError.value = null;
  parseResult.value = null;

  try {
    const fileFormData = new FormData();
    fileFormData.append("file", selectedFile.value);

    const response = await axios.post(
      `${API_BASE_URL}/parse-txt/`,
      fileFormData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    parseResult.value = response.data;

    // Заполняем форму данными из файла
    if (response.data.data) {
      if (response.data.data.genre) {
        formData.genre = response.data.data.genre;
      }
      if (response.data.data.hero) {
        formData.hero = response.data.data.hero;
      }
      if (response.data.data.goal) {
        formData.goal = response.data.data.goal;
      }
    }
  } catch (err) {
    parseError.value =
      err.response?.data?.error || "Ошибка при обработке файла";
  } finally {
    parseLoading.value = false;
  }
};

const generateQuest = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await axios.post(`${API_BASE_URL}/generate/`, {
      genre: formData.genre,
      hero: formData.hero,
      goal: formData.goal,
      scene_count: formData.sceneCount, // Отправляем настройки генерации
      max_depth: formData.maxDepth,
      complexity: formData.complexity,
      ending_type: formData.endingType,
    });
    quest.value = response.data;

    // Переключаемся на вкладку дерева после успешной генерации
    setTimeout(() => {
      const treeTab = document.getElementById("tree-tab");
      if (treeTab) {
        treeTab.click();
      }
    }, 1000);
  } catch (err) {
    error.value =
      err.response?.data?.error || "Произошла ошибка при генерации квеста";
  } finally {
    loading.value = false;
  }
};

// Следим за изменениями quest для обновления состояния вкладок
watch(quest, (newQuest) => {
  const treeTab = document.getElementById("tree-tab");
  const graphTab = document.getElementById("graph-tab");

  if (treeTab) {
    treeTab.disabled = !newQuest;
  }
  if (graphTab) {
    graphTab.disabled = !newQuest;
  }
});
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 0;
  margin-bottom: 30px;
}

.quest-generator {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.nav-tabs {
  border-bottom: 2px solid #dee2e6;
}

.nav-tabs .nav-link {
  border: none;
  border-bottom: 3px solid transparent;
  color: #6c757d;
  font-weight: 500;
  padding: 12px 20px;
  transition: all 0.3s ease;
}

.nav-tabs .nav-link:hover {
  border-color: #667eea;
  color: #667eea;
}

.nav-tabs .nav-link.active {
  border-color: #667eea;
  color: #667eea;
  background: transparent;
}

.nav-tabs .nav-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card {
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  border-bottom: none;
  padding: 1.5rem;
}

.form-control-lg {
  font-size: 1.1rem;
  padding: 12px 16px;
}

.btn-lg {
  font-size: 1.1rem;
  padding: 12px 30px;
}

.scene-description {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.choices-section {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
}

.alert {
  border: none;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 0;
  }

  .display-3 {
    font-size: 2.5rem;
  }

  .nav-tabs .nav-link {
    padding: 8px 12px;
    font-size: 0.9rem;
  }
}
</style>
