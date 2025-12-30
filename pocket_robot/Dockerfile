FROM python:3.12-slim

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# copy app
COPY . /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "pocket_robot.webapi.app:asgi_app", "--host", "0.0.0.0", "--port", "8000"]
