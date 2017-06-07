FROM python:3.6-alpine

ADD . /app/
WORKDIR /app

RUN apk add --update libpq python3-dev postgresql-dev build-base libxml2-dev libxslt-dev libstdc++
RUN pip install -r requirements.txt

RUN pip install -U https://github.com/openspending/babbage.fiscal-data-package/archive/master.zip
RUN pip install -U https://github.com/openspending/babbage/archive/feature/optimize-member-queries.zip#egg=babbage==0.2.0
RUN rm -rf /var/cache/apk/*

ENV OS_API_CACHE=redis
ENV OS_STATSD_HOST=10.7.255.254
ENV CELERY_CONFIG=amqp://guest:guest@mq:5672//
ENV CELERY_BACKEND_CONFIG=amqp://guest:guest@mq:5672//

ADD docker/startup.sh /startup.sh

EXPOSE 8000

CMD  /startup.sh
