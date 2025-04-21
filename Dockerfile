FROM python:3.12-slim-bullseye AS prod


RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg unzip software-properties-common && \
    curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(. /etc/os-release && echo "$VERSION_CODENAME") main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && curl -sL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==2.1.2
# Configuring poetry
RUN poetry config virtualenvs.create false
RUN poetry config cache-dir /tmp/poetry_cache

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements

COPY . /app/src
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

#build frontend
WORKDIR /app/src/frontend
RUN npm install
RUN npm run build
RUN cp -r /app/src/frontend/dist /app/src/

WORKDIR /app/src

RUN chmod +x /app/src/startup.sh

EXPOSE 8000
CMD ["sh", "startup.sh"]

FROM prod AS dev

RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

# CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]