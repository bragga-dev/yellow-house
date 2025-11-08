



# # Dockerfile
# FROM python:3.12-alpine

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# WORKDIR /code

# RUN apk add --no-cache bash git

# COPY requirements.txt .
# RUN pip install --upgrade pip && pip install -r requirements.txt

# COPY . .


# CMD ["gunicorn", "casa_amarela.wsgi:application", "--bind", "0.0.0.0:8000"]


FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Instala dependências do sistema
RUN apk add --no-cache bash git build-base libpq-dev

# Instala dependências do projeto
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Executa collectstatic apenas se estiver em produção
ARG DJANGO_ENV=dev
ENV DJANGO_ENV=${DJANGO_ENV}

# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["gunicorn", "casa_amarela.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]

# docker compose -f docker-compose.prod.yml up -d --build
