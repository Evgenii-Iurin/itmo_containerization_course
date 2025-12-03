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
