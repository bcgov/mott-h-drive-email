FROM python:3.13-slim

# Set custom cache and virtualenv paths that are writable
ENV POETRY_CACHE_DIR=/app/.cache
ENV POETRY_VIRTUALENVS_PATH=/app/.virtualenvs

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/evan-harley/h-drive-email.git .
COPY . /app/

RUN pip3 install poetry==1.8.5

RUN poetry install --no-interaction --no-ansi

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["poetry", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]