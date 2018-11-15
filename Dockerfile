FROM python:3.6-alpine

RUN apk add --no-cache \
    libpq \
    python3-dev \
    postgresql-dev \
    libxml2-dev \
    libxslt-dev \
    libstdc++ \
    bash \
    curl

WORKDIR /app

ADD requirements.txt .

RUN apk add --no-cache --virtual .build-deps \
    git \
    build-base \
    ca-certificates \
    && update-ca-certificates \
    && pip install -r requirements.txt \
    && apk del --no-cache .build-deps

COPY docker/entrypoint.sh /entrypoint.sh

ADD . .

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["-t 120", "-w 4", "os_api.app:app", "-b 0.0.0.0:8000"]
