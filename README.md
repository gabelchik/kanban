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

## Ключевые возможности
- **Пользователи** – регистрация и аутентификация по email через JWT (access + refresh токены).
- **Рабочие пространства (Workspaces)** – создание, управление участниками с ролями `admin` и `member`. Приглашения по email с асинхронной отправкой писем (Celery).
- **Проекты** – CRUD внутри workspace, отдельные роли для участников проекта.
- **Kanban доски и задачи** – доски в проектах, задачи со статусами, приоритетами и исполнителями. Сортировка, обновление, удаление.
- **Real‑time уведомления** – WebSocket (Django Channels) мгновенно оповещает всех участников рабочего пространства о новых досках, задачах и изменениях.
- **Фоновые задачи** – Celery обрабатывает отправку приглашений, не блокируя HTTP‑ответы.
- **API‑документация** – интерактивный Swagger UI с группировкой и описанием всех эндпоинтов.

## Быстрый старт
1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/gabelchik/kanban-saas.git
   cd kanban-saas
   ```

2. **Запустите сервисы:**
   ```bash
   docker compose up -d --build
   ```

3. **Откройте в браузере:**
   - API: `http://localhost:8000/api/v1/`
   - Swagger UI: `http://localhost:8000/api/docs/`

## Документация API
Полное описание всех методов доступно в Swagger UI после запуска.

## Структура проекта
- `config/` – настройки Django, Celery, ASGI, WSGI
- `accounts/` – кастомная модель User, регистрация, JWT
- `workspaces/` – рабочие пространства, участники, приглашения
- `projects/` – проекты, доски, задачи
- `notifications/` – WebSocket consumer, middleware, утилиты для real‑time
- `docker-compose.yml` – сервисы: backend, worker, postgres, redis
- `Dockerfile` – сборка образа backend/worker

## Планы по развитию
- Загрузка файлов к задачам (MinIO / S3)
- Автотесты (pytest) и CI/CD (GitHub Actions)
- Production‑сборка (Gunicorn + Nginx)
