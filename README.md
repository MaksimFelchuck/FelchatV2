# FelchatV2 🚀

**Современный чат-сервис с real-time сообщениями, аутентификацией и блокировкой пользователей**

## 📖 О проекте

FelchatV2 - это мой pet-проект, современный веб-чат на FastAPI с WebSocket поддержкой. Проект демонстрирует использование современных технологий для создания полнофункционального чат-приложения с возможностью регистрации, аутентификации, приватных сообщений и управления пользователями.

### 🎯 Основные возможности

- **👤 Аутентификация пользователей** - регистрация, вход, выход
- **💬 Real-time чат** - мгновенная отправка сообщений через WebSocket
- **🔒 Приватные сообщения** - общение только между двумя пользователями
- **🚫 Блокировка пользователей** - возможность блокировать/разблокировать других пользователей
- **📱 Адаптивный интерфейс** - работает на всех устройствах
- **📊 API документация** - автоматически генерируемая Swagger документация
- **🛡️ Безопасность** - хэширование паролей, secure cookies, CORS защита

### 🏗️ Архитектура

Проект построен с использованием **Clean Architecture** принципов:

- **Domain Layer** - бизнес-логика и модели
- **Repository Pattern** - абстракция доступа к данным
- **Dependency Injection** - управление зависимостями
- **Service Layer** - координация между слоями
- **API Layer** - HTTP и WebSocket endpoints

## 🛠 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **WebSocket** - real-time коммуникация
- **Pydantic** - валидация данных и сериализация

### База данных
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и хранение сообщений чата

### Frontend
- **HTML5/CSS3** - структура и стили
- **JavaScript (Vanilla)** - интерактивность
- **WebSocket API** - real-time обновления

### Инфраструктура
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация сервисов
- **Railway** - платформа для деплоя

### Тестирование
- **pytest** - unit и integration тесты
- **TestClient** - тестирование API endpoints

## 🚀 Быстрый старт

### Локальный деплой

#### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/FelchatV2.git
cd FelchatV2
```

#### 2. Настройка окружения
```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### 3. Настройка переменных окружения
```bash
# Копирование примера
cp env.example .env

# Редактирование .env файла
# Убедитесь, что настройки соответствуют вашей среде
```

#### 4. Запуск баз данных
```bash
# Запуск PostgreSQL и Redis через Docker
docker-compose up -d

# Проверка статуса
docker-compose ps
```

#### 5. Миграции базы данных
```bash
# Применение миграций
alembic upgrade head

# Проверка статуса
alembic current
```

#### 6. Запуск приложения
```bash
# Запуск в режиме разработки
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 7. Проверка работы
- **Приложение**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **ReDoc документация**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/ping


📖 **Подробная инструкция по деплою**: [DEPLOY.md](DEPLOY.md)

## 📚 API Endpoints

### Аутентификация
- `POST /api/v1/users/register` - регистрация пользователя
- `POST /api/v1/users/login` - вход в систему
- `POST /api/v1/users/logout` - выход из системы
- `GET /api/v1/users/me` - информация о текущем пользователе

### Пользователи
- `GET /api/v1/users/` - список всех пользователей
- `POST /api/v1/users/block/{user_id}` - заблокировать пользователя
- `DELETE /api/v1/users/block/{user_id}` - разблокировать пользователя

### Web интерфейс
- `GET /users/register` - страница регистрации
- `GET /users/login` - страница входа
- `GET /users/` - список пользователей
- `GET /chat?user={user_id}` - чат с пользователем
- `GET /users/profile` - профиль пользователя

### WebSocket
- `WS /ws/chat?user_id={id}&other_user={id}` - WebSocket для чата

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src

# Запуск конкретного теста
pytest tests/api/test_users_api.py

# Запуск с подробным выводом
pytest -v
```

## 📁 Структура проекта

```
FelchatV2/
├── src/
│   ├── chat/                    # WebSocket чат
│   │   ├── repositories/        # Репозитории чата
│   │   │   ├── abs/            # Абстрактные классы
│   │   │   ├── db/             # Реализация с Redis
│   │   │   └── inmem/          # In-memory для тестов
│   │   └── ws_service.py       # WebSocket сервис
│   ├── users/                   # Пользователи и аутентификация
│   │   ├── api.py              # API endpoints
│   │   ├── models.py           # SQLAlchemy модели
│   │   ├── repositories/       # Репозитории пользователей
│   │   ├── schemas.py          # Pydantic схемы
│   │   └── services.py         # Бизнес-логика
│   ├── web/                    # Web интерфейс
│   │   ├── chat.py             # WebSocket и чат страницы
│   │   └── users.py            # Страницы пользователей
│   ├── di/                     # Dependency injection
│   │   └── container.py        # DI контейнер
│   ├── db/                     # База данных
│   │   ├── base.py             # Базовые модели
│   │   └── session.py          # Сессии БД
│   ├── config.py               # Конфигурация
│   ├── dependencies.py         # FastAPI зависимости
│   ├── logger.py               # Логирование
│   └── main.py                 # Точка входа
├── tests/                      # Тесты
│   └── api/                    # API тесты
├── alembic/                    # Миграции БД
├── static/                     # Статические файлы
├── templates/                  # HTML шаблоны
├── docker-compose.yml          # Docker Compose
├── Dockerfile                  # Docker образ
├── requirements.txt            # Python зависимости
└── README.md                   # Документация
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL PostgreSQL | `postgresql+psycopg2://felchat:felchat@db:5432/felchat` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `ENV` | Окружение | `prod` |
| `PORT` | Порт приложения | `8000` |
| `SESSION_COOKIE_SECURE` | Secure cookies | `true` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

### Настройки чата

| Настройка | Описание | По умолчанию |
|-----------|----------|--------------|
| `MAX_MESSAGE_LENGTH` | Максимальная длина сообщения | `1000` |
| `CHAT_HISTORY_LIMIT` | Лимит истории сообщений | `50` |
| `MESSAGE_RETENTION_MINUTES` | Время хранения сообщений | `30` |

## 🚀 Производительность

- **WebSocket соединения** - поддержка множественных сессий
- **Redis кэширование** - быстрый доступ к сообщениям
- **PostgreSQL** - надежное хранение данных пользователей
- **Асинхронная обработка** - FastAPI для высокой производительности

## 🔒 Безопасность

- **Хэширование паролей** - bcrypt для безопасного хранения
- **Secure cookies** - защищенные сессии
- **CORS защита** - настройка cross-origin запросов
- **Валидация данных** - Pydantic для проверки входных данных
- **SQL injection защита** - SQLAlchemy ORM

## 🤝 Вклад в проект

Этот проект создан для изучения современных технологий и демонстрации навыков разработки. Если у вас есть предложения по улучшению или вы нашли баги - создавайте issues!

## 📄 Лицензия

Этот проект является pet-проектом и создан в образовательных целях.

---

**Автор**: [Ваше имя]  
**Версия**: 2.0  
**Дата создания**: 2024