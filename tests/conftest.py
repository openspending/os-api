import os
from elasticsearch import Elasticsearch
import pytest

from os_api.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
    return app


@pytest.fixture(scope='module')
def elasticsearch():
    host = os.environ.get('OS_ELASTICSEARCH_ADDRESS', 'localhost:9200')
    es = Elasticsearch(hosts=[host])

    def _delete_indices():
        indices = [
            'packages',
        ]

        for index in indices:
            es.indices.delete(index=index, ignore=[400, 404])

    _delete_indices()
    yield es
    _delete_indices()
