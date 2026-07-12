FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

RUN mkdir -p /app/custody_data

EXPOSE 5000

CMD ["python", "-c", "from src.api import create_app; create_app().run(host='0.0.0.0', port=5000)"]
