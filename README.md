# Restful Booker API Autotests


Фреймворк автотестов для REST API [Restful Booker](https://restful-booker.herokuapp.com/).
Построен на `pytest`, использует `requests` для HTTP-запросов, `Pydantic` для валидации
ответов и `Allure` для отчётов. Тестируемый сервис (исходники лежат в папке `restful-booker`)
собирается и поднимается вместе с тестами одной командой через Docker Compose; CI настроен на GitHub Actions.

---

## Стек

| Компонент | Назначение |
|---|---|
| Python 3.12 | Язык |
| pytest | Тест-раннер, фикстуры, параметризация, маркеры |
| requests | HTTP-клиент |
| Pydantic v2 | Валидация запросов и ответов, модели данных |
| Faker | Генерация тестовых данных |
| Allure | Отчёты с шагами, вложениями и разбивкой по severity |
| Docker / Docker Compose | Изолированный запуск API (из исходников) и тестов |
| GitHub Actions | CI: прогон тестов и публикация Allure-артефакта |

---

## Что покрыто

**Эндпоинты:**
- `POST /auth` — авторизация, получение токена
- `GET /ping` — health-check
- `GET /booking` — список бронирований, фильтрация по `firstname`, `checkin`, `checkout`
- `GET /booking/{id}` — бронирование по ID
- `POST /booking` — создание
- `PUT /booking/{id}` — полное обновление
- `PATCH /booking/{id}` — частичное обновление
- `DELETE /booking/{id}` — удаление

**Типы проверок:**
- Позитивные сценарии (CRUD, авторизация, фильтрация)
- Негативные сценарии: отсутствие авторизации (403), несуществующий ID (404/405),
  невалидные типы данных, пустое тело, лишние поля, повторное удаление
- Валидация структуры ответа через Pydantic-модели (`Booking`, `BookingCreateResponse`, `AuthResponse`)
- Цепочки запросов: получить токен → создать → обновить → удалить → проверить 404

**Маркеры pytest:** `smoke`, `regression`, `positive`, `negative`, `auth`, `get`, `post`,
`put`, `patch`, `delete`, `cleanup` — можно гонять подмножества, например `pytest -m smoke`.

---

## Структура проекта

```text
.
├── autotests/
│   ├── clients/              # API-клиенты (BookingApi) и ApiManager
│   ├── config/               # Настройки: BASE_URL, креды из .env
│   ├── custom_requester/     # Обёртка над requests: логирование, Allure, проверка статусов
│   ├── models/               # Pydantic-модели запросов и ответов
│   ├── tests/api/            # Тесты по методам: get/post/put/patch/delete
│   ├── utils/                # DataGenerator на Faker
│   ├── conftest.py           # Фикстуры: session, api_manager, auth_token, created_booking
│   ├── pytest.ini            # Маркеры и addopts
│   ├── requirements.txt
│   └── Dockerfile
├── restful-booker/           # Исходный код тестируемого API (Node.js)
├── docker-compose.yaml       # api (сборка из исходников) + tests, healthcheck
├── .github/workflows/ci.yml  # CI: прогон тестов и загрузка Allure-отчёта
├── .env.example              # Шаблон переменных окружения
└── README.md
```

### Быстрый старт
#### Через Docker (рекомендуется)

#### Выполни в терминале:
```bash
git clone https://github.com/specqa/restful-booker-api-autotest.git
cd restful-booker-api-autotest
```
### Создай файл .env (можно скопировать из .env.example)
```
cp .env.example .env
docker compose up --build
```
Что происходит:
```
    Собирается Docker-образ для API из папки restful-booker.
    Поднимается контейнер api на http://localhost:3001.
    Docker ждёт healthcheck (GET /ping), чтобы тесты не стартовали раньше времени.
    Запускается контейнер tests, прогоняет pytest, результаты складывает в ./allure-results.
```
### Сгенерировать и открыть отчёт:
```bash
allure serve allure-results
```

### Локально (без Docker для тестов)

#### Поднять только API:
```bash
docker compose up -d api
```
#### Создать окружение и установить зависимости:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r autotests/requirements.txt
```

#### Запустить тесты:
```bash
cd autotests
pytest -v --alluredir=../allure-results
```
### Переменные окружения

#### Скопируй .env.example в .env и заполни env:
```
BASE_URL=http://localhost:3001
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password123
```
```
BASE_URL по умолчанию — http://localhost:3001. Внутри Docker Compose тесты
получают BASE_URL=http://api:3001 автоматически (имя сервиса в сети Compose).
```
### CI
```
На каждый push и pull_request в main GitHub Actions:
    Создает файл .env с тестовыми кредами.
    Собирает образы и поднимает api + tests через docker compose.
    Прогоняет все тесты; пайплайн падает, если падают тесты.
    Генерирует Allure-отчёт (даже при падении тестов) и загружает его как артефакт allure-report (хранится 14 дней).
```
Запустить вручную можно через вкладку Actions → API Autotests → Run workflow.