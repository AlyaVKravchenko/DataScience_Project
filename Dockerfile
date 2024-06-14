FROM python:3.9-slim

# Встановлення необхідних бібліотек
RUN pip install --upgrade pip
RUN pip install tensorflow fastapi uvicorn

# Створення робочої директорії
WORKDIR /app

# Копіювання всіх файлів до робочої директорії
COPY . /app

# Вказівка команди для запуску додатку
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]