# Felchat API Tests

Этот каталог содержит тесты для всех API эндпоинтов проекта Felchat.

## Структура тестов

```
tests/
├── api/                    # Тесты API эндпоинтов
│   ├── test_users_api.py   # Тесты API пользователей
│   ├── test_chat_api.py    # Тесты API чата
│   └── test_pages_api.py   # Тесты основных страниц
├── conftest.py             # Конфигурация pytest
└── README.md              # Этот файл
```

## Особенности тестов

### 🧪 InMem репозитории
Все тесты используют InMem (in-memory) репозитории вместо реальных баз данных:
- `InMemUserRepository` - для тестирования пользователей
- `InMemChatRepository` - для тестирования чата
- Нет зависимости от PostgreSQL или Redis

### 🎯 Покрытие API
Тесты покрывают все основные эндпоинты:

#### Users API (`/users/*`)
- ✅ Регистрация пользователей
- ✅ Авторизация/выход
- ✅ Получение текущего пользователя
- ✅ Список пользователей
- ✅ Блокировка/разблокировка
- ✅ Статус блокировки

#### Chat API (`/chat/*`)
- ✅ Страница чата
- ✅ История сообщений
- ✅ WebSocket соединения
- ✅ Обработка блокировок

#### Pages API
- ✅ Страницы входа/регистрации
- ✅ Список пользователей
- ✅ Статические файлы
- ✅ Редиректы

## Запуск тестов

### Установка зависимостей
```bash
pip install -r requirements-test.txt
```

### Запуск всех тестов
```bash
python run_tests.py
```

### Запуск через pytest
```bash
# Все API тесты
pytest tests/api/ -v -m api

# Конкретный файл
pytest tests/api/test_users_api.py -v

# С покрытием кода
pytest tests/api/ --cov=src --cov-report=html
```

### Запуск конкретного теста
```bash
python run_tests.py tests/api/test_users_api.py
```

## Маркеры тестов

- `@pytest.mark.api` - API тесты
- `@pytest.mark.asyncio` - Асинхронные тесты

## Фикстуры

### `client`
TestClient с настроенными InMem репозиториями

### `setup_users`
Создает тестовых пользователей в InMem репозитории

### `user_service`, `chat_service`
Сервисы с InMem репозиториями

## Примеры тестов

### Тест регистрации
```python
def test_register_user_success(self, client: TestClient):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }
    
    response = client.post("/users/register", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
```

### Тест с аутентификацией
```python
def test_authenticated_endpoint(self, client: TestClient, setup_users):
    # Сначала логинимся
    login_data = {"username": "testuser1", "password": "password123"}
    login_response = client.post("/users/login", data=login_data)
    assert login_response.status_code == 200
    
    # Теперь тестируем защищенный эндпоинт
    response = client.get("/users/current")
    assert response.status_code == 200
```

## Покрытие кода

Тесты генерируют отчеты о покрытии кода:
- Терминал: `--cov-report=term-missing`
- HTML: `--cov-report=html:htmlcov`

Отчеты сохраняются в папке `htmlcov/`.

## Добавление новых тестов

1. Создайте файл в соответствующей папке `tests/api/`
2. Используйте маркер `@pytest.mark.api`
3. Используйте фикстуры из `conftest.py`
4. Добавьте описательные docstrings

## Отладка тестов

Для отладки используйте:
```bash
pytest tests/api/test_users_api.py -v -s --pdb
```

Флаг `-s` показывает print() вывод, `--pdb` запускает отладчик при ошибке. 