# 🚀 Деплой на Railway

## Подготовка проекта

1. **Убедитесь, что код закоммичен в GitHub**
2. **Проверьте, что все файлы на месте:**
   - `Dockerfile` - для контейнеризации
   - `railway.json` - конфигурация Railway
   - `requirements.txt` - зависимости Python
   - `alembic.ini` и папка `alembic/` - миграции БД

## Шаги деплоя на Railway

### 1. Создание проекта
1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш репозиторий `FelchatV2`

### 2. Добавление базы данных PostgreSQL
1. В проекте нажмите "New Service"
2. Выберите "Database" → "PostgreSQL"
3. Railway автоматически создаст базу и сгенерирует `DATABASE_URL`

### 3. Добавление Redis
1. В проекте нажмите "New Service"
2. Выберите "Database" → "Redis"
3. Railway автоматически создаст Redis и сгенерирует `REDIS_URL`

### 4. Настройка переменных окружения
В вашем основном сервисе (приложении) добавьте переменные:

```env
# Обязательные
DATABASE_URL=postgresql://... (Railway сгенерирует автоматически)
REDIS_URL=redis://... (Railway сгенерирует автоматически)
ENV=prod
PORT=8000

# Опциональные (настройте по желанию)
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
LOG_LEVEL=INFO
MAX_MESSAGE_LENGTH=1000
CHAT_HISTORY_LIMIT=50
MESSAGE_RETENTION_MINUTES=30
```

### 5. Настройка домена
1. В настройках сервиса перейдите в "Settings"
2. В разделе "Domains" нажмите "Generate Domain"
3. Railway создаст URL вида: `https://your-app-name-production.up.railway.app`
4. Или настройте кастомный домен в разделе "Custom Domains"

### 6. Деплой
1. Railway автоматически запустит деплой при пуше в GitHub
2. Или нажмите "Deploy" вручную
3. Следите за логами в разделе "Deployments"

## Проверка работы

1. **Health check**: `https://your-domain/ping`
2. **Главная страница**: `https://your-domain/`
3. **API документация**: `https://your-domain/docs`

## Мониторинг

- **Логи**: В разделе "Deployments" → выберите деплой → "View Logs"
- **Метрики**: В разделе "Metrics" 
- **Переменные**: В разделе "Variables"

## Troubleshooting

### Проблемы с миграциями
Если миграции не запускаются:
1. Проверьте `DATABASE_URL` в переменных окружения
2. Убедитесь, что PostgreSQL сервис запущен
3. Проверьте логи деплоя

### Проблемы с Redis
Если Redis не подключается:
1. Проверьте `REDIS_URL` в переменных окружения
2. Убедитесь, что Redis сервис запущен
3. Проверьте, что Redis доступен из основного сервиса

### Проблемы с портом
Railway автоматически устанавливает переменную `PORT`, убедитесь что в коде используется:
```python
port = int(os.getenv("PORT", "8000"))
```

## Обновление приложения

Просто запушьте изменения в GitHub - Railway автоматически пересоберёт и перезапустит приложение! 