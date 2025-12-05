# LAB 1
TODO

# LAB 2

| Требование | Статус | Комментарий |
|-----------|--------|-------------|
| минимум **1 init + 2 app** сервиса | ✅ | PostgreSQL (init.sql) + App |
| автоматическая **сборка образа из Dockerfile** и присвоение имени | ✅ | в docker-compose, приложение собирается из `src/services/router/Dockerfile` |
| **жёсткое именование контейнеров** | ✅ | `beauty_booking_postgres`, `beauty_booking_app`|
| минимум один сервис с **depends_on** | ✅ | `beauty_booking_app` зависит от `beauty_booking_postgres` |
| минимум один сервис с **volume** | ✅ | `beauty_booking_postgres` содержит volume: `postgres_data:/var/lib/postgresql/data` |
| минимум один сервис с **прокидыванием порта наружу** | ✅ | `beauty_booking_postgres` прокидывает порт 5432, `beauty_booking_postgres` прокидывает порт 8000 |
| минимум один сервис с **command** и/или **entrypoint** | ✅ | `beauty_booking_app` содержит команду запуска приложения на `uvicorn` |
| добавить **healthcheck** | ✅ | `beauty_booking_postgres` делает `["CMD-SHELL", "pg_isready -U $$POSTGRES_USER"]` |
| **env-файл .env**, а не переменные в compose | ✅ | переменные разбросаны по разным env файлам: `.env`, `.env.openai_model`, `.env.postgresql` |
| явно указана **одна общая network** | ✅ | `beauty_booking_network` |


### Описание Compose файла

Docker Compose файл определяет три сервиса для системы бронирования:

**postgres** — сервис базы данных PostgreSQL 16 (Alpine):
- Использует именованный volume `postgres_data` для персистентности данных
- Автоматически выполняет инициализацию схемы из `init.sql` при первом запуске
- Имеет healthcheck, проверяющий готовность БД через `pg_isready`
- Прокидывает порт 5432 наружу для доступа из хоста

**init** — сервис инициализации (одноразовый):
- Собирается из `src/services/init/Dockerfile`
- Запускается после того, как PostgreSQL станет здоровым
- Выполняется один раз и завершается (`restart: "no"`)
- Используется для дополнительной настройки БД после создания схемы

**app** — основное приложение:
- Собирается из `src/services/router/Dockerfile`
- Запускает FastAPI приложение через uvicorn
- Зависит от `postgres` (должен быть здоровым) и `init` (должен завершиться успешно)
- Автоматически перезапускается при сбоях (`restart: unless-stopped`)
- Прокидывает порт приложения наружу

Все сервисы используют общую bridge-сеть `beauty_booking_network` для взаимодействия. Конфигурация загружается из отдельных env-файлов: `.env`, `.env.postgresql`, `.env.openai_model`.


### Ответы на вопросы

- Можно ли ограничивать ресурсы (например, память или CPU) для сервисов в docker-compose.yml? Если нет, то почему, если да, то как
    * Для **Compose v2+** и Docker (не Swarm) ограничения задаются через `deploy.resources`, но они **работают только в Docker Swarm**
    * Для обычного Docker Compose используются параметры `mem_limit`, `cpus` и др., но они поддерживаются **только в формате версии 2.x**

- Как можно запустить только определенный сервис из docker-compose.yml, не запуская остальные?
    Использовать имя сервиса в команде:

    ```bash
    docker compose up service_name
    ```