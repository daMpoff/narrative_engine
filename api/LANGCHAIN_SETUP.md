# Настройка LangChain для улучшенной генерации квестов

## 🚀 Преимущества LangChain

LangChain генератор предоставляет:

- **Цепочки рассуждений**: модель планирует структуру квеста поэтапно
- **Память диалога**: возможность итеративно улучшать квест
- **Структурированные выходы**: автоматическая валидация JSON
- **Retry логика**: более умная обработка ошибок
- **Промпт-инжиниринг**: более гибкие шаблоны

## 📦 Установка

### Вариант 1: Через Poetry (рекомендуется)

```bash
cd api
poetry add langchain-mistralai
poetry add langchain-core
poetry add pydantic
```

### Вариант 2: Через pip

```bash
cd api
pip install langchain-mistralai langchain-core pydantic
```

### Вариант 3: Если langchain-mistralai недоступен

```bash
cd api
poetry add langchain-community
# или
pip install langchain-community
```

## 🔧 Проверка установки

После установки перезапустите сервер Django:

```bash
cd api/src
python manage.py runserver
```

В логах вы должны увидеть:

```
LangChain Quest Generator настроен успешно
🚀 Используем LangChain генератор для улучшенной генерации...
```

## 🎯 Как это работает

### Этап 1: Планирование (Planning Chain)

- Модель создает детальный план структуры квеста
- Определяет все scene_id заранее
- Проверяет отсутствие циклов
- Убеждается в наличии quest_end

### Этап 2: Генерация (Generation Chain)

- Создает полный квест по составленному плану
- Использует только сцены из плана
- Гарантирует корректные ссылки между сценами

### Этап 3: Валидация (Validation Chain)

- Проверяет финальный квест на корректность
- Находит и сообщает о проблемах
- Предлагает улучшения

## 🔄 Fallback механизм

Если LangChain недоступен, система автоматически переключается на базовый Mistral AI генератор.

## 🐛 Устранение проблем

### "ChatMistralAI недоступен"

Попробуйте установить:

```bash
poetry add langchain-mistralai
```

### "LangChain not available"

Установите базовые компоненты:

```bash
poetry add langchain-core pydantic
```

### Предупреждения в IDE

Предупреждения об импортах в IDE не критичны - код работает с graceful fallback.
