FROM python:3.6-alpine

RUN apk --no-cache add \
    python3 \
    git \
    libpq \
    wget \
    ca-certificates \
    python3-dev \
    postgresql-dev \
    build-base \
    libxml2-dev \
    libxslt-dev \
    libstdc++ \
    bash \
    curl
RUN update-ca-certificates

WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

# ENV OS_API_CACHE=redis
# ENV OS_STATSD_HOST=10.7.255.254
# ENV CELERY_CONFIG=amqp://guest:guest@mq:5672//
# ENV CELERY_BACKEND_CONFIG=amqp://guest:guest@mq:5672//

COPY docker/startup.sh /startup.sh
COPY docker/docker-entrypoint.sh /entrypoint.sh

EXPOSE 8000

CMD ["/startup.sh"]
ENTRYPOINT ["/entrypoint.sh"]
