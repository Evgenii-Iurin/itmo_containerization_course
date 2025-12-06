# Beaury Booking Assistant

A bot that automates manicure appointment booking by letting clients choose services and available time slots while the system confirms and stores reservations automatically.

### Requirements

| Component           | Requirement                                                  |
| ------------------- | ------------------------------------------------------------ |
| Operating System    | Linux (Ubuntu recommended) <br> ⚠️ Windows is **not tested** |
| Python Version      | 3.11                                                         |
| Environment Manager | Conda                                                        |
| Package Manager     | Poetry                                                       |

---

### How to use

Приложение подключено к базе, которая содержит даты для записи на процедуры. Агент может пользоваться следующими тулами:
 - Достать свободные слоты по дате и типу процедуры
 - Записать клиента на процедуру

Note: на данный момент, front-end не подключен

#### Пример №1

Запрос:

```
curl -X POST http://localhost:8000/chat \ 
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "query": "Какие есть окошки на завтра?"}'
```

Ответ:

```
{
   "answer":"К сожалению, на завтра, 7 декабря 2025 года, нет доступных окошек для записи на маникюр. Могу помочь вам с выбором другой даты или типа маникюра?",
   "query":"Какие есть окошки на завтра?"
}
```

**Пояснение**: Агент посмотрел в базе доступное время на процедуру на 7 декабря. В базе не оказалось свободных окон.

#### Пример №2

Запрос:

```
 curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "query": "Хочу записаться на 10 декабря, какие есть свободные окошки?"}'
```

Ответ:

```
{
   "answer":"На 10 декабря у нас есть следующие свободные окошки: 10:00, 12:00, 14:00, 16:00 и 18:00. Какое время вам подходит? И какой тип маникюра вы предпочитаете: классический, японский, гель или наращивание?",
   "query":"Хочу записаться на 10 декабря, какие есть свободные окошки?"
}
```

**Пояснение**: Агент показал доступные слоты на 10 декабря, но также **уточнил тип маникюра**.

#### Пример №3

Запрос:

```
 curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "query": "Хочу записаться на японский маникюр, подскажите ближайшую дату?"}'
```

Ответ:

```
{
   "answer":"У нас есть несколько свободных дат для японского маникюра. Ближайшие доступные даты: 8 декабря 2025 года в 10:00, 12:00, 14:00, 16:00 и 18:00, а также 9 декабря 2025 года в 10:00, 12:00, 14:00, 16:00 и 18:00. Какое время вам подходит?",
   "query":"Хочу записаться на японский маникюр, подскажите ближайшую дату?"
}  
```

**Пояснение**: Система нашла ближайшие даты на **определенный тип** процедуры.

#### Пример №4

Запрос:

```
 curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "query": "Запишите меня на 9 декабря на  10:00"}'
```

Ответ:

```
{
   "answer":"К сожалению, чтобы завершить бронирование, мне нужно знать, какой тип маникюра вы хотите выбрать. У нас есть следующие варианты: классический, японский, гель или наращивание. Пожалуйста, сообщите мне ваш выбор, и я продолжу с бронированием на 9 декабря в 10:00!",
   "query":"Запишите меня на 9 декабря на  10:00"
}
```

**Пояснение**: При попытке записаться, система **идентифицировала, что не хватает типа процедуры**.

#### Пример №5

Запрос:

```
 curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "query": "Запишите меня на 9 декабря на 10:00 на японский маникюр"}'
```

Ответ:

```
{
   "answer":"Ваше бронирование на японский маникюр на 9 декабря в 10:00 подтверждено! Ваш уникальный идентификационный номер бронирования: BK020251206003430. Если у вас есть дополнительные вопросы или вы хотите внести изменения, дайте знать!",
   "query":"Запишите меня на 9 декабря на  10:00 на японский маникюр"
}
```

**Пояснение**: Система **проверила**, что **дата доступна** для данного типа маникюра и **автоматически записала** на процедуру.




### Repository Setup

1. **Install `conda`**

   ⚠️ The following instructions are for **Ubuntu**. For Windows, please refer to [the official guide](https://www.anaconda.com/docs/getting-started/miniconda/install#windows-command-prompt).

   ```bash
   mkdir -p ~/miniconda3
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
   bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
   rm ~/miniconda3/miniconda.sh
   ```

   ```bash
   source ~/miniconda3/bin/activate
   ```

   ```bash
   conda init --all
   ```

2. **Create a new environment**

   ```bash
   conda create --name beauty-booking-assistant python=3.11
   ```

3. **Activate the environment**

   ```bash
   conda activate beauty-booking-assistant
   ```

4. **Install `poetry`**

   ```bash
   pip install poetry
   ```

   ✅ Make sure that Python and Poetry are installed **inside your environment**:

   ```bash
   which poetry   # should return {your_path}/envs/beauty-booking-assistant/bin/poetry
   ```

   ```bash
   which python   # should return {your_path}/envs/beauty-booking-assistant/bin/python
   ```

5. **Install all project requirements**

   ```bash
   poetry install
   ```

   **Optional: Install development dependencies**

   For document processing and development tools, you can install additional dependencies:

   ```bash
   # Install document processing tools (includes docling)
   poetry install --extras document-processing
   
   # Or install all extras
   poetry install --all-extras
   ```

6. **Install pre-commit**

    ```
    poetry run pre-commit install
    ```


### Configuration

**Main `.env` file:**
```bash
MODEL_PROVIDER=openai # or "gigachat"
POSTGRES_PORT=5432
LLM_MODEL_TIMEOUT=10
```

**For OpenAI** - create `.env.openai_model`:
```bash
OPENAI_API_KEY=sk-your-key
MODEL=gpt-4o-mini
TEMPERATURE=0.5
```

**For GigaChat** - create `.env.gigachat_model`:
```bash
GIGACHAT_API_KEY=your-key
GIGACHAT_CREDENTIALS=path-to-credentials
MODEL=GigaChat-Pro
TEMPERATURE=0.5
```

**For PostgreSQL** - create `.env.postgresql`:
```bash
POSTGRES_USER=booking_user 
POSTGRES_PASSWORD=booking_password 
POSTGRES_DB=beauty_booking
POSTGRES_HOST=postgres
```


### Database Setup

**Start PostgreSQL with Docker Compose:**
```bash
docker-compose up -d postgres
```

This will:
- Start PostgreSQL container
- Create the database schema automatically from `init.sql`
- Seed initial available slots for the next 2 weeks

**Verify database is running:**
```bash
docker-compose ps
```

## Run application

### Prerequisites

Create the configuration files as described above.

### [First approach] Run from terminal

```
uvicorn src.services.router.app.main:app --reload
```

**Note**: The Docker image only includes production dependencies.

#### Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Main Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health


## Run Docker Compose

```
docker-compose build --no-cache
docker-compose up -d
```