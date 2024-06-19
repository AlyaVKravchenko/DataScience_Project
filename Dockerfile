FROM python:3.9-slim

WORKDIR /app

# Копіюємо файл з залежностями
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо всі файли в робочу директорію
COPY . .

# Відкриваємо порт 8000 для доступу до сервера
EXPOSE 8000

# Команда для запуску Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]