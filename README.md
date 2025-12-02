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
MODEL_PROVIDER=openai  # or "gigachat"
```

**For OpenAI** - create `.env.openai_model`:
```bash
OPENAI_API_KEY=sk-your-key
MODEL=gpt-4o-mini
TEMPERATURE=0.5
MAX_TOKENS=
```

**For GigaChat** - create `.env.gigachat_model`:
```bash
GIGACHAT_API_KEY=your-key
GIGACHAT_CREDENTIALS=path-to-credentials
MODEL=GigaChat-Pro
TEMPERATURE=0.5
MAX_TOKENS=
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
