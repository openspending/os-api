# OpenSpending API

[![Gitter](https://img.shields.io/gitter/room/openspending/chat.svg)](https://gitter.im/openspending/chat)
[![Build Status](https://travis-ci.org/openspending/os-api.svg?branch=master)](https://travis-ci.org/openspending/os-api)
[![Coverage Status](https://coveralls.io/repos/openspending/os-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/openspending/os-api?branch=master)
[![Issues](https://img.shields.io/badge/issue-tracker-orange.svg)](https://github.com/openspending/openspending/issues)
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](http://docs.openspending.org/)

An API to explore the OpenSpending database.

- An analytical API powered by [Babbage](https://github.com/openspending/babbage)
- A search API to access package-level meta data
- A search API to access fiscal line-level data

The API is written in Python 3 and uses [Flask](http://flask.pocoo.org/) blueprints.

## Quick start

Clone the repo, install dependencies from pypi, and run the server.

For development, create a `.env` file and add environmental variables:

```ini
# Address for the postgres instance, e.g. postgresql://postgres@db/postgres
OS_API_ENGINE=postgresql://postgres@db/postgres
# Address of elasticsearch server
OS_ELASTICSEARCH_ADDRESS=localhost:9200
# Address of Redis instance
OS_API_CACHE=redis

# Check health of ElasticSearch before starting app (optional)
OS_CHECK_ES_HEALTHY='True'
```

With the backing services available, a development server can be started with:
`python dev_server.py`

## Available Endpoints

- `/api/3/info/<dataset>/package`
  - Returns the Fiscal Data-Pacakge for this dataset
- `/api/3/cubes`:
  - Returns a list of the available datasets in the store
- `/api/3/cubes/<dataset>/model`:
  - Returns the `babbage` model for the dataset. This is the model which is used  when querying the data.
- `/api/3/cubes/<dataset>/facts`:
  - Returns individual entries from the dataset in non-aggregated form.
  - Parameters:
    - `cut` - filters on the data (`field_name:value`, `field_name:value|field_name:value` etc.)
    - `fields` - fields to return
    - `order` - data ordering (e.g. `field_name:desc`)
    - `pagesize` - number of entries in one batch of returned data
    - `page` - page selection
- `/api/3/cubes/<dataset>/members/<dimension>`
  - Returns the distinct set of values for a specific dimension.
  - Parameters: `cut`, `order`, `page` and `pagesize` as above
- `/api/3/cubes/<dataset>/aggregate`
  - Returns an aggregate of the data in the specified dataset.
  - Parameters:
    - `cut`, `order`, `page` and `pagesize` as above
    - `drilldown` - group by these dimensions (e.g. `field_name_1|field_name_2`)
    - `aggregates` - which measures to aggregate (and what function to perform (e.g. `amount.sum`, `count`)

## Testing

You need a few services running, namely Elasticsearch v5.x running on localhost:9200 and PostgreSQL.

Then set a few environment variables (your DB connection string might vary):
```bash
$ export OS_API_ENGINE=postgresql://postgres@/postgres
$ export DPP_DB_ENGINE=postgresql://postgres@/postgres
$ export OS_ELASTICSEARCH_ADDRESS=localhost:9200
$ export ELASTICSEARCH_ADDRESS=localhost:9200
```

Install a few dependencies:
```bash
$ npm install -g os-types
$ sudo apt-get install libleveldb-dev libleveldb1 libpq-dev python3-dev
$ pip3 install tox coveralls 'datapackage-pipelines[speedup]>=2.0.0' 'datapackage-pipelines-fiscal>=1.2.0' psycopg2-binary

# or for MacOS
$ npm install -g os-types
$ brew install leveldb
$ pip3 install tox coveralls 'datapackage-pipelines[speedup]>=2.0.0' 'datapackage-pipelines-fiscal>=1.2.0' psycopg2-binary
```

Fill the local DB with a sample fiscal data:
```
$ cd tests/sample_data && dpp run --verbose --concurrency=8 all
```

Then run:
```bash
$ tox
```
