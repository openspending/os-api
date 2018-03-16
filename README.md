# OpenSpending-Next API

[![Gitter](https://img.shields.io/gitter/room/openspending/chat.svg)](https://gitter.im/openspending/chat)
[![Build Status](https://travis-ci.org/openspending/os-api.svg?branch=master)](https://travis-ci.org/openspending/os-api)
[![Coverage Status](https://coveralls.io/repos/openspending/os-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/openspending/os-api?branch=master)
[![Issues](https://img.shields.io/badge/issue-tracker-orange.svg)](https://github.com/openspending/openspending/issues)
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](http://docs.openspending.org/en/latest/developers/api/)

An API to explore the OpenSpending database.

## Quick start

Clone the repo, install dependencies from pypi, and run the server. See the [docs](http://docs.openspending.org/en/latest/developers/api/) for more information.

For development, create a `.env` file and add environmental variables:

```ini
# Address for the postgres instance, e.g. postgresql://postgres@db/postgres
OS_API_ENGINE=postgresql://postgres@db/postgres
# Address of RabbitMQ instance
OS_MQ_ADDRESS=mq
# Address of elasticsearch server
OS_ELASTICSEARCH_ADDRESS=localhost:9200
# Address of RabbitMQ
CELERY_CONFIG=amqp://guest:guest@localhost:5672//
CELERY_BACKEND_CONFIG=amqp://guest:guest@localhost:5672//
# Address of Redis instance
OS_API_CACHE=redis

# Check health of ElasticSearch before starting app (optional)
OS_CHECK_ES_HEALTHY='True'
```

A development server can be started with:
`python dev_server.py`

## Testing

Make sure you have a local ElasticSearch instance running on `localhost:9200`,
and run:

```
$ tox
```
