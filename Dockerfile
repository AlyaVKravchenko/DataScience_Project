# Використовуємо базовий образ Python 3.9
FROM python:3.9-slim

# Встановлюємо необхідні системні залежності
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо Poetry
RUN pip install poetry

# Створюємо робочу директорію
WORKDIR /app

# Копіюємо файли pyproject.toml та poetry.lock у робочу директорію
COPY pyproject.toml poetry.lock ./

# Встановлюємо залежності через Poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Копіюємо решту коду проекту в контейнер
COPY . .

# Виставляємо порт, який буде використовуватися додатком
EXPOSE 8000

# Команда за замовчуванням для запуску контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]