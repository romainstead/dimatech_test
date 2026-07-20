# Тестовое задание

## Тестовые учётные записи

| Роль          | Login             | Password    |
|---------------|-------------------|-------------|
| Пользователь  | user@test.com     | user12345   |
| Администратор | admin@test.com    | admin12345  |

---

## Вариант 1: Запуск через Docker Compose

1. Скопируйте `.env.example` в `.env` и при необходимости поправьте значения:
   ```bash
   cp .env.example .env
   ```

2. Соберите и запустите контейнеры:
   ```bash
   docker compose up --build
   ```

3. Приложение автоматически:
   - дождётся готовности PostgreSQL (healthcheck),
   - выполнит `alembic upgrade head` (создаст таблицы и seed-данные из п. "Тестовые учётные записи"),
   - запустится на `http://localhost:8000`.

4. Остановка:
   ```bash
   docker compose down
   ```

5. Полная очистка (включая данные БД):
   ```bash
   docker compose down -v
   ```

---

## Вариант 2: Запуск без Docker (локально)

1. Убедитесь, что установлен PostgreSQL 15+ и создана база данных:
   ```sql
   CREATE DATABASE test_task;
   CREATE USER postgres WITH PASSWORD 'postgres';
   ```

2. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/macOS
   .venv\Scripts\activate         # Windows PowerShell

   pip install -r requirements.txt
   ```

3. Скопируйте `.env.example` в `.env` и укажите `DB_HOST=localhost`:
   ```bash
   cp .env.example .env
   ```

4. Примените миграции (создаст таблицы и тестовые учётки):
   ```bash
   alembic upgrade head
   ```

5. Запустите приложение:
   ```bash
   sanic app.main:app --host=0.0.0.0 --port=8000
   ```

6. Приложение доступно на `http://localhost:8000`.

---

## Известные особенности Windows

Если при `docker compose up` возникает ошибка вида:
exec /entrypoint.sh: no such file or directory
это связано с автоконвертацией окончаний строк Git на Windows (CRLF вместо LF). Решение:
```bash
git config core.autocrlf input
git add --renormalize .
docker compose build --no-cache app
```