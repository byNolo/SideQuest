FROM python:3.12-slim
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
# Install build dependencies required by some Python packages (psycopg)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libpq-dev \
	&& rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python","app.py"]
