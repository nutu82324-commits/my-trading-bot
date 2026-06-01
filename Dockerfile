FROM python:3.9-slim
WORKDIR /app
RUN pip install aiogram==3.1.1
COPY . .
CMD ["python", "bot.py"]
