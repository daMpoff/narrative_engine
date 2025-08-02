# Настройка Mistral AI для генерации квестов

## 1. Получение API ключа Mistral AI

1. Зайдите на [Mistral AI Platform](https://console.mistral.ai/)
2. Создайте аккаунт или войдите в существующий
3. Перейдите в раздел "API Keys"
4. Создайте новый API ключ
5. Скопируйте ключ

## 2. Настройка переменных окружения

Создайте файл `.env` в папке `api/` со следующим содержимым:

```env
# Mistral AI API Configuration
MISTRAL_API_KEY=your_mistral_api_key_here

# Django Settings
DEBUG=True
SECRET_KEY=your-django-secret-key-here

# Optional: Model configuration
MISTRAL_MODEL=mistral-large-latest
```

## 3. Установка зависимостей

```bash
cd api
poetry install
```

## 4. Проверка настройки

Запустите сервер Django:

```bash
cd api
python manage.py runserver
```

В логах вы должны увидеть:

- "Mistral AI настроен: mistral-large-latest" (если API ключ правильный)
- "Mistral API ключ не найден" (если ключ не настроен)

## 5. Доступные модели Mistral

- `mistral-tiny` - быстрая модель для простых задач
- `mistral-small` - сбалансированная модель
- `mistral-medium` - мощная модель для сложных задач
- `mistral-large` - самая мощная модель (рекомендуется)

## 6. Тестирование

Отправьте POST запрос на `http://127.0.0.1:8000/api/generate/` с данными:

```json
{
  "genre": "киберпанк",
  "hero": "хакер-одиночка",
  "goal": "взломать систему безопасности"
}
```

## Альтернативные LLM

Если хотите использовать другие LLM, раскомментируйте соответствующие строки в `.env`:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
```

## Безопасность

⚠️ **Важно:**

- Никогда не коммитьте `.env` файл в git
- Добавьте `.env` в `.gitignore`
- Используйте разные API ключи для разработки и продакшена

## Устранение неполадок

### Ошибка "Mistral API ключ не найден"

- Проверьте, что файл `.env` создан в правильной папке
- Убедитесь, что ключ скопирован правильно
- Проверьте, что нет лишних пробелов в ключе

### Ошибка "Invalid API key"

- Проверьте правильность API ключа
- Убедитесь, что у вас есть доступ к Mistral AI API
- Проверьте баланс аккаунта Mistral AI

### Ошибка "Rate limit exceeded"

- Подождите немного и попробуйте снова
- Рассмотрите возможность перехода на платный план Mistral AI

### Ошибка "Model not found"

- Проверьте правильность названия модели в `MISTRAL_MODEL`
- Убедитесь, что модель доступна в вашем аккаунте
