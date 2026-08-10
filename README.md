# Kanban API

Серверная часть многопользовательской Kanban системы с ролевой моделью, real‑time уведомлениями и фоновыми задачами.  
Проект создан для демонстрации навыков проектирования и разработки сложных веб-приложений.

## Стек технологий
- **Python 3.14**, **Django 6.0**, **Django REST Framework 3.17**
- **PostgreSQL 17**, **Redis 7**
- **Celery** + **Redis**
- **Django Channels** + **Daphne**
- **Docker Compose**
- **JWT аутентификация**
- **Swagger UI**
- **Poetry**
- **GitHub Actions (CI/CD)**
- **pytest**, **factory_boy**
- **Gunicorn + Uvicorn** (production)

## Основные возможности

### Управление пользователями
- Регистрация и аутентификация по email с JWT‑токенами (access + refresh).
- Кастомная модель пользователя (email как уникальный идентификатор).

### Рабочие пространства (Workspaces)
- Создание рабочих пространств, назначение владельца и участников.
- Роли `admin` и `member` с разграничением прав.
- Приглашения по email с асинхронной отправкой писем через Celery.
- Автоматическое удаление дублирующихся приглашений при активации.

### Проекты
- CRUD внутри рабочего пространства с собственными ролями участников.
- Права на создание/редактирование/удаление: только администраторы проекта или workspace.

### Kanban-доски и задачи
- Создание досок в проектах.
- Задачи с полями: статус, приоритет, исполнитель, порядок сортировки.
- Обновление статусов и назначение исполнителей.
- Real‑time уведомления через WebSocket о создании досок, задач и изменении их статусов.

### Фоновые задачи
- Celery обрабатывает отправку приглашений, не блокируя HTTP‑ответы.

### API-документация
- Интерактивный Swagger UI с группировкой эндпоинтов по тегам и подробными описаниями.

### Тестирование и CI/CD
- Юнит-тесты с pytest + factory_boy.
- Автоматический запуск тестов в GitHub Actions при каждом пуше и Pull Request.

## Безопасность
- **Аутентификация**: JWT‑токены (access + refresh), access‑токен имеет ограниченное время жизни.
- **Разграничение доступа**: кастомные permissions (`IsOwnerOrAdmin`, `IsWorkspaceMember`, `IsProjectAdmin`, `IsProjectMember`), проверка ролей на уровне рабочих пространств, проектов и задач.
- **Изоляция данных**: каждый пользователь видит только те сущности, к которым имеет доступ (свои workspace, проекты, доски).
- **Защита от утечки секретов**: переменные окружения хранятся в `.env` (для демонстрации включён в репозиторий, в реальном проекте исключается из Git). В production-сборке секреты передаются через переменные окружения без попадания в образ.
- **Безопасность production‑окружения**: отключён режим DEBUG, настроен обратный прокси Nginx, статика отдаётся напрямую, ограничены хосты через `ALLOWED_HOSTS`.

## Структура проекта
- `config/` – настройки Django, Celery, ASGI
- `accounts/` – кастомная модель User, регистрация, JWT
- `workspaces/` – рабочие пространства, участники, приглашения
- `projects/` – проекты, доски, задачи
- `notifications/` – WebSocket consumer, middleware, утилиты для real‑time
- `tests/` – фабрики factory_boy и общие тестовые утилиты
- `.github/workflows/tests.yml` – CI/CD
- `docker-compose.yml` – dev‑окружение (Daphne)
- `docker-compose.prod.yml` – production‑окружение (Gunicorn + Nginx)
- `nginx/nginx.conf` – конфигурация Nginx для production
- `Dockerfile` – единый образ для backend и worker
- `entrypoint.sh` – скрипт для сборки статики
- `Makefile` – удобные команды (test, dev-up, prod-up)

## Быстрый старт
**Клонируйте репозиторий:**
```bash
git clone https://github.com/gabelchik/kanban-saas.git
cd kanban-saas
```

### Разработка

**Запустите сервисы:**
```bash
make dev-up
```

**Выполните миграции:**
```bash
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

**Откройте в браузере:**
- API: `http://localhost:8000/api/v1/`
- Swagger UI: `http://localhost:8000/api/docs/`

### Production‑сборка
**Запустите сервисы:**
```bash
make prod-up
```

**Выполните миграции:**
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

**После запуска приложение доступно через Nginx на порту 80:**
- API: http://localhost/api/v1/
- Swagger UI: http://localhost/api/docs/

Для использования аргументов используйте ARGS=

## Документация API
Полное описание всех методов доступно в Swagger UI после запуска.

## Запуск тестов
Для запуска тестов через Docker-контейнер используйте Makefile:
```bash
make test
```
Для использования аргументов используйте ARGS=""

**При каждом пуше в основную ветку и при создании Pull Request тесты автоматически выполняются в GitHub Actions.**
